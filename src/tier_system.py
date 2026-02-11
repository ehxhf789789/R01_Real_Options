#!/usr/bin/env python3
"""
Tier System: 입력 데이터 계층 변환
5-Level Hierarchical Framework (논문 Figure 1)
Level 1 (Data Input) → Level 2 (Parameter Mapping) → Level 3 (Probabilistic Modeling)

Implementation as: Tier 0 (확정) → Tier 1 (파생) → Tier 2 (확률분포)
"""

import numpy as np
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass
class Tier0Input:
    """
    Level 1: 공고문에서 확정적으로 추출 가능한 입력 (Table 8 from Paper)

    Tender Document Variables (6):
        S: Contract Amount (계약금액)
        I: Infrastructure Type (인프라 유형)
        D: Design Phase (과업 수행 단계)
        T: Contract Duration (계약 기간)
        P: Procurement Type (발주 방식)
        C: Client Type (발주처 유형)

    Company Characteristic Variables (4):
        Firm Size, BIM Years, Same-type Count, Current Utilization
    """
    # 입찰 공고 변수 (6개) - Table 8
    project_id: str
    contract_amount: float      # S: 백만원
    infra_type: str             # I: Road, Bridge, Tunnel
    design_phase: str           # D: 기본설계/Basic Design, 실시설계/Detailed Design
    contract_duration: float    # T: 년
    procurement_type: str       # P: 일반경쟁/Open, 제한경쟁/Limited, 지명경쟁/Nominated
    client_type: str            # C: 중앙/Central, 지방/Local, 공기업/Public Corp

    # 기업 특성 변수 (4개) - Table 4
    firm_size: str              # Large, Medium, Small
    bim_years: int              # BIM 도입 연차 (년)
    same_type_count: int        # 최근 5년 동일 유형 실적 (건수)
    current_utilization: float  # 현재 가동률 (0.0-1.0)


