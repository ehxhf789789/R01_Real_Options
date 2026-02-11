# Model Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      BIM ROV Valuation System                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐   │
│   │   CSV Input │───▶│ Tier System │───▶│  Valuation Engine   │   │
│   │   (Tier 0)  │    │  (Tier 1-2) │    │  (Monte Carlo)      │   │
│   └─────────────┘    └─────────────┘    └──────────┬──────────┘   │
│                                                     │              │
│                                                     ▼              │
│                                         ┌─────────────────────┐   │
│                                         │   Results & Viz     │   │
│                                         │   (Figures, CSV)    │   │
│                                         └─────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
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
- `n_simulations`: Number of Monte Carlo iterations (default: 5,000)
- `fixed_params`: Model parameters (discount rates, option parameters, caps)

### 2. Tier System (`src/tier_system.py`)

Manages the 3-tier input transformation.

```python
@dataclass
class Tier0Input:
    # 10 deterministic input variables

class Tier1Derivation:
    @staticmethod
    def derive(tier0: Tier0Input) -> Dict

class Tier2Sampler:
    @classmethod
    def sample(tier1: Dict) -> Dict
```

---

## ROV Calculation Flow

```
                    ┌───────────────────────────────────┐
                    │         7 Option Values           │
                    │  ┌─────────────────────────────┐  │
                    │  │ + Follow-on      + Contract │  │
                    │  │ + Capability     + Switch   │  │
                    │  │ + Resource       + Staging  │  │
                    │  │ + Abandonment               │  │
                    │  └─────────────────────────────┘  │
                    │              = ROV Gross          │
                    └───────────────┬───────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────────┐
                    │      - Interaction Discount       │
                    │        (8-22% based on count)     │
                    └───────────────┬───────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────────┐
                    │         = ROV Adjusted            │
                    └───────────────┬───────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────────┐
                    │      - Risk Premium               │
                    │      - Deferral Cost              │
                    └───────────────┬───────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────────┐
                    │    Apply Cap: ROV ≤ 0.80×|NPV|    │
                    └───────────────┬───────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────────┐
                    │           = ROV Net               │
                    └───────────────────────────────────┘
```

---

## Option Calculation Details

### 1. Follow-on Option

```python
# Compound option structure (Geske 1979)
if condition1 and condition2 and condition3:  # All must be true
    intrinsic_value = (S2 - K2) - strategic_penalty
    time_decay = exp(-rf * time_to_decision)
    rov_follow = intrinsic_value * time_decay * realization_rate * competition_discount
```

### 2. Capability Option

```python
if capability_level < 0.60:
    # Unskilled: learning cost > learning benefit
    learning_cost = contract * complexity * (0.60 - capability) * 0.20
    learning_benefit = contract * complexity * capability * 0.10
    rov_capability = learning_benefit - learning_cost  # Can be negative
else:
    # Skilled: diminishing returns
    learning_diminishing = 1 - (capability ** 1.5)
    rov_capability = contract * complexity * growth_rate * learning_diminishing
```

### 3. Resource Option

```python
if resource_utilization > 0.80:
    # Overloaded: opportunity cost
    overload_cost = (utilization - 0.80) * contract * 0.15
    idle_benefit = contract * (1 - utilization) * 0.06
    rov_resource = idle_benefit - overload_cost  # Can be negative
else:
    # Normal utilization
    rov_resource = contract * (1 - utilization) * premium * complexity
```

---

## Decision Framework

### Decision Categories

| Decision | Condition | Interpretation |
|----------|-----------|----------------|
| **Strong Participate** | TPV > NPV×1.5 AND TPV > 30M | High confidence bid |
| **Participate** | NPV×1.05 < TPV ≤ NPV×1.5 | Standard bid |
| **Conditional** | NPV×0.80 < TPV ≤ NPV×1.05 | Careful evaluation needed |
| **Reject** | TPV ≤ NPV×0.80 OR TPV ≤ 0 | Do not bid |

### Decision Change Detection

```python
# Detects when ROV changes the NPV-based decision
if npv < 0 and tpv > 0:
    direction = "Up"    # Reject → Participate
elif npv > 0 and tpv < 0:
    direction = "Down"  # Participate → Reject
else:
    direction = "No Change"
```

---

## Fixed Parameters

```python
fixed_params = {
    # Discount rates
    'risk_free_rate': 0.035,
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
    'interaction_discount': 0.18,
    'risk_premium_rate': 0.25,
    'deferral_multiplier': 0.08,

    # Cap (Trigeorgis 1996)
    'rov_cap_ratio': 0.80,  # ROV ≤ 0.80 × |NPV|
}
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
| `rov_follow_on` | Mean follow-on option value |
| `rov_capability` | Mean capability option value |
| ... | (other option components) |
| `prob_strong_participate` | Probability of Strong Participate |
| `prob_participate` | Probability of Participate |
| `prob_conditional` | Probability of Conditional |
| `prob_reject` | Probability of Reject |
| `tpv_decision` | Most likely decision |
| `decision_changed` | Whether ROV changed the decision |
| `decision_direction` | Direction of change (Up/Down/No Change) |

---

## File Dependencies

```
src/
├── __init__.py              # Package exports
├── valuation_engine.py      # Main engine (imports tier_system)
└── tier_system.py           # Input transformation (standalone)

data/
└── sample_projects.csv      # Input data

scripts/
└── generate_figures.py      # Visualization (imports valuation_engine)
```
