# Real Options Theory

## Why Real Options?

### Limitations of Traditional NPV (DCF)

Traditional Net Present Value (NPV) analysis based on Discounted Cash Flow (DCF) has significant limitations when evaluating projects with high uncertainty:

1. **Static Assumption**: NPV assumes a fixed project plan that cannot be changed once investment is decided
2. **Ignores Managerial Flexibility**: Management's ability to expand, contract, or abandon projects in response to market changes is not valued
3. **Binary Decision**: Projects are either accepted or rejected, with no middle ground
4. **Undervalues Strategic Options**: Projects with low short-term profitability but high long-term growth potential are undervalued

> "DCF의 한계는 리스크 자체를 무시하는 것이 아닌, 불확실성에 대응하는 유연한 의사결정 권한의 경제적 가치를 평가 체계에 포함하지 못한다는 점에 있다." - Trigeorgis (1996)

### What are Real Options?

Real Options extend financial option theory to real (physical) assets and strategic decisions. Just as a financial call option gives the holder the right (but not obligation) to buy a stock at a predetermined price, a real option gives management the right to take certain actions in the future.

**Key Insight**: Uncertainty + Flexibility = Value (Managerial Flexibility)

When a company has the flexibility to respond to uncertainty, that uncertainty actually creates value!

**Key Theoretical Foundation**:
- Myers (1977): Corporate investments have option-like characteristics
- Dixit & Pindyck (1994): Real options are especially important when uncertainty is high and investments are irreversible
- Trigeorgis (1996): Expanded NPV = Traditional NPV + Option Value
- Copeland & Antikarov (2001): Practical framework for real options valuation

---

## Core Formula

### Total Project Value (TPV)

```
TPV = NPV + ROV                                    ... Eq.(1)
```

Where:
- **TPV**: Total Project Value (총 프로젝트 가치)
- **NPV**: Net Present Value - Deterministic revenue (확정적 수익)
- **ROV**: Real Option Value - Opportunity value (기회 가치)

### Real Option Value (ROV)

```
ROV = Σ(7 Options) - Σ(3 Adjustments)              ... Eq.(2)

     7              3
ROV = Σ Option_i - Σ Adjustment_j
     i=1           j=1

Where:
  Adjustments = Interaction Discount (I_int) + Risk Premium (P_risk) + Deferral Cost (C_wait)
```

### Net Present Value (NPV)

```
NPV = S × (1 - C_adj)                              ... Eq.(12)

Where:
  S = Contract Amount (총 계약 금액)
  C_adj = Adjusted Cost Ratio (조정된 원가율)
```

---

## The 7 Real Options in This Model

Based on Trigeorgis (1996) classification, operationalized for BIM engineering projects:

### Category 1: Growth Options (성장 잠재력)

#### 1. Option to Expand (O_exp) - 후속 사업 참여 옵션

**Definition**: Leveraging information advantage for subsequent projects (선행 사업 수행으로 획득한 정보 우위를 활용한 후속 사업 참여 기회)

**BIM Project Interpretation**:
- Basic design creates opportunity for detailed design participation
- Information advantage from understanding project scope, risks, and client requirements
- Compound Option characteristics (Geske 1979)

**Activation Condition**: Preliminary Design Phase (기본설계 단계)

**When it's valuable**:
- Basic design phase with high probability of detailed design follow-up
- Strong relationship with client (발주처 신뢰도 높음)
- Good project performance

**Theoretical Basis**: Compound Option Theory (Geske 1979)

**Key Parameters**:
- Follow-on Probability: Beta(α=3.2, β=2.3), mean ≈ 0.58 (Jofre-Bonet & Pesendorfer 2003)
- Value Multiplier (m_f): Road 1.67, Bridge/Tunnel 1.84 (MOTIE 2024)
- Multiplier Range: ±15% based on NABO (2009) bid rate statistics

---

#### 2. Growth Option (O_grw) - 역량 축적 옵션

**Definition**: Accumulating BIM capabilities and technical assets (BIM 역량 축적 및 기술 자산화)

**BIM Project Interpretation**:
- High-complexity BIM project execution accumulates organizational know-how
- Learning effects reduce costs in future similar projects
- Technical capabilities become organizational assets