class Tier1Derivation:
    """
    Level 2: Parameter Mapping (Table 2, 4 from Paper)
    Tier 0 → Tier 1 결정론적 변환 규칙
    """

    # === 인프라 유형별 파라미터 (Table 2 from Paper) ===

    # 기본 복잡도 κ₀ (Flyvbjerg et al. 2003 - 비용초과율 정규화)
    # Road: 20.4/33.8 = 0.60, Bridge: 0.85, Tunnel: 1.00 (reference)
    BASE_COMPLEXITY = {
        'Road': 0.60,
        'Bridge': 0.85,
        'Tunnel': 1.00
    }

    # 설계 변경 유연성 f_scope (Eq.4 from Paper)
    # σ_road/σ_type 비율로 계산
    DESIGN_FLEXIBILITY = {
        'Road': 1.00,    # 29.9/29.9
        'Bridge': 0.65,  # 29.9/46.2
        'Tunnel': 0.48   # 29.9/62.4
    }

    # 기본 변동성 σ₀ (Eq.5 from Paper with α=1.86)
    BASE_VOLATILITY = {
        'Road': 0.22,
        'Bridge': 0.35,
        'Tunnel': 0.42
    }

    # 설계 검토 횟수 n (MOLIT 2024)
    DESIGN_REVIEWS = {
        'Road': 3,      # VE×2 + General Review
        'Bridge': 4,    # VE×2 + Seismic + Structural
        'Tunnel': 4     # VE×2 + Special Method + Ground Safety
    }

    # 후속사업 규모 배수 m_f (MOTIE 2024)
    VALUE_MULTIPLIER = {
        'Road': 1.67,      # 실시설계/기본설계 요율 비율
        'Bridge': 1.84,    # 1.67 × 1.10 (난이도 조정)
        'Tunnel': 1.84     # 1.67 × 1.10 (난이도 조정)
    }

    # === 발주 방식별 파라미터 (KENCA 2023, Beak et al. 2015) ===
    COMPETITION_PARAMS = {
        # Korean
        '일반경쟁': {'mean': 0.72, 'std': 0.14},
        '제한경쟁': {'mean': 0.48, 'std': 0.10},
        '지명경쟁': {'mean': 0.21, 'std': 0.04},
        # English
        'Open': {'mean': 0.72, 'std': 0.14},
        'Limited': {'mean': 0.48, 'std': 0.10},
        'Nominated': {'mean': 0.21, 'std': 0.04},
    }

    # === 발주처 신뢰도 φ_c (KENCA 2023 - 기성금 지급 지연율 기반) ===
    CLIENT_RELIABILITY = {
        # Korean
        '중앙': 0.92,     # 중앙정부: 1 - 8.2% = 0.918 ≈ 0.92
        '공기업': 0.88,   # 공기업: 1 - 12.5% = 0.875 ≈ 0.88
        '지방': 0.81,     # 지자체: 1 - 18.7% = 0.813 ≈ 0.81
        # English
        'Central': 0.92,
        'Public Corp': 0.88,
        'Local': 0.81,
    }

    # === 기업 규모별 원가율 C₀ (KENCA 2023 - Table 3 from Paper) ===
    COST_RATIO_BASE = {
        'Large': 0.87,   # 대기업: 영업이익률 13.2% → 원가율 86.8%
        'Medium': 0.92,  # 중견기업: 영업이익률 7.8% → 원가율 92.2%
        'Small': 0.97,   # 소기업: 영업이익률 2.9% → 원가율 97.1%
    }

    @staticmethod
    def derive(tier0: Tier0Input) -> Dict:
        """Tier 0에서 Tier 1 파생 (Level 2: Parameter Mapping)"""

        infra_type = tier0.infra_type

        # 1. 후속설계 존재 여부 F (기본설계/Basic Design만 후속 있음)
        has_follow_on = (tier0.design_phase in ["기본설계", "Basic Design"])

        # 2. 후속설계 규모 배수 범위 [m_f,min, m_f,max] (NABO 2009: ±15%)
        if has_follow_on:
            base_mult = Tier1Derivation.VALUE_MULTIPLIER.get(infra_type, 1.67)
            follow_on_mult_range = (base_mult * 0.85, base_mult * 1.15)  # ±15%
        else:
            follow_on_mult_range = (0.0, 0.0)

        # 3. 기본 복잡도 κ₀ (Flyvbjerg et al. 2003)
        base_complexity = Tier1Derivation.BASE_COMPLEXITY.get(infra_type, 0.60)

        # 복잡도 조정 κ_adj (Eq.3 from Paper: Bosch-Rekveldt et al. 2011)
        # κ_adj = 1 + ε × (S/S_ref - 1), ε=0.13, S_ref=100억원
        complexity_adjustment = 1 + 0.13 * (tier0.contract_amount / 100 - 1)
        complexity_value = base_complexity * complexity_adjustment

        # 4. 경쟁 수준 분포 파라미터 μ_c, σ_c (KENCA 2023, Beak et al. 2015)
        competition_params = Tier1Derivation.COMPETITION_PARAMS.get(
            tier0.procurement_type, {'mean': 0.48, 'std': 0.10})

        # 5. 마일스톤 수 n (MOLIT 2024)
        n_milestones = Tier1Derivation.DESIGN_REVIEWS.get(infra_type, 3)

        # 6. 후속 확률 Beta 분포 파라미터 (Jofre-Bonet & Pesendorfer 2003)
        # (α, β) = (3.2, 2.3), mean ≈ 0.58
        if has_follow_on:
            follow_on_beta_params = (3.2, 2.3)  # Paper Table 2
        else:
            follow_on_beta_params = (1.0, 9.0)  # Very low probability

        # 7. 발주처 신뢰도 φ_c (KENCA 2023)
        client_reliability = Tier1Derivation.CLIENT_RELIABILITY.get(tier0.client_type, 0.85)

        # 8. 기본 변동성 σ₀ (Flyvbjerg et al. 2003, Eq.5)
        base_volatility = Tier1Derivation.BASE_VOLATILITY.get(infra_type, 0.22)

        # 9. 설계 유연성 f_scope (Flyvbjerg et al. 2003, Eq.4)
        design_flexibility = Tier1Derivation.DESIGN_FLEXIBILITY.get(infra_type, 0.65)

        # === 기업 특성 변수 파라미터 변환 (Table 4 from Paper) ===

        # 10. 기업 규모 → 기본 원가율 C₀ (KENCA 2023)
        cost_ratio_base = Tier1Derivation.COST_RATIO_BASE.get(tier0.firm_size, 0.92)

        # 11. BIM 도입 연차 → BIM 숙련도 L (Eq.7 from Paper)
        # L = ln(1+Y) / ln(1+Y_sat), Y_sat=10년 (Lee & Yu 2020)
        if tier0.bim_years >= 10:
            bim_expertise = 1.0
        else:
            bim_expertise = np.log(1 + tier0.bim_years) / np.log(1 + 10)

        # 12. 동일 유형 실적 → 전략적 적합성 S (Eq.8 from Paper)
        # S = 0.40 + 0.55 × min(N, N_ref) / N_ref, N_ref=10
        N = tier0.same_type_count
        N_ref = 10
        strategic_fit = 0.40 + 0.55 * min(N, N_ref) / N_ref

        # 13. 현재 가동률 → 유휴 자원 비율 R_idle (Eq.9 from Paper)
        idle_resource_ratio = 1.0 - tier0.current_utilization

        return {
            # 프로젝트 특성 (from Tender Documents)
            'has_follow_on': has_follow_on,
            'follow_on_mult_range': follow_on_mult_range,
            'complexity': complexity_value,
            'base_complexity': base_complexity,
            'competition_params': competition_params,
            'n_milestones': n_milestones,
            'follow_on_beta_params': follow_on_beta_params,
            'client_reliability': client_reliability,
            'time_to_decision': tier0.contract_duration,
            'infra_type': tier0.infra_type,
            'contract_amount': tier0.contract_amount,
            'design_phase': tier0.design_phase,
            'base_volatility': base_volatility,
            'design_flexibility': design_flexibility,

            # 기업 특성 (from Company Characteristics)
            'cost_ratio_base': cost_ratio_base,
            'bim_expertise': bim_expertise,
            'strategic_fit': strategic_fit,
            'idle_resource_ratio': idle_resource_ratio,
            'firm_size': tier0.firm_size,
        }


