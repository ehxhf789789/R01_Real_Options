#!/usr/bin/env python3
"""
Tier System: 입력 데이터 계층 변환
Tier 0 (확정) → Tier 1 (파생) → Tier 2 (확률분포)
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class Tier0Input:
    """공고문에서 확정적으로 추출 가능한 입력 (10개 변수)"""
    # 입찰 공고 변수 (6개)
    project_id: str
    contract_amount: float      # 백만원
    infra_type: str             # Road, Bridge, Tunnel
    design_phase: str           # 기본설계, 실시설계
    contract_duration: float    # 년
    procurement_type: str       # 일반경쟁, 제한경쟁, 지명경쟁
    client_type: str            # 중앙, 지방, 공기업

    # 기업 특성 변수 (4개) - 필수 입력
    firm_size: str              # Large, Medium, Small
    bim_years: int              # BIM 도입 연차 (년)
    same_type_count: int        # 최근 5년 동일 유형 실적 (건수)
    current_utilization: float  # 현재 가동률 (0.0-1.0)


class Tier1Derivation:
    """Tier 0 → Tier 1 결정론적 변환 규칙"""

    @staticmethod
    def derive(tier0: Tier0Input) -> Dict:
        """Tier 0에서 Tier 1 파생"""

        # 1. 후속설계 존재 여부 (기본설계/Basic Design만 후속 있음)
        has_follow_on = (tier0.design_phase in ["기본설계", "Basic Design"])

        # 2. 후속설계 규모 배수 범위
        if has_follow_on:
            follow_on_mult_range = (1.5, 2.5)  # 실시설계는 기본의 1.5~2.5배
        else:
            follow_on_mult_range = (0.0, 0.0)

        # 3. 프로젝트 복잡도 범위 (인프라 유형 + 금액 기반)
        complexity_base = {
            'Tunnel': 'high',
            'Bridge': 'medium',
            'Road': 'low'
        }.get(tier0.infra_type, 'medium')

        # 금액에 따른 조정 (300M 이상이면 한 단계 상승)
        if tier0.contract_amount >= 300:
            complexity_map = {'low': 'medium', 'medium': 'high', 'high': 'high'}
            complexity_base = complexity_map[complexity_base]

        # 4. 경쟁 수준 분포 파라미터 (Korean + English support)
        competition_params_map = {
            # Korean
            '일반경쟁': {'dist': 'high_variance', 'mean': 0.6, 'std': 0.15},
            '제한경쟁': {'dist': 'medium_variance', 'mean': 0.4, 'std': 0.10},
            '지명경쟁': {'dist': 'low_variance', 'mean': 0.2, 'std': 0.05},
            # English
            'Open': {'dist': 'high_variance', 'mean': 0.6, 'std': 0.15},
            'Limited': {'dist': 'medium_variance', 'mean': 0.4, 'std': 0.10},
            'Negotiated': {'dist': 'low_variance', 'mean': 0.2, 'std': 0.05},
        }
        competition_params = competition_params_map.get(
            tier0.procurement_type, {'dist': 'medium_variance', 'mean': 0.4, 'std': 0.10})

        # 5. 마일스톤 수 (인프라 유형별)
        n_milestones = {
            'Road': 3,      # 노선선정 → 예비설계 → 상세설계
            'Bridge': 3,    # 형식선정 → 구조해석 → 상세설계
            'Tunnel': 4,    # 지질조사 → 단면설계 → 굴착계획 → 상세설계
        }.get(tier0.infra_type, 3)

        # 6. 후속 확률 Beta 분포 파라미터 (설계 단계별)
        if tier0.design_phase in ["기본설계", "Basic Design"]:
            # 기본설계: 후속 확률 높음 (Beta 분포 오른쪽 치우침)
            follow_on_beta_params = (4, 2)  # mean ≈ 0.67
        else:
            # 실시설계: 후속 확률 낮음 (감리 참여 정도)
            follow_on_beta_params = (1.5, 4)  # mean ≈ 0.27

        # 7. 발주처 신뢰도 (Tier 2 샘플링에 영향) - Korean + English support
        client_reliability_map = {
            # Korean
            '중앙': 0.9,    # 국토부 등 - 안정적
            '공기업': 0.8,  # 한국도로공사 등 - 안정적
            '지방': 0.6,    # 지자체 - 변동성 있음
            # English
            'Central': 0.9,
            'Public Corp': 0.8,
            'Local': 0.6,
        }
        client_reliability = client_reliability_map.get(tier0.client_type, 0.7)

        # === 기업 특성 변수 파라미터 변환 (4개) ===

        # 8. 기업 규모 → 기본 원가율 (KENCA 2023)
        cost_ratio_base = {
            'Large': 0.87,   # 대기업: 영업이익률 13.2% → 원가율 86.8%
            'Medium': 0.92,  # 중견기업: 영업이익률 7.8% → 원가율 92.2%
            'Small': 0.97,   # 소기업: 영업이익률 2.9% → 원가율 97.1%
        }.get(tier0.firm_size, 0.92)

        # 9. BIM 도입 연차 → BIM 숙련도 (Lee & Yu 2020 학습곡선)
        # L = L_max * ln(1+Y) / ln(1+Y_sat), Y_sat=10년
        if tier0.bim_years >= 10:
            bim_expertise = 1.0
        else:
            bim_expertise = np.log(1 + tier0.bim_years) / np.log(1 + 10)

        # 10. 동일 유형 실적 → 전략적 적합성 (0.40-0.95 범위)
        # N_ref=10건 기준, 초과 시 0.95 수렴
        N = tier0.same_type_count
        N_ref = 10
        strategic_fit = 0.40 + (0.95 - 0.40) * min(N, N_ref) / N_ref

        # 11. 현재 가동률 → 유휴 자원 비율
        idle_resource_ratio = 1.0 - tier0.current_utilization

        return {
            # 프로젝트 특성
            'has_follow_on': has_follow_on,
            'follow_on_mult_range': follow_on_mult_range,
            'complexity': complexity_base,
            'competition_params': competition_params,
            'n_milestones': n_milestones,
            'follow_on_beta_params': follow_on_beta_params,
            'client_reliability': client_reliability,
            'time_to_decision': tier0.contract_duration,
            'infra_type': tier0.infra_type,
            'contract_amount': tier0.contract_amount,
            'design_phase': tier0.design_phase,

            # 기업 특성 (필수 입력 기반)
            'cost_ratio_base': cost_ratio_base,
            'bim_expertise': bim_expertise,
            'strategic_fit': strategic_fit,
            'idle_resource_ratio': idle_resource_ratio,
            'firm_size': tier0.firm_size,  # 전달
        }


class Tier2Sampler:
    """Tier 2 확률 분포 샘플링"""

    # 기본 분포 설정
    DISTRIBUTIONS = {
        'cost_ratio': {
            'type': 'triangular',
            'params': {'left': 0.75, 'mode': 0.85, 'right': 1.05}
        },
        'strategic_alignment': {
            'type': 'uniform',
            'params': {'low': 0.3, 'high': 0.9}
        },
        'alternative_attractiveness': {
            'type': 'triangular',
            'params': {'left': 0.5, 'mode': 0.8, 'right': 1.2}
        },
        'volatility': {
            'type': 'lognormal',
            'params': {'mean': 0.22, 'sigma': 0.05}
        },
        'capability_level': {
            'type': 'uniform',
            'params': {'low': 0.5, 'high': 0.9}
        },
        'resource_utilization': {
            'type': 'uniform',
            'params': {'low': 0.5, 'high': 0.85}
        },
        'recovery_rate': {
            'type': 'triangular',
            'params': {'left': 0.15, 'mode': 0.28, 'right': 0.40}
        },
    }

    @classmethod
    def sample(cls, tier1: Dict) -> Dict:
        """Tier 1 기반으로 Tier 2 파라미터 샘플링"""

        sampled = {}

        # 1. 비용 비율 (기업 규모 기반 + 경쟁 조정)
        # Tier1에서 계산된 기본 원가율 사용
        cost_ratio_base = tier1.get('cost_ratio_base', 0.92)
        competition = tier1.get('competition_level', 0.5)
        design_phase = tier1.get('design_phase', '기본설계')

        # 경쟁 강도에 따른 조정 (경쟁 높으면 저가 입찰 → 비용비율 상승)
        competition_penalty = competition * 0.12  # 최대 +0.12
        adjusted_mode = cost_ratio_base + competition_penalty

        # 실시설계/Detailed Design는 단순 작업으로 경쟁 더 심화
        if '실시' in design_phase or 'Detailed' in design_phase:
            adjusted_mode += 0.05

        # 삼각분포 파라미터 설정 (기업 특성 반영)
        spread = 0.08  # ±8% 변동 (기업 규모별 차이 반영)
        adjusted_left = max(0.75, adjusted_mode - spread)
        adjusted_right = min(1.10, adjusted_mode + spread)  # 1.10까지 허용

        sampled['cost_ratio'] = np.random.triangular(adjusted_left, adjusted_mode, adjusted_right)

        # 2. 후속 확률 (Tier 1에서 파생된 Beta 파라미터 사용)
        if tier1['has_follow_on']:
            alpha, beta = tier1['follow_on_beta_params']
            sampled['follow_on_prob'] = np.random.beta(alpha, beta)

            # 후속 배수
            mult_range = tier1['follow_on_mult_range']
            sampled['follow_on_multiplier'] = np.random.uniform(mult_range[0], mult_range[1])
        else:
            sampled['follow_on_prob'] = 0.0
            sampled['follow_on_multiplier'] = 0.0

        # 3. 전략적 정합성 (Tier1 입력 기반 + 변동)
        strategic_fit_base = tier1.get('strategic_fit', 0.6)
        # ±10% 변동
        sampled['strategic_alignment'] = np.clip(
            strategic_fit_base + np.random.uniform(-0.10, 0.10), 0.3, 0.95
        )

        # 4. 대안 매력도
        dist = cls.DISTRIBUTIONS['alternative_attractiveness']['params']
        sampled['alternative_attractiveness'] = np.random.triangular(
            dist['left'], dist['mode'], dist['right']
        )

        # 5. 시장 변동성
        dist = cls.DISTRIBUTIONS['volatility']['params']
        sampled['volatility'] = np.random.lognormal(
            np.log(dist['mean']), dist['sigma']
        )

        # 6. BIM 역량 수준 (Tier1 입력 기반)
        bim_expertise_base = tier1.get('bim_expertise', 0.7)
        # ±5% 변동
        sampled['capability_level'] = np.clip(
            bim_expertise_base + np.random.uniform(-0.05, 0.05), 0.5, 1.0
        )

        # 7. 자원 활용률 (Tier1 입력 기반)
        idle_ratio = tier1.get('idle_resource_ratio', 0.3)
        # 현재 가동률 = 1 - idle_ratio
        current_util = 1.0 - idle_ratio
        # ±5% 변동
        sampled['resource_utilization'] = np.clip(
            current_util + np.random.uniform(-0.05, 0.05), 0.5, 0.95
        )

        # 8. 잔존가치 회수율
        dist = cls.DISTRIBUTIONS['recovery_rate']['params']
        sampled['recovery_rate'] = np.random.triangular(
            dist['left'], dist['mode'], dist['right']
        )

        # 9. 경쟁 수준 (Tier 1 파라미터 기반)
        comp_params = tier1['competition_params']
        raw_competition = np.random.normal(comp_params['mean'], comp_params['std'])
        sampled['competition_level'] = np.clip(raw_competition, 0.0, 1.0)

        # 10. 복잡도 (Tier 1에서 파생, 약간의 변동 추가)
        complexity_base = {'low': 0.3, 'medium': 0.6, 'high': 0.9}[tier1['complexity']]
        sampled['complexity'] = np.clip(
            complexity_base + np.random.normal(0, 0.1), 0.1, 1.0
        )

        # Tier 1 정보 그대로 전달
        sampled['n_milestones'] = tier1['n_milestones']
        sampled['time_to_decision'] = tier1['time_to_decision']
        sampled['has_follow_on'] = tier1['has_follow_on']
        sampled['infra_type'] = tier1['infra_type']

        return sampled


def process_tier0_to_simulation_params(tier0: Tier0Input) -> Dict:
    """Tier 0 입력을 Monte Carlo 시뮬레이션용 파라미터로 변환"""

    # Tier 0 → Tier 1
    tier1 = Tier1Derivation.derive(tier0)

    # Tier 1 → Tier 2 (단일 샘플)
    tier2 = Tier2Sampler.sample(tier1)

    return {
        'tier0': tier0.__dict__,
        'tier1': tier1,
        'tier2': tier2,
    }