**Activation Condition**: High Project Complexity (고복잡도 프로젝트)

**When it's valuable**:
- Early stage of BIM adoption (BIM 도입 초기)
- Complex projects that accelerate learning
- Strategic importance for future capabilities

**Theoretical Basis**: Learning Curve Theory (Argote & Epple 1990; Wright 1936)

**BIM Expertise Formula**:
```
L = ln(1 + Y) / ln(1 + Y_sat)                      ... Eq.(7)

Where:
  L = BIM expertise level (0 to 1)
  Y = years since BIM adoption
  Y_sat = 10 years (saturation point, Lee & Yu 2020)

Results:
  Year 1: 0.29, Year 3: 0.58, Year 5: 0.75, Year 10+: 1.00
```

---

### Category 2: Flexibility Options (운영 유연성)

#### 3. Option to Switch-In (O_swi) - 자원 활용 옵션

**Definition**: Utilizing idle manpower to prevent fixed cost loss (유휴 인력 활용으로 고정비 손실 방지)

**BIM Project Interpretation**:
- Deploy underutilized resources to new projects
- Prevent fixed cost absorption issues
- Match resource requirements with available capacity

**Activation Condition**: Low Resource Utilization (낮은 자원 가동률)

**Idle Resource Ratio Formula**:
```
R_idle = 1 - U_current                             ... Eq.(9)

Where:
  R_idle = Idle resource ratio
  U_current = Current utilization rate
```

---

#### 4. Option to Contract (O_cnt) - 계약 유연성 옵션

**Definition**: Adjusting scope via consultation under cost overruns (원가 초과 시 협의를 통한 범위 조정)

**BIM Project Interpretation**:
- Negotiate with client to reduce scope when budget exceeds
- Flexibility coefficient varies by infrastructure type based on physical irreversibility
- Higher for road (adjustable), lower for tunnel (irreversible)

**Activation Condition**: High Physical Irreversibility (높은 물리적 비가역성)

**Design Flexibility by Infrastructure Type (f_scope)**:

| Type | f_scope | Derivation | Rationale |
|------|---------|------------|-----------|
| Road | 1.00 | σ_road/σ_road = 29.9/29.9 | Relatively adjustable |
| Bridge | 0.65 | σ_road/σ_bridge = 29.9/46.2 | Moderate constraints |
| Tunnel | 0.48 | σ_road/σ_tunnel = 29.9/62.4 | High irreversibility after excavation |

**Source**: Flyvbjerg et al. (2003) cost overrun standard deviations, Eq.(4)

---

#### 5. Option to Switch-Out (O_swo) - 인력 전환 옵션

**Definition**: Reallocating key personnel to better opportunities (핵심 인력의 더 나은 기회로 재배치)

**BIM Project Interpretation**:
- Redirect resources to more attractive alternative projects
- Personnel mobility enables opportunity capture
- Low switching costs maximize value

**Activation Condition**: High Personnel Mobility (높은 인력 이동성)

---

### Category 3: Control Options (위험 통제)

#### 6. Option to Abandon (O_abn) - 포기 옵션

**Definition**: Terminating project to limit downside losses (프로젝트 중도 타절로 손실 제한)

**BIM Project Interpretation**:
- When bottom 5% NPV simulation exceeds loss threshold
- Terminate or pay penalty to exit contract
- Salvage remaining value and prevent further losses

**Activation Condition**: Bottom 5% NPV < Loss Limit (하위 5% NPV가 손실 임계치 초과)

**Theoretical Basis**: Triantis (2005)

**Salvage Rate (R_sal)**: Triangular(0.10, 0.30, 0.50) - 10-50% of invested costs
**Source**: Kodukula & Papudesu (2006)

---

#### 7. Option to Stage (O_stg) - 단계적 투자 옵션

**Definition**: Risk management through phased contracting (단계별 계약을 통한 리스크 관리)

**BIM Project Interpretation**:
- Execute project in stages rather than all at once
- Initial uncertainty resolved before subsequent investment
- Milestone checkpoints allow informed decisions

**Activation Condition**: Long Project Duration (장기 프로젝트)

**Design Review Count by Infrastructure Type (n)**:

| Type | Reviews | Components | Legal Basis |
|------|---------|------------|-------------|
| Road | 3 | VE×2 + General Review | MOLIT 2024 Art.75 |
| Bridge | 4 | VE×2 + Seismic + Structural | MOLIT 2024 Art.75, 98 |
| Tunnel | 4 | VE×2 + Special Method + Ground Safety | MOLIT 2024 Art.75-2 |

**Source**: Construction Technology Promotion Act (건설기술진흥법 시행령)

---

## The 3 Adjustment Factors

To prevent overvaluation of real options, three adjustment factors are applied:

### 1. Interaction Discount (I_int) - 상호작용 할인

**Definition**: Discount for overlapping benefits when multiple options coexist

Multiple options cannot be fully additive because exercising one may affect others. For example, capability accumulation (O_grw) may increase follow-on success probability (O_exp), creating overlap.

**Formula**:
```
I_int = ROV_gross × γ

Where:
  γ ∈ [0, 0.30] (Interaction Index)

  Active Options | γ (Discount Rate)
  -------------- | -----------------
  6-7 options    | 0.22 - 0.30
  4-5 options    | 0.15 - 0.22
  1-3 options    | 0.08 - 0.15
```

**Theoretical Basis**: Trigeorgis (1993)

---

### 2. Risk Premium (P_risk) - 리스크 프리미엄

**Definition**: Additional discount for non-tradable, irreversible risks

Unlike financial options, real options cannot be instantly traded in markets. Exercise involves organizational decision delays and technical friction.

**Formula**:
```
P_risk = ROV_adjusted × ρ

Where:
  ρ = Base_Premium + Volatility_Premium + Complexity_Premium

  Base_Premium = 0.15
  Volatility_Premium = σ × 0.30
  Complexity_Premium = κ × 0.10
```

**Theoretical Basis**: Borison (2005)

---

### 3. Deferral Cost (C_wait) - 연기 비용 (이연 비용)

**Definition**: Opportunity cost of not waiting (대기 옵션 포기의 기회비용)

This represents the cost of forgoing the "Option to Wait" by participating now. If strategic fit (S) is low or market alternatives (A) are more attractive, deferral cost increases.

**Formula**:
```
C_wait = f(Strategic_Alignment, Alternative_Attractiveness, Time_to_Decision)

C_wait = S × (1 - S_fit) × A × 0.18 × √T
```

**Design Purpose**: Prevents indiscriminate bidding participation

**Theoretical Basis**: Dixit & Pindyck (1994)

---

## Key Parameters by Infrastructure Type

### Base Complexity (κ₀)

Derived from Flyvbjerg et al. (2003) cost overrun data (20 countries, 258 projects):

| Type | Cost Overrun | Normalized κ₀ |
|------|--------------|---------------|
| Road | 20.4% | 0.60 (= 20.4/33.8) |
| Bridge | ~27% | 0.85 |
| Tunnel | 33.8% | 1.00 (reference) |

### Complexity Adjustment (Eq.3)

```
κ_adj = 1 + ε × (S/S_ref - 1)

Where:
  ε = 0.13 (scale-complexity elasticity, Bosch-Rekveldt et al. 2011)
  S_ref = 10 billion KRW (reference amount)
```

### Base Volatility (σ₀)

Annual volatility derived from Flyvbjerg et al. (2003) with design-stage adjustment:

```
σ₀ = ln(1 + μ_overrun) / √T_avg × α                ... Eq.(5)

Where:
  α = 1.86 (design stage adjustment factor, AACE 18R-97)
```

| Type | σ₀ | Source |
|------|-----|--------|
| Road | 0.22 | Flyvbjerg (2003), Eq.(5) |
| Bridge | 0.35 | Flyvbjerg (2003), Eq.(5) |
| Tunnel | 0.42 | Flyvbjerg (2003), Eq.(5) |

### Dynamic Volatility Adjustment (Eq.11)

```
σ = σ₀ × (1 + (κ - κ̄) / κ̄)

Where:
  κ = project complexity
  κ̄ = average complexity for infrastructure type
```

---

## Decision Framework

### TPV-Based Classification (Table 7 from Paper)