class Tier2Sampler:
    """
    Level 3: Probabilistic Modeling (Table 5 from Paper)
    Tier 2 확률 분포 샘플링 (Vose 2008 criteria)
    """

    @classmethod
    def sample(cls, tier1: Dict) -> Dict:
        """Tier 1 기반으로 Tier 2 파라미터 샘플링"""

        sampled = {}

        # === 1. 비용 비율 C - Triangular Distribution (KENCA 2023) ===
        # Range-Constrained: (0.80, C₀, 0.98)
        cost_ratio_base = tier1.get('cost_ratio_base', 0.92)
        competition = tier1.get('competition_level', 0.5)
        design_phase = tier1.get('design_phase', '기본설계')

        # 경쟁 강도에 따른 조정 (경쟁 높으면 저가 입찰 → 비용비율 상승)
        competition_penalty = competition * 0.10
        adjusted_mode = min(cost_ratio_base + competition_penalty, 0.98)

        # 실시설계는 경쟁 더 심화
        if '실시' in design_phase or 'Detailed' in design_phase:
            adjusted_mode = min(adjusted_mode + 0.03, 0.98)

        # 삼각분포 (0.80, mode, 0.98) - Table 5
        sampled['cost_ratio'] = np.random.triangular(0.80, adjusted_mode, 0.98)

        # === 2. 후속 수주 확률 p_f - Beta Distribution ===
        # (α, β) = (3.2, 2.3), mean ≈ 0.58 (Jofre-Bonet & Pesendorfer 2003)
        if tier1['has_follow_on']:
            alpha, beta = tier1['follow_on_beta_params']
            sampled['follow_on_prob'] = np.random.beta(alpha, beta)

            # 후속 배수 m_f - Uniform [m_f,min, m_f,max]
            mult_range = tier1['follow_on_mult_range']
            sampled['follow_on_multiplier'] = np.random.uniform(mult_range[0], mult_range[1])
        else:
            sampled['follow_on_prob'] = 0.0
            sampled['follow_on_multiplier'] = 0.0

        # === 3. 전략적 적합성 S - Triangular (±0.15) ===
        strategic_fit_base = tier1.get('strategic_fit', 0.6)
        sampled['strategic_alignment'] = np.clip(
            np.random.triangular(
                max(0.30, strategic_fit_base - 0.15),
                strategic_fit_base,
                min(0.95, strategic_fit_base + 0.15)
            ), 0.30, 0.95
        )

        # === 4. 대안 매력도 A - Triangular (0.35, 0.55, 0.75) ===
        # (CERIK 2025, KDI 2025)
        sampled['alternative_attractiveness'] = np.random.triangular(0.35, 0.55, 0.75)

        # === 5. 변동성 σ - Dynamic Adjustment (Eq.11 from Paper) ===
        # σ = σ₀ × (1 + (κ - κ̄) / κ̄) with Normal noise
        base_volatility = tier1.get('base_volatility', 0.22)
        complexity = tier1.get('complexity', 0.6)
        base_complexity = tier1.get('base_complexity', 0.6)

        # Complexity-adjusted volatility
        complexity_factor = 1 + (complexity - base_complexity) / max(base_complexity, 0.1)
        adjusted_volatility = base_volatility * complexity_factor

        # Add uncertainty (σ_adj = 0.18 × σ₀)
        volatility_noise = np.random.normal(0, 0.18 * base_volatility)
        sampled['volatility'] = max(0.05, adjusted_volatility + volatility_noise)

        # === 6. BIM 역량 수준 L - Beta from Tier1 ===
        bim_expertise_base = tier1.get('bim_expertise', 0.7)
        # ±5% 변동
        sampled['capability_level'] = np.clip(
            bim_expertise_base + np.random.uniform(-0.05, 0.05), 0.3, 1.0
        )

        # === 7. 자원 활용률 - Uniform (±0.15) ===
        idle_ratio = tier1.get('idle_resource_ratio', 0.3)
        current_util = 1.0 - idle_ratio
        sampled['resource_utilization'] = np.clip(
            current_util + np.random.uniform(-0.05, 0.05), 0.40, 0.95
        )

        # === 8. 잔존가치 회수율 R_sal - Triangular (0.10, 0.30, 0.50) ===
        # (Kodukula & Papudesu 2006)
        sampled['recovery_rate'] = np.random.triangular(0.10, 0.30, 0.50)

        # === 9. 경쟁 수준 c - Truncated Normal ===
        # (μ_c, σ_c, 0, 1) from KENCA 2023
        comp_params = tier1['competition_params']
        raw_competition = np.random.normal(comp_params['mean'], comp_params['std'])
        sampled['competition_level'] = np.clip(raw_competition, 0.0, 1.0)

        # === 10. 복잡도 κ - Normal ===
        complexity_base = tier1.get('complexity', 0.6)
        sampled['complexity'] = np.clip(
            complexity_base + np.random.normal(0, 0.08), 0.1, 1.2
        )

        # === 11. 상호작용 할인율 γ - Uniform [0, 0.30] ===
        # (Trigeorgis 1993)
        sampled['interaction_rate'] = np.random.uniform(0.0, 0.30)

        # Tier 1 정보 그대로 전달
        sampled['n_milestones'] = tier1['n_milestones']
        sampled['time_to_decision'] = tier1['time_to_decision']
        sampled['has_follow_on'] = tier1['has_follow_on']
        sampled['infra_type'] = tier1['infra_type']
        sampled['design_flexibility'] = tier1.get('design_flexibility', 0.65)
        sampled['client_reliability'] = tier1.get('client_reliability', 0.85)

        return sampled


def process_tier0_to_simulation_params(tier0: Tier0Input) -> Dict:
    """Tier 0 입력을 Monte Carlo 시뮬레이션용 파라미터로 변환"""

    # Tier 0 → Tier 1 (Level 2: Parameter Mapping)
    tier1 = Tier1Derivation.derive(tier0)

    # Tier 1 → Tier 2 (Level 3: Probabilistic Modeling) - 단일 샘플
    tier2 = Tier2Sampler.sample(tier1)

    return {
        'tier0': tier0.__dict__,
        'tier1': tier1,
        'tier2': tier2,
    }
