# Model Architecture

## System Overview (BIM-ROVS)

The BIM Real Options Valuation System (BIM-ROVS) is a Python-based standalone decision support system for engineering firms' bid/no-bid decisions.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BIM-ROVS Decision Support System                      │
│                    (Figure 2 from Paper: Process Flow)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Step 1-2: USER INPUT                                                       │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  CSV Template (7 variables from tender documents)                    │   │
│   │  + Company characteristics (4 variables)                            │   │
│   └──────────────────────────┬──────────────────────────────────────────┘   │
│                              │                                               │
│                              ▼                                               │
│   Step 3: PARAMETER MAPPING (Rule-based Engine)                             │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Tier0Input → Tier1Derivation → 12 derived parameters               │   │
│   └──────────────────────────┬──────────────────────────────────────────┘   │
│                              │                                               │
│                              ▼                                               │
│   Step 4: PROBABILISTIC MODELING                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  13 probability distributions → 5,000 random sample sets            │   │
│   └──────────────────────────┬──────────────────────────────────────────┘   │
│                              │                                               │
│                              ▼                                               │
│   Step 5: MONTE CARLO SIMULATION                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  NPV calculation + 7 Options + 3 Adjustments → TPV distribution     │   │
│   └──────────────────────────┬──────────────────────────────────────────┘   │
│                              │                                               │
│                              ▼                                               │
│   Step 6-7: DASHBOARD & DECISION                                            │
│   ┌─────────────────────────────────────────────────────────────────────┐   │
│   │  Visualization + Decision Signal + Quantitative Justification       │   │
│   └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. ValuationEngine (`src/valuation_engine.py`)

The main orchestrator class that runs the complete valuation process.

```python
class ValuationEngine:
    def __init__(self, n_simulations: int = 5000)
    def run_valuation(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]
    def _monte_carlo_simulation(tier0, tier1) -> Dict
    def _calculate_all_options(contract, tier1, tier2) -> Dict
```

**Key Parameters**:
- `n_simulations`: Number of Monte Carlo iterations (default: 5,000, range: 1,000-20,000)
- `fixed_params`: Model parameters from literature (discount rates, option parameters, caps)

### 2. Tier System (`src/tier_system.py`)

Manages the input transformation hierarchy.

```python
@dataclass
class Tier0Input:
    # 6 tender document variables + 4 company variables = 10 total

class Tier1Derivation:
    @staticmethod
    def derive(tier0: Tier0Input) -> Dict  # Rule-based parameter derivation

class Tier2Sampler:
    @classmethod
    def sample(tier1: Dict) -> Dict  # Probabilistic sampling
```

---

## ROV Calculation Flow (Eq.2 from Paper)

```
                    ┌───────────────────────────────────────┐
                    │         7 Option Values (Gross)       │
                    │  ┌─────────────────────────────────┐  │
                    │  │ O_exp: Follow-on (Geske 1979)   │  │
                    │  │ O_grw: Capability (Wright 1936) │  │
                    │  │ O_swi: Resource utilization     │  │
                    │  │ O_cnt: Contract flexibility     │  │
                    │  │ O_swo: Personnel switch         │  │
                    │  │ O_abn: Abandonment (Triantis)   │  │
                    │  │ O_stg: Staging (Sequential)     │  │
                    │  └─────────────────────────────────┘  │
                    │           = ROV Gross                 │
                    └───────────────────┬───────────────────┘
                                        │
                                        ▼
                    ┌───────────────────────────────────────┐
                    │  - Interaction Discount (I_int)       │
                    │    γ ∈ [0.08, 0.30] based on count    │
                    │    (Trigeorgis 1993)                  │
                    └───────────────────┬───────────────────┘
                                        │
                                        ▼
                    ┌───────────────────────────────────────┐
                    │         = ROV Adjusted                │
                    └───────────────────┬───────────────────┘
                                        │
                                        ▼
                    ┌───────────────────────────────────────┐
                    │  - Risk Premium (P_risk)              │
                    │    ρ = 0.15 + σ×0.30 + κ×0.10        │
                    │    (Borison 2005)                     │
                    │                                       │
                    │  - Deferral Cost (C_wait)             │
                    │    (Dixit & Pindyck 1994)             │
                    └───────────────────┬───────────────────┘
                                        │
                                        ▼
                    ┌───────────────────────────────────────┐
                    │    Apply Cap: ROV ≤ 0.80 × |NPV|      │
                    │    (Trigeorgis 1996)                  │
                    └───────────────────┬───────────────────┘
                                        │
                                        ▼
                    ┌───────────────────────────────────────┐
                    │           = ROV Net                   │
                    └───────────────────────────────────────┘
```

