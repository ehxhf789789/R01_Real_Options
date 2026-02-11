#!/usr/bin/env python3
"""
BIM Real Options Valuation Engine
7 Real Options + 3-Tier Probabilistic Valuation System
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List

try:
    from tier_system import Tier0Input, Tier1Derivation, Tier2Sampler
except ImportError:
    from .tier_system import Tier0Input, Tier1Derivation, Tier2Sampler


class ValuationEngine:
    """BIM Real Options Valuation Engine"""

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

            # 조정 파라미터 (과대평가 방지 강화)
            'interaction_discount': 0.18,      # 0.12 → 0.18 (복수 옵션 중복 할인 강화)
            'risk_premium_rate': 0.25,          # 0.15 → 0.25 (복잡도·변동성 리스크 강화)
            'deferral_multiplier': 0.08,        # 0.05 → 0.08 (기회비용 반영 강화)

            # ROV 상한 제약 (Trigeorgis 1996)
            'rov_cap_ratio': 0.80,              # ROV ≤ 0.80 × |NPV|
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
            # Tier 0 입력 객체 생성 (10개 변수)
            tier0 = Tier0Input(
                project_id=row['project_id'],
                contract_amount=row['contract_amount'],
                infra_type=row['infra_type'],
                design_phase=row['design_phase'],
                contract_duration=row['contract_duration'],
                procurement_type=row['procurement_type'],
                client_type=row['client_type'],
                firm_size=row['firm_size'],
                bim_years=int(row['bim_years']),
                same_type_count=int(row['same_type_count']),
                current_utilization=float(row['current_utilization']),
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

        # 1. 후속설계 참여 옵션 - 복합옵션 (Geske 1979) + 음수 허용
        if tier2['has_follow_on'] and tier2['follow_on_prob'] > 0:
            # 1단계: 기본설계 NPV 평가
            npv_stage1 = contract * (1 - tier2['cost_ratio'])

            # 2단계: 실시설계 기대가치
            S2 = contract * tier2['follow_on_multiplier'] * tier2['follow_on_prob']
            K2 = contract * tier2['follow_on_multiplier'] * tier2['cost_ratio']

            # 복합옵션 행사 조건 (3개 모두 만족해야 행사)
            condition1 = npv_stage1 > 0
            condition2 = tier2['follow_on_prob'] > 0.5
            condition3 = tier2['strategic_alignment'] > 0.4

            if condition1 and condition2 and condition3:
                # Geske 근사식 (경쟁 리스크 반영)
                # 🔥 FIX: 전략적 부적합 시 음수 전환 허용
                if tier2['strategic_alignment'] < 0.50:
                    strategic_penalty = (0.50 - tier2['strategic_alignment']) * contract * 0.15
                    intrinsic_value = (S2 - K2) - strategic_penalty  # 음수 가능
                else:
                    intrinsic_value = max(S2 - K2, 0)

                time_decay = np.exp(-fp['risk_free_rate'] * tier1['time_to_decision'])

                # 인프라 유형별 실현률 (조달청 2023 분리발주율 기반)
                infra_realization = {
                    'Road': 0.25,     # 도로: 분리발주 75% → 실현 25%
                    'Bridge': 0.42,   # 교량: 분리발주 58% → 실현 42%
                    'Tunnel': 0.55    # 터널: 분리발주 45% → 실현 55%
                }
                infra_type = tier2.get('infra_type', 'Road')
                realization_rate = infra_realization.get(infra_type, 0.35)

                rov_follow = intrinsic_value * time_decay * realization_rate * competition_discount
            else:
                rov_follow = 0
        else:
            rov_follow = 0

        # 2. 역량 축적 옵션 (한계효용 체감 반영 - Argote & Epple 1990) + 음수 허용
        # 🔥 FIX: BIM 미숙련 기업은 학습 비용 > 학습 효과 → 음수
        bim_threshold = 0.60
        if tier2['capability_level'] < bim_threshold:
            # 미숙련: 학습 비용이 학습 효과를 초과
            learning_cost = contract * tier2['complexity'] * (bim_threshold - tier2['capability_level']) * 0.20
            learning_benefit = contract * tier2['complexity'] * tier2['capability_level'] * 0.10
            rov_capability = learning_benefit - learning_cost  # 음수 가능
        else:
            # 숙련: 기존 로직 유지
            learning_diminishing = 1 - (tier2['capability_level'] ** 1.5)
            rov_capability = (contract * tier2['complexity'] *
                              fp['capability_growth_rate'] * learning_diminishing)
        rov_capability *= competition_discount  # 경쟁 할인

        # 3. 자원 활용 옵션 + 음수 허용
        # 🔥 FIX: 가동률 과부하 시 기회비용 > 유휴자원 가치 → 음수
        if tier2['resource_utilization'] > 0.80:
            # 가동률 초과: 기회비용 발생
            overload_cost = (tier2['resource_utilization'] - 0.80) * contract * 0.15
            idle_benefit = contract * (1 - tier2['resource_utilization']) * 0.06
            rov_resource = idle_benefit - overload_cost  # 음수 가능
        else:
            # 정상 가동률
            resource_mult = 1 - tier2['resource_utilization']
            rov_resource = (contract * resource_mult *
                            fp['resource_utilization_premium'] * tier2['complexity'])
        rov_resource *= competition_discount  # 경쟁 할인

        # 4. 포기 옵션 (Triantis 2005 - 조기 종료 유연성) + 음수 허용
        npv = contract * (1 - tier2['cost_ratio'])
        # 🔥 FIX: NPV > 0인 우량 프로젝트는 포기 옵션이 오히려 손실
        if npv > 0:
            # 우량 프로젝트: 포기하면 손실 → 음수
            rov_abandonment = -contract * 0.02
        elif npv < contract * 0.15 or tier2['strategic_alignment'] < 0.30:
            # 부실 프로젝트: 포기 옵션 가치 있음
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
            interaction_discount = 0.30
        elif active_options >= 4:
            interaction_discount = 0.22
        else:
            interaction_discount = 0.15

        interaction = rov_gross * interaction_discount
        rov_adj = rov_gross - interaction

        # 2. 리스크 프리미엄 (Borison 2005 - 변동성 및 복잡도 연동)
        base_premium = 0.15
        volatility_premium = tier2['volatility'] * 0.30
        complexity_premium = tier2['complexity'] * 0.10
        risk_premium_rate = base_premium + volatility_premium + complexity_premium
        risk_premium = rov_adj * risk_premium_rate

        # 3. 연기옵션 가치 (Dixit & Pindyck 1994 - 자원 제약 반영)
        resource_opportunity = tier2['resource_utilization']  # 가동률 높으면 연기 가치 증가
        market_opportunity = tier2['alternative_attractiveness'] * (1 + resource_opportunity)
        deferral = (contract * (1 - tier2['strategic_alignment']) *
                    market_opportunity * 0.18 * np.sqrt(tier2['time_to_decision']))

        # ROV Net (조정 전)
        rov_net_raw = rov_adj - risk_premium - deferral

        # === ROV 상한 제약 (Trigeorgis 1996) ===
        # NPV 대비 과도한 ROV 제한
        npv = contract * (1 - tier2['cost_ratio'])
        rov_cap = abs(npv) * fp['rov_cap_ratio']  # ROV ≤ 0.80 × |NPV|

        if rov_net_raw > rov_cap:
            rov_net = rov_cap
            cap_applied = True
        else:
            rov_net = rov_net_raw
            cap_applied = False

        # ROV Net = 3가지 조정요소만 적용 (논문 정의)

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
            'rov_cap_applied': cap_applied,  # 디버깅용
            'rov_cap_value': rov_cap,        # 디버깅용
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
