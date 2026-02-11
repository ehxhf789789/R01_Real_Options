# 5-Level Hierarchical Input System

## Overview

The BIM-ROVS model uses a 5-Level hierarchical framework that transforms raw tender document information into probabilistic parameters suitable for Monte Carlo simulation. This design minimizes input burden while ensuring statistical reliability by systematically managing input data uncertainty.

```
Level 1       Level 2          Level 3            Level 4           Level 5
Data Input → Parameter    →  Probabilistic  →  Value          →  Decision
             Mapping          Modeling          Evaluation        Making
```

---

## System Architecture (Figure 1 from Paper)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    5-Level Hierarchical Framework                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Level 1: DATA INPUT (확정 정보)                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Tender Documents (6):                                                   │ │
│  │   S (Contract Amount), I (Infra Type), D (Design Phase),               │ │
│  │   T (Duration), P (Procurement Type), C (Client Type)                  │ │
│  │                                                                         │ │
│  │ Company Characteristics (4):                                            │ │
│  │   Firm Size, BIM Years, Same-type Count, Current Utilization           │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    ↓                                         │
│  Level 2: PARAMETER MAPPING (수치 파라미터 변환)                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Rule-based derivation from literature & statistics:                     │ │
│  │   κ₀ (Base Complexity), f_scope (Design Flexibility),                  │ │
│  │   σ₀ (Base Volatility), n (Review Count), m_f (Value Multiplier),      │ │
│  │   μ_c/σ_c (Competition), φ_c (Client Reliability), etc.                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    ↓                                         │
│  Level 3: PROBABILISTIC MODELING (확률 모형화)                               │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Distribution Assignment (Vose 2008 criteria):                           │ │
│  │   Beta: p_f (Follow-on Prob), L (BIM Expertise)                        │ │
│  │   Triangular: C (Cost Ratio), S (Strategic Fit), A (Market), R_sal     │ │
│  │   Uniform: m_f (Multiplier), R_idle, γ (Interaction)                   │ │
│  │   Normal: κ (Complexity), c (Competition)                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    ↓                                         │
│  Level 4: VALUE EVALUATION (가치 평가)                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Monte Carlo Simulation (5,000 iterations):                              │ │
│  │   NPV = S × (1 - C_adj)                                                │ │
│  │   ROV = Σ(7 Options) - Σ(3 Adjustments)                                │ │
│  │   TPV = NPV + ROV                                                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                    ↓                                         │
│  Level 5: DECISION (의사결정)                                                │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Decision Signals: Strong Participate / Participate / Conditional / Reject │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Level 1: Data Input (Deterministic)

Level 1 contains confirmed information that can be directly extracted from tender documents and company records.

### Tender Document Variables (6) - Table 8 from Paper

| Variable | Symbol | Description | Format | Valid Values |
|----------|--------|-------------|--------|--------------|
| Contract Amount | S | Total contract value | Numeric (Million KRW) | Positive number |
| Infrastructure Type | I | Project infrastructure type | String | "Road", "Bridge", "Tunnel" |
| Design Phase | D | Current design phase | String | "Basic Design", "Detailed Design" |
| Procurement Type | P | Bidding method | String | "Open", "Limited", "Nominated" |
| Client Type | C | Client organization type | String | "Central", "Local", "Public Corp" |
| Contract Duration | T | Contract period | Numeric (Years) | Positive float |

### Company Characteristic Variables (4)

| Variable | Description | Type | Example |
|----------|-------------|------|---------|
| Firm Size | Company size category | String | "Large", "Medium", "Small" |
| BIM Years | Years of BIM experience | Integer | 5 |
| Same-type Count | Similar projects in last 5 years | Integer | 8 |
| Current Utilization | Current resource utilization rate | Float (0-1) | 0.65 |

### Key Design Principle: Objectification

To prevent optimism bias (Flyvbjerg et al. 2003), the model restricts user input to objectively verifiable information from tender documents, rather than subjective estimates like profit margins or win probabilities.

---

## Level 2: Parameter Mapping (Derived)

Level 2 parameters are deterministically derived from Level 1 inputs using predefined rules based on literature and statistics.

### Tender Document-Based Parameters (Table 2 from Paper)

