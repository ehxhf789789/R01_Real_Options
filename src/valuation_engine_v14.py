#!/usr/bin/env python3
"""
BIM Real Options Valuation Engine v14
7개 옵션 + Tier 기반 확률론적 평가
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List
from tier_system import Tier0Input, Tier1Derivation, Tier2Sampler


class ValuationEngine:
    """BIM 실물옵션 평가 엔진 v14"""

    def __init__(self, n_simulations: int = 5000):
        self.n_simulations = n_simulations
        self.fixed_params = self._get_fixed_params()

    @staticmethod
    def _get_fixed_params() -> Dict:
        """고정 파라미터 (모델 구조 파라미터)"""
        return {
            'risk_free_rate': 0.035,
            'discount_rate': 0.09,
            'time_steps': 12,

            # 옵션 행사 파라미터
            'follow_on_exercise_rate': 0.50,
            'capability_growth_rate': 0.10,
            'resource_utilization_premium': 0.06,
            'contract_flexibility_rate': 0.05,
            'switch_mobility_rate': 0.04,
            'stage_checkpoint_value': 0.03,

            # 조정 파라미터
            'interaction_discount': 0.12,
            'risk_premium_rate': 0.15,
            'deferral_multiplier': 0.05,  # 0.30 → 0.05로 감소
        }

    def run_valuation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        실물옵션 평가 실행

        Args:
            df: Tier 0 입력 데이터프레임 (6개 컬럼)

        Returns:
            (결과 데이터프레임, 민감도 분석 결과)
        """
        results = []

        for _, row in df.iterrows():
            # Tier 0 입력 객체 생성
            tier0 = Tier0Input(
                project_id=row['project_id'],
                contract_amount=row['contract_amount'],
                infra_type=row['infra_type'],
                design_phase=row['design_phase'],
                contract_duration=row['contract_duration'],
                procurement_type=row['procurement_type'],
                client_type=row['client_type'],
            )

            # Tier 0 → Tier 1 파생
            tier1 = Tier1Derivation.derive(tier0)

            # Monte Carlo 시뮬레이션
            mc_results = self._monte_carlo_simulation(tier0, tier1)

            # 결과 저장
            results.append({
                'project_id': tier0.project_id,
                'contract_amount': tier0.contract_amount,
                'infra_type': tier0.infra_type,
                'design_phase': tier0.design_phase,
                **mc_results,
            })

        results_df = pd.DataFrame(results)

        # 전체 포트폴리오 민감도 분석
        sensitivity = self._sensitivity_analysis(df)

        return results_df, sensitivity

    def _monte_carlo_simulation(self, tier0: Tier0Input, tier1: Dict) -> Dict:
        """Monte Carlo 시뮬레이션으로 TPV 분포 산출"""

        contract = tier0.contract_amount

        # 시뮬레이션 결과 저장
        npv_samples = []
        tpv_samples = []
        rov_samples = {
            'follow_on': [], 'capability': [], 'resource': [],
            'abandonment': [], 'contract': [], 'switch': [], 'stage': [],
            'interaction': [], 'risk_premium': [], 'deferral': [],
        }

        for _ in range(self.n_simulations):
            # Tier 2 샘플링
            tier2 = Tier2Sampler.sample(tier1)

            # NPV 계산
            npv = contract * (1 - tier2['cost_ratio'])
            npv_samples.append(npv)

            # 7개 옵션 가치 계산
            rov = self._calculate_all_options(contract, tier1, tier2)

            for key in rov_samples:
                if key in rov:
                    rov_samples[key].append(rov[key])

            # TPV 계산
            tpv = npv + rov['rov_net']
            tpv_samples.append(tpv)

        # 통계 계산
        tpv_array = np.array(tpv_samples)
        npv_array = np.array(npv_samples)

        # 의사결정 확률
        decision_probs = self._calculate_decision_probabilities(tpv_array, npv_array)

        # 평균 ROV 구성
        rov_means = {f'rov_{k}': np.mean(v) for k, v in rov_samples.items() if v}

        return {
            # NPV
            'npv': np.mean(npv_array),
            'npv_std': np.std(npv_array),
            'npv_decision': 'Participate' if np.mean(npv_array) >= 0 else 'Reject',

            # ROV 구성 (7개 옵션)
            'rov_follow_on': np.mean(rov_samples['follow_on']),
            'rov_capability': np.mean(rov_samples['capability']),
            'rov_resource': np.mean(rov_samples['resource']),
            'rov_abandonment': np.mean(rov_samples['abandonment']),
            'rov_contract': np.mean(rov_samples['contract']),
            'rov_switch': np.mean(rov_samples['switch']),
            'rov_stage': np.mean(rov_samples['stage']),

            # ROV 합계
            'rov_gross': np.mean([sum(x) for x in zip(
                rov_samples['follow_on'], rov_samples['capability'],
                rov_samples['resource'], rov_samples['abandonment'],
                rov_samples['contract'], rov_samples['switch'], rov_samples['stage']
            )]),

            # 조정 요소
            'interaction_adjustment': np.mean(rov_samples['interaction']),
            'risk_premium': np.mean(rov_samples['risk_premium']),
            'deferral_value': np.mean(rov_samples['deferral']),

            # ROV Net
            'rov_net': np.mean([t - n for t, n in zip(tpv_samples, npv_samples)]),

            # TPV
            'tpv': np.mean(tpv_array),
            'tpv_std': np.std(tpv_array),
            'tpv_ci_lower': np.percentile(tpv_array, 5),
            'tpv_ci_upper': np.percentile(tpv_array, 95),

            # 의사결정 확률 (신규)
            **decision_probs,

            # TPV 의사결정 (최대 확률 기준)
            'tpv_decision': self._get_most_likely_decision(decision_probs),

            # 의사결정 변경
            'decision_changed': self._check_decision_change(
                np.mean(npv_array), decision_probs
            ),

            # 의사결정 방향
            'decision_direction': self._get_decision_direction(
                np.mean(npv_array), decision_probs
            ),
        }

    def _calculate_all_options(self, contract: float, tier1: Dict, tier2: Dict) -> Dict:
        """7개 옵션 가치 + 조정 요소 계산"""

        fp = self.fixed_params  # 고정 파라미터

        # === (+) 옵션 가치 (7개) ===

        # 경쟁 리스크 할인 계수 (Porter 1980, Li & Akintoye 2003)
        competition_discount = 1 - (tier2['competition_level'] * 0.25)

        # 1. 후속설계 참여 옵션 (조달청 2023 - 인프라 유형별 차별화)
        if tier2['has_follow_on'] and tier2['follow_on_prob'] > 0:
            # 인프라 유형별 연계율 (분리발주율 반영)
            infra_type_follow_rate = {
                'Road': 0.30,     # 도로: 분리발주 75%
                'Bridge': 0.45,   # 교량: 분리발주 58%
                'Tunnel': 0.60    # 터널: 분리발주 45%
            }
            infra_type = tier2.get('infra_type', 'Road')
            exercise_rate = infra_type_follow_rate.get(infra_type, 0.45)

            S0 = contract * tier2['follow_on_prob'] * tier2['follow_on_multiplier']
            K = contract * tier2['cost_ratio'] * tier2['follow_on_multiplier']
            rov_follow = max(S0 - K, 0) * exercise_rate
            rov_follow *= competition_discount  # 경쟁 할인
        else:
            rov_follow = 0

        # 2. 역량 축적 옵션 (한계효용 체감 반영 - Argote & Epple 1990)
        learning_diminishing = 1 - (tier2['capability_level'] ** 1.5)
        rov_capability = (contract * tier2['complexity'] *
                          fp['capability_growth_rate'] * learning_diminishing)
        rov_capability *= competition_discount  # 경쟁 할인

        # 3. 자원 활용 옵션
        resource_mult = 1 - tier2['resource_utilization']
        rov_resource = (contract * resource_mult *
                        fp['resource_utilization_premium'] * tier2['complexity'])
        rov_resource *= competition_discount  # 경쟁 할인

        # 4. 포기 옵션 (Triantis 2005 - 조기 종료 유연성)
        npv = contract * (1 - tier2['cost_ratio'])
        # NPV가 낮거나, 전략적 정합성이 낮으면 포기 옵션 활성화
        if npv < contract * 0.15 or tier2['strategic_alignment'] < 0.30:
            completion_ratio = 0.45  # 평균 45% 수행 후 포기
            salvage = contract * completion_ratio * 0.80  # 기성 80% 인정

            # 자원 재배치 가치
            reallocation_value = (contract * (1 - completion_ratio) *
                                  tier2['resource_utilization'] * 0.50)

            rov_abandonment = max(salvage + reallocation_value - contract * completion_ratio, 0)
        else:
            rov_abandonment = 0

        # 5. 축소 옵션 (신규)
        scope_flex = {'Road': 0.7, 'Bridge': 0.5, 'Tunnel': 0.3}.get(
            tier2.get('infra_type', 'Road'), 0.5
        )
        adverse_prob = max(0, tier2['cost_ratio'] - 0.85) * 2
        rov_contract = contract * scope_flex * adverse_prob * fp['contract_flexibility_rate']

        # 6. 전환 옵션 (신규)
        resource_mobility = 1 - tier2['complexity'] * 0.5
        rov_switch = (contract * resource_mobility *
                      tier2['alternative_attractiveness'] * fp['switch_mobility_rate'])

        # 7. 단계적 투자 옵션 (신규)
        info_factor = min(tier2['time_to_decision'], 2.0) / 2.0
        rov_stage = (contract * tier2['n_milestones'] *
                     info_factor * fp['stage_checkpoint_value'])

        # (+) 합계
        rov_gross = (rov_follow + rov_capability + rov_resource +
                     rov_abandonment + rov_contract + rov_switch + rov_stage)

        # === (-) 조정 요소 (3개) ===

        # 1. 옵션 상호작용 할인 (Trigeorgis 1993 - 옵션 개수에 비례)
        active_options = sum([
            rov_follow > 0, rov_capability > 0, rov_resource > 0,
            rov_abandonment > 0, rov_contract > 0, rov_switch > 0, rov_stage > 0
        ])
        if active_options >= 6:
            interaction_discount = 0.22
        elif active_options >= 4:
            interaction_discount = 0.15
        else:
            interaction_discount = 0.08

        interaction = rov_gross * interaction_discount
        rov_adj = rov_gross - interaction

        # 2. 리스크 프리미엄 (Borison 2005 - 변동성 및 복잡도 연동)
        base_premium = 0.10
        volatility_premium = tier2['volatility'] * 0.25
        complexity_premium = tier2['complexity'] * 0.08
        risk_premium_rate = base_premium + volatility_premium + complexity_premium
        risk_premium = rov_adj * risk_premium_rate

        # 3. 연기옵션 가치 (Dixit & Pindyck 1994 - 자원 제약 반영)
        resource_opportunity = tier2['resource_utilization']  # 가동률 높으면 연기 가치 증가
        market_opportunity = tier2['alternative_attractiveness'] * (1 + resource_opportunity)
        deferral = (contract * (1 - tier2['strategic_alignment']) *
                    market_opportunity * 0.12 * np.sqrt(tier2['time_to_decision']))

        # ROV Net
        rov_net = rov_adj - risk_premium - deferral

        return {
            'follow_on': rov_follow,
            'capability': rov_capability,
            'resource': rov_resource,
            'abandonment': rov_abandonment,
            'contract': rov_contract,
            'switch': rov_switch,
            'stage': rov_stage,
            'interaction': interaction,
            'risk_premium': risk_premium,
            'deferral': deferral,
            'rov_net': rov_net,
        }

    def _calculate_decision_probabilities(self, tpv_array: np.ndarray,
                                           npv_array: np.ndarray) -> Dict:
        """의사결정 확률 계산 (보정된 임계값)"""
        n = len(tpv_array)
        npv_mean = np.mean(npv_array)

        # 계약금액 대비 ROV 기여도로 판단 (더 엄격한 기준)
        # Strong: TPV가 NPV의 150% 이상 AND TPV > 30M
        # Participate: NPV의 105-150% OR 10M < TPV <= 30M
        # Conditional: NPV의 80-105% OR 0 < TPV <= 10M
        # Reject: TPV < NPV의 80% OR TPV <= 0

        return {
            'prob_strong_participate': np.sum((tpv_array > npv_mean * 1.5) & (tpv_array > 30)) / n,
            'prob_participate': np.sum(((tpv_array > npv_mean * 1.05) & (tpv_array <= npv_mean * 1.5)) |
                                      ((tpv_array > 10) & (tpv_array <= 30))) / n,
            'prob_conditional': np.sum(((tpv_array > npv_mean * 0.80) & (tpv_array <= npv_mean * 1.05)) |
                                      ((tpv_array > 0) & (tpv_array <= 10))) / n,
            'prob_reject': np.sum((tpv_array <= npv_mean * 0.80) | (tpv_array <= 0)) / n,
            'decision_robustness': None,  # 아래에서 계산
        }

    def _get_most_likely_decision(self, probs: Dict) -> str:
        """가장 확률 높은 의사결정 반환"""
        decision_map = {
            'prob_strong_participate': 'Strong Participate',
            'prob_participate': 'Participate',
            'prob_conditional': 'Conditional',
            'prob_reject': 'Reject',
        }

        max_key = max(decision_map.keys(), key=lambda k: probs.get(k, 0))
        probs['decision_robustness'] = probs[max_key]

        return decision_map[max_key]

    def _check_decision_change(self, npv_mean: float, probs: Dict) -> bool:
        """의사결정 변경 여부 판정"""
        npv_decision = 'Participate' if npv_mean >= 0 else 'Reject'

        # 가장 높은 확률의 TPV 의사결정
        if probs['prob_strong_participate'] + probs['prob_participate'] > 0.5:
            tpv_direction = 'Participate'
        elif probs['prob_reject'] > 0.5:
            tpv_direction = 'Reject'
        else:
            tpv_direction = 'Conditional'

        return npv_decision != tpv_direction

    def _get_decision_direction(self, npv_mean: float, probs: Dict) -> str:
        """의사결정 방향 판단 (Up: 불참→참여, Down: 참여→불참)"""
        npv_decision = 'Participate' if npv_mean >= 0 else 'Reject'

        # TPV 기반 의사결정 방향
        if probs['prob_strong_participate'] + probs['prob_participate'] > 0.5:
            tpv_direction = 'Participate'
        elif probs['prob_reject'] > 0.5:
            tpv_direction = 'Reject'
        else:
            return 'No Change'

        # 방향 판정
        if npv_decision == 'Reject' and tpv_direction == 'Participate':
            return 'Up'
        elif npv_decision == 'Participate' and tpv_direction == 'Reject':
            return 'Down'
        else:
            return 'No Change'

    def _sensitivity_analysis(self, df: pd.DataFrame) -> Dict:
        """민감도 분석 (Tier 2 분포 파라미터 변동)"""

        # 간소화된 민감도 분석: Tier 2 파라미터별 TPV 영향도
        # 재귀 호출 방지를 위해 간단한 분석만 수행

        sensitivity_params = [
            'cost_ratio', 'follow_on_prob', 'strategic_alignment',
            'alternative_attractiveness', 'volatility', 'capability_level',
            'resource_utilization', 'recovery_rate', 'competition_level', 'complexity'
        ]

        sensitivity_results = {}

        for param in sensitivity_params:
            # 파라미터별 영향도 (플레이스홀더)
            # 실제 구현에서는 Tier2Sampler의 분포 파라미터를 조정하여 재평가
            sensitivity_results[param] = {
                'impact': np.random.uniform(-0.3, 0.3),
                'direction': 'positive' if np.random.random() > 0.5 else 'negative'
            }

        return {
            'baseline_tpv': 0.0,  # 플레이스홀더
            'param_sensitivity': sensitivity_results,
            'most_sensitive_param': max(sensitivity_results.items(),
                                        key=lambda x: abs(x[1]['impact']))[0]
        }


# 테스트 코드
if __name__ == '__main__':
    # 샘플 데이터 생성
    sample_data = pd.DataFrame([
        {
            'project_id': 'P001',
            'contract_amount': 250,
            'infra_type': 'Road',
            'design_phase': '기본설계',
            'contract_duration': 1.0,
            'procurement_type': '제한경쟁',
            'client_type': '중앙'
        }
    ])

    engine = ValuationEngine(n_simulations=1000)
    results, sensitivity = engine.run_valuation(sample_data)

    print("\n=== Valuation Results ===")
    print(results.to_string())
    print("\n=== Sensitivity Analysis ===")
    print(f"Baseline TPV: {sensitivity['baseline_tpv']:.2f}M")
    print(f"Most Sensitive Parameter: {sensitivity['most_sensitive_param']}")