| Decision Signal | TPV Condition | Strategic Interpretation | Basis |
|-----------------|---------------|--------------------------|-------|
| **Strong Participate** | TPV > NPV×1.5 AND TPV > 300M | High strategic value, bid aggressively | KENCA 2024 top 10% |
| **Participate** | TPV > NPV×1.05 OR 100M < TPV ≤ 300M | Favorable opportunity, standard bid | Copeland & Antikarov 2001 |
| **Conditional** | TPV > NPV×0.80 OR 0 < TPV ≤ 100M | Marginal value, conditional bid | Estimation uncertainty |
| **Reject** | TPV ≤ NPV×0.80 OR TPV ≤ 0 | Opportunity cost exceeds value, conserve resources | Dixit & Pindyck 1994 |

### Basis for Criteria

- **1.5× threshold**: ROV > 50% of NPV indicates significant strategic premium (KENCA 2024 top 10% project size: 300M KRW)
- **1.05× threshold**: Exceeds typical estimation error of ±5-10% (Copeland & Antikarov 2001)
- **0.80× threshold**: Wait value exceeds bid value (Dixit & Pindyck 1994)

---

## Summary Table: Option Types

| Category | Option Type | Symbol | BIM Project Interpretation | Activation Condition |
|----------|-------------|--------|----------------------------|----------------------|
| Growth | Option to Expand | O_exp | Leveraging info. advantage for subsequent projects | Preliminary Design Phase |
| Growth | Growth Option | O_grw | Accumulating BIM capabilities and technical assets | High Project Complexity |
| Flexibility | Option to Switch (In) | O_swi | Utilizing idle manpower to prevent fixed cost loss | Low Resource Utilization |
| Flexibility | Option to Contract | O_cnt | Adjusting scope via consultation under cost overruns | High Physical Irreversibility |
| Flexibility | Option to Switch (Out) | O_swo | Reallocating key personnel to better opportunities | High Personnel Mobility |
| Control | Option to Abandon | O_abn | Terminating project to limit downside losses | Bottom 5% NPV < Limit |
| Control | Option to Stage | O_stg | Risk management through phased contracting | Long Project Duration |

---

## References

1. Trigeorgis, L. (1993). The nature of option interactions and the valuation of investments with multiple real options. Journal of Financial and Quantitative Analysis, 28(1), 1-20.
2. Trigeorgis, L. (1996). Real options: Managerial flexibility and strategy in resource allocation. MIT Press.
3. Dixit, A. K., & Pindyck, R. S. (1994). Investment under Uncertainty. Princeton University Press.
4. Copeland, T., & Antikarov, V. (2001). Real options: A practitioner's guide. Texere LLC.
5. Borison, A. (2005). Real Options Analysis: Where Are the Emperor's Clothes? Journal of Applied Corporate Finance.
6. Argote, L., & Epple, D. (1990). Learning Curves in Manufacturing. Science.
7. Geske, R. (1979). The Valuation of Compound Options. Journal of Financial Economics.
8. Myers, S. C. (1977). Determinants of corporate borrowing. Journal of Financial Economics.
9. Flyvbjerg, B., Skamris Holm, M. K., & Buhl, S. L. (2003). How common and how large are cost overruns in transport infrastructure projects? Transport Reviews.
10. Triantis, A. (2005). Realizing the Potential of Real Options. Journal of Applied Corporate Finance.
11. Jofre-Bonet, M., & Pesendorfer, M. (2003). Estimation of a dynamic auction game. Econometrica.
12. Kodukula, P., & Papudesu, C. (2006). Project valuation using real options: A practitioner's guide. J. Ross Publishing.
13. Lee, S., & Yu, J. (2020). Longitudinal study of BIM acceptance in the Korean AEC industry. Applied Sciences.
14. Bosch-Rekveldt, M. et al. (2011). Grasping project complexity in large engineering projects. International Journal of Project Management.
15. AACE International. (2020). Cost Estimate Classification System (18R-97).
16. KENCA. (2023). Engineering Service Industry Survey. Korea Engineering & Consulting Association.
17. MOTIE. (2024). Engineering Service Fee Standards. Ministry of Trade, Industry and Energy.
18. NABO. (2009). Engineering Service Procurement Analysis. National Assembly Budget Office.