| Input Variable | Derived Parameter | Value or Formula | Source |
|----------------|-------------------|------------------|--------|
| Contract Amount (S) | Complexity Adjustment (κ_adj) | 1 + 0.13 × (S/100 - 1) | Bosch-Rekveldt et al. (2011) |
| Infrastructure Type (I) | Base Complexity (κ₀) | Road: 0.60, Bridge: 0.85, Tunnel: 1.00 | Flyvbjerg et al. (2003) |
| Infrastructure Type (I) | Design Flexibility (f_scope) | Road: 1.00, Bridge: 0.65, Tunnel: 0.48 | Flyvbjerg et al. (2003), Eq.(4) |
| Infrastructure Type (I) | Base Volatility (σ₀) | Road: 0.22, Bridge: 0.35, Tunnel: 0.42 | Flyvbjerg et al. (2003), Eq.(5) |
| Infrastructure Type (I) | Design Review Count (n) | Road: 3, Bridge: 4, Tunnel: 4 | MOLIT (2024) |
| Design Phase (D) | Follow-on Flag (F) | Basic: True, Detailed: False | - |
| Design Phase (D) | Beta Parameters (α, β) | (3.2, 2.3) | Jofre-Bonet & Pesendorfer (2003) |
| Design Phase (D) | Value Multiplier (m_f) | Road: 1.67, Bridge/Tunnel: 1.84 | MOTIE (2024) |
| Design Phase (D) | Multiplier Range | [m_f × 0.85, m_f × 1.15] | NABO (2009) |
| Procurement Type (P) | Competition Mean (μ_c) | Open: 0.72, Limited: 0.48, Nominated: 0.21 | KENCA (2023) |
| Procurement Type (P) | Competition SD (σ_c) | Open: 0.14, Limited: 0.10, Nominated: 0.04 | Beak et al. (2015) |
| Client Type (C) | Client Reliability (φ_c) | Central: 0.92, Public Corp: 0.88, Local: 0.81 | KENCA (2023) |
| Contract Duration (T) | Risk-free Rate (r_f) | 3.5% | Smith & Nau (1995), BOK (2024) |

### Company Characteristic-Based Parameters (Table 4 from Paper)

| Input Variable | Derived Parameter | Derivation Rule | Source |
|----------------|-------------------|-----------------|--------|
| Firm Size | Cost Ratio Base (C₀) | Large: 0.87, Medium: 0.92, Small: 0.97 | KENCA (2023) |
| BIM Years | BIM Expertise (L) | L = ln(1+Y) / ln(11), Y_sat=10 | Wright (1936), Lee & Yu (2020) |
| Same-type Count | Strategic Fit (S) | S = 0.40 + 0.55 × min(N,10)/10 | - |
| Current Utilization | Idle Resource Ratio (R_idle) | R_idle = 1 - U_current | - |

### External Factor-Based Parameters

| Parameter | Value | Source |
|-----------|-------|--------|
| Market Attractiveness (A) | 0.55 (normalized from CBSI 72.2) | CERIK (2025), KDI (2025) |

### Model Internal Parameters

| Parameter | Distribution | Range | Source |
|-----------|--------------|-------|--------|
| Interaction Discount (γ) | Uniform | [0, 0.30] | Trigeorgis (1993) |
| Salvage Rate (R_sal) | Triangular | (0.10, 0.30, 0.50) | Kodukula & Papudesu (2006) |

---

## Level 3: Probabilistic Modeling

Level 3 parameters are sampled from probability distributions, with distribution parameters influenced by Level 2 values.

### Distribution Selection Criteria (Vose 2008)

1. **Domain Constraint**: Bounded (0-1) vs unbounded variables require different distributions
2. **Available Information**: Mean/variance, min/mode/max, or range only
3. **Theoretical Justification**: Central limit theorem for multi-factor composites

### Distribution Specifications (Table 5 from Paper)