---

## Option Calculation Details

### 1. Follow-on Option (O_exp) - Compound Option

Based on Geske (1979) compound option theory:

```python
# Activation: Basic Design phase only
if has_follow_on and follow_on_prob > 0:
    # Stage 1: Basic design NPV
    npv_stage1 = contract * (1 - cost_ratio)

    # Stage 2: Expected detailed design value
    S2 = contract * follow_on_multiplier * follow_on_prob  # Road: 1.67, Bridge/Tunnel: 1.84
    K2 = contract * follow_on_multiplier * cost_ratio

    # Compound option exercise conditions (all 3 must be true)
    condition1 = npv_stage1 > 0
    condition2 = follow_on_prob > 0.5  # Beta(3.2, 2.3), mean ≈ 0.58
    condition3 = strategic_alignment > 0.4

    if all conditions:
        intrinsic_value = S2 - K2 - strategic_penalty
        time_decay = exp(-r_f * time_to_decision)

        # Infra-type realization rates (based on separate bidding rates)
        realization_rate = {'Road': 0.25, 'Bridge': 0.42, 'Tunnel': 0.55}

        rov_follow = intrinsic_value * time_decay * realization_rate * competition_discount
```

### 2. Capability Option (O_grw) - Learning Curve

Based on Argote & Epple (1990) and Wright (1936):

```python
bim_threshold = 0.60  # Minimum expertise for positive learning effect

if capability_level < bim_threshold:
    # Unskilled: learning cost > learning benefit → can be negative
    learning_cost = contract * complexity * (0.60 - capability) * 0.20
    learning_benefit = contract * complexity * capability * 0.10
    rov_capability = learning_benefit - learning_cost
else:
    # Skilled: diminishing returns (Argote & Epple 1990)
    learning_diminishing = 1 - (capability ** 1.5)
    rov_capability = contract * complexity * growth_rate * learning_diminishing
```

### 3. Resource Option (O_swi) - Fixed Cost Avoidance

```python
if resource_utilization > 0.80:
    # Overloaded: opportunity cost dominates
    overload_cost = (utilization - 0.80) * contract * 0.15
    idle_benefit = contract * (1 - utilization) * 0.06
    rov_resource = idle_benefit - overload_cost  # Can be negative
else:
    # Normal utilization: idle resource value
    rov_resource = contract * (1 - utilization) * premium * complexity
```

### 4. Contract Flexibility Option (O_cnt)

```python
# Design flexibility by infra type (Flyvbjerg 2003, Eq.4)
scope_flex = {'Road': 1.00, 'Bridge': 0.65, 'Tunnel': 0.48}

adverse_prob = max(0, cost_ratio - 0.85) * 2  # Probability of adverse scenario
rov_contract = contract * scope_flex * adverse_prob * flexibility_rate
```

### 5. Abandonment Option (O_abn)

Based on Triantis (2005):

```python
if npv > 0:
    # Profitable project: abandonment is a loss
    rov_abandonment = -contract * 0.02
elif npv < contract * 0.15 or strategic_alignment < 0.30:
    # Distressed project: abandonment has value
    completion_ratio = 0.45  # Average 45% completion before abandonment
    salvage = contract * completion_ratio * 0.80  # 80% payment recognition
    reallocation_value = contract * (1 - completion_ratio) * utilization * 0.50
    rov_abandonment = max(salvage + reallocation_value - contract * completion_ratio, 0)
```

---

## Fixed Parameters (Literature-Based)

```python
fixed_params = {
    # Discount rates (Smith & Nau 1995, BOK 2024)
    'risk_free_rate': 0.035,  # 10-year bond 3.0% + AAA spread 0.5%
    'discount_rate': 0.09,
    'time_steps': 12,

    # Option exercise parameters
    'follow_on_exercise_rate': 0.50,
    'capability_growth_rate': 0.10,
    'resource_utilization_premium': 0.06,
    'contract_flexibility_rate': 0.05,
    'switch_mobility_rate': 0.04,
    'stage_checkpoint_value': 0.03,

    # Adjustment parameters
    'interaction_discount': 0.18,      # Range: 0.08-0.30 (Trigeorgis 1993)
    'risk_premium_rate': 0.25,          # 0.15 + σ×0.30 + κ×0.10 (Borison 2005)
    'deferral_multiplier': 0.08,        # (Dixit & Pindyck 1994)

    # Cap (Trigeorgis 1996)
    'rov_cap_ratio': 0.80,  # ROV ≤ 0.80 × |NPV|
}
```