| Type | Variable | Symbol | Distribution | Derivation Rule | Source |
|------|----------|--------|--------------|-----------------|--------|
| Bounded Probability | Follow-on Probability | p_f | Beta | (α, β) = (3.2, 2.3) | Jofre-Bonet & Pesendorfer (2003) |
| Bounded Probability | BIM Expertise | L | Beta | Eq.(10) from μ, σ² | Lee & Yu (2020) |
| Range-Constrained | Cost Ratio | C | Triangular | (0.80, C₀, 0.98) | KENCA (2023) |
| Range-Constrained | Strategic Fit | S | Triangular | (S₀ ± 0.15) | - |
| Range-Constrained | Market Attractiveness | A | Triangular | (0.35, 0.55, 0.75) | CERIK (2025), KDI (2025) |
| Range-Constrained | Salvage Rate | R_sal | Triangular | (0.10, 0.30, 0.50) | Kodukula & Papudesu (2006) |
| Range-Only | Value Multiplier | m_f | Uniform | [m_f,min, m_f,max] | MOTIE (2024), NABO (2009) |
| Range-Only | Idle Resource Ratio | R_idle | Uniform | [R_idle ± 0.15] | Maximum Entropy |
| Range-Only | Interaction Discount | γ | Uniform | [0, 0.30] | Trigeorgis (1993) |
| Multi-Factor Composite | Complexity | κ | Normal | (μ_κ, σ_κ) | Central Limit Theorem |
| Multi-Factor Composite | Competition Intensity | c | Truncated Normal | (μ_c, σ_c, 0, 1) | KENCA (2023) |
| Dynamic Adjustment | Volatility | σ | Normal | Eq.(11), σ_adj = 0.18×σ₀ | Flyvbjerg et al. (2003) |

### Dynamic Volatility Adjustment (Eq.11)

```python
σ = σ₀ × (1 + (κ - κ̄) / κ̄)

# Volatility increases when complexity exceeds average for that infra type
# Additional uncertainty: Normal(0, 0.18 × σ₀)
```

---

## Level 4: Monte Carlo Simulation

### Simulation Process

```python
for iteration in range(5000):
    # Sample all Level 3 parameters from distributions
    params = sample_level3_parameters(level2)

    # Calculate NPV (Eq.12)
    npv = contract * (1 - params['cost_ratio'])

    # Calculate 7 option values
    rov_options = calculate_seven_options(contract, level2, params)

    # Apply 3 adjustments
    rov_net = apply_adjustments(rov_options, params)

    # Apply ROV cap (Trigeorgis 1996): ROV ≤ 0.80 × |NPV|
    rov_net = min(rov_net, abs(npv) * 0.80)

    # Calculate TPV (Eq.1)
    tpv = npv + rov_net

    results.append(tpv)

# Output: TPV distribution with statistics
```

### Convergence Validation

- Iterations tested: 1,000 ~ 20,000
- Convergence criterion: Coefficient of Variation (CV) < 1%
- Result: 5,000 iterations achieve statistical stability

---

## Level 5: Decision Classification

### Decision Signal Framework (Table 7 from Paper)

| Decision Signal | TPV Condition | Strategic Interpretation | Basis |
|-----------------|---------------|--------------------------|-------|
| **Strong Participate** | TPV > NPV×1.5 AND TPV > 300M | High strategic value, bid aggressively | KENCA (2024) top 10% |
| **Participate** | TPV > NPV×1.05 OR 100M < TPV ≤ 300M | Favorable opportunity, standard bid | Copeland & Antikarov (2001) |
| **Conditional** | TPV > NPV×0.80 OR 0 < TPV ≤ 100M | Marginal value, conditional bid | Estimation uncertainty |
| **Reject** | TPV ≤ NPV×0.80 OR TPV ≤ 0 | Opportunity cost exceeds value | Dixit & Pindyck (1994) |

---

## Implementation Mapping

The conceptual 5-Level framework is implemented in code as a 3-Tier system for practical purposes:

| Conceptual Level | Implementation | Code Location |
|------------------|----------------|---------------|
| Level 1: Data Input | Tier0Input | `tier_system.py` |
| Level 2: Parameter Mapping | Tier1Derivation | `tier_system.py` |
| Level 3: Probabilistic Modeling | Tier2Sampler | `tier_system.py` |
| Level 4: Value Evaluation | ValuationEngine | `valuation_engine.py` |
| Level 5: Decision | Decision Logic | `valuation_engine.py` |

---

## Code Reference

- **Tier0Input**: `src/tier_system.py` - Dataclass for Level 1 inputs
- **Tier1Derivation**: `src/tier_system.py` - Level 2 derivation rules
- **Tier2Sampler**: `src/tier_system.py` - Level 3 probability sampling
- **ValuationEngine**: `src/valuation_engine.py` - Level 4-5 evaluation & decision