---

## Infrastructure-Type Specific Parameters

### From Flyvbjerg et al. (2003)

| Parameter | Road | Bridge | Tunnel | Source |
|-----------|------|--------|--------|--------|
| Base Complexity (κ₀) | 0.60 | 0.85 | 1.00 | Cost overrun normalization |
| Design Flexibility (f_scope) | 1.00 | 0.65 | 0.48 | Eq.(4) from std dev |
| Base Volatility (σ₀) | 0.22 | 0.35 | 0.42 | Eq.(5) with α=1.86 |
| Design Reviews (n) | 3 | 4 | 4 | MOLIT (2024) |
| Value Multiplier (m_f) | 1.67 | 1.84 | 1.84 | MOTIE (2024) |

### From KENCA (2023)

| Parameter | Open | Limited | Nominated |
|-----------|------|---------|-----------|
| Competition Mean (μ_c) | 0.72 | 0.48 | 0.21 |
| Competition SD (σ_c) | 0.14 | 0.10 | 0.04 |

| Client Type | Reliability (φ_c) |
|-------------|-------------------|
| Central | 0.92 |
| Public Corp | 0.88 |
| Local | 0.81 |

---

## Decision Framework (Table 7 from Paper)

### Decision Categories

| Decision | Condition | Interpretation | Basis |
|----------|-----------|----------------|-------|
| **Strong Participate** | TPV > NPV×1.5 AND TPV > 300M | High confidence bid | KENCA 2024 top 10% |
| **Participate** | NPV×1.05 < TPV ≤ NPV×1.5 | Standard bid | Copeland & Antikarov 2001 |
| **Conditional** | NPV×0.80 < TPV ≤ NPV×1.05 | Careful evaluation needed | Estimation error |
| **Reject** | TPV ≤ NPV×0.80 OR TPV ≤ 0 | Do not bid | Dixit & Pindyck 1994 |

### Decision Change Detection

```python
# Detects when ROV changes the NPV-based decision
if npv < 0 and tpv > 0:
    direction = "Up"    # Reject → Participate (strategic value recognized)
elif npv > 0 and tpv < 0:
    direction = "Down"  # Participate → Reject (hidden risks identified)
else:
    direction = "No Change"
```

---

## Output Structure

### Per-Project Results

| Field | Description |
|-------|-------------|
| `npv` | Mean NPV from simulation |
| `npv_std` | NPV standard deviation |
| `tpv` | Mean TPV from simulation |
| `tpv_std` | TPV standard deviation |
| `tpv_ci_lower` | 5th percentile TPV |
| `tpv_ci_upper` | 95th percentile TPV |
| `rov_net` | Mean net ROV |
| `rov_follow_on` | Mean follow-on option value (O_exp) |
| `rov_capability` | Mean capability option value (O_grw) |
| `rov_resource` | Mean resource option value (O_swi) |
| `rov_contract` | Mean contract option value (O_cnt) |
| `rov_switch` | Mean switch option value (O_swo) |
| `rov_abandonment` | Mean abandonment option value (O_abn) |
| `rov_stage` | Mean staging option value (O_stg) |
| `interaction_adjustment` | Interaction discount (I_int) |
| `risk_premium` | Risk premium (P_risk) |
| `deferral_value` | Deferral cost (C_wait) |
| `prob_strong_participate` | Probability of Strong Participate |
| `prob_participate` | Probability of Participate |
| `prob_conditional` | Probability of Conditional |
| `prob_reject` | Probability of Reject |
| `tpv_decision` | Most likely decision |
| `decision_changed` | Whether ROV changed the decision |
| `decision_direction` | Direction of change (Up/Down/No Change) |

---

## Visualization Components (Figure 3 from Paper)

### Dashboard Layout

1. **Control Panel (Left)**
   - Data load button
   - Simulation execution
   - Iteration count slider (1,000-20,000)
   - Portfolio summary (NPV/ROV/TPV totals)

2. **Analysis Dashboard (Right)**
   - NPV vs TPV comparison chart (Figure 4)
   - ROV Waterfall chart (Figure 5)
   - Sensitivity Tornado diagram (Figure 6)

---

## File Dependencies

```
src/
├── __init__.py              # Package exports
├── valuation_engine.py      # Main engine (Level 4-5)
└── tier_system.py           # Input transformation (Level 1-3)

data/
└── sample_projects.csv      # Input data (Table 9 format)

scripts/
└── generate_figures.py      # Visualization (Figures 4-6)
```
