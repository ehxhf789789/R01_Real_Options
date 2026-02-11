# 3-Tier Input System

## Overview

The 3-Tier Input System is a hierarchical approach to managing input data uncertainty in real options valuation. It transforms raw tender document information into probabilistic parameters suitable for Monte Carlo simulation.

```
Tier 0 (Deterministic) → Tier 1 (Derived) → Tier 2 (Probabilistic)
   Raw confirmed data      Rule-based          Random
   from tender docs        derivation          sampling
```

---

## Tier 0: Deterministic Inputs

Tier 0 contains confirmed information that can be directly extracted from tender documents and company records.

### Tender Document Variables (6)

| Variable | Description | Type | Example |
|----------|-------------|------|---------|
| `project_id` | Unique project identifier | string | "R01" |
| `contract_amount` | Contract value in million KRW | float | 520.0 |
| `infra_type` | Infrastructure type | string | "Road", "Bridge", "Tunnel" |
| `design_phase` | Design phase | string | "Basic Design", "Detail Design" |
| `contract_duration` | Contract period in years | float | 1.5 |
| `procurement_type` | Procurement method | string | "Open", "Limited", "Negotiated" |
| `client_type` | Client organization type | string | "Central", "Local", "Public Corp" |

### Company Variables (4)

| Variable | Description | Type | Example |
|----------|-------------|------|---------|
| `firm_size` | Company size category | string | "Large", "Medium", "Small" |
| `bim_years` | Years of BIM experience | int | 5 |
| `same_type_count` | Similar projects in last 5 years | int | 8 |
| `current_utilization` | Current resource utilization rate | float | 0.65 |

---

## Tier 1: Derived Parameters

Tier 1 parameters are deterministically derived from Tier 0 inputs using predefined rules.

### Key Derivation Rules

#### 1. Follow-on Existence
```python
has_follow_on = (design_phase in ["기본설계", "Basic Design"])
```
Only basic design projects have follow-on opportunities.

#### 2. Project Complexity
```python
complexity_base = {
    'Tunnel': 'high',
    'Bridge': 'medium',
    'Road': 'low'
}

# Adjust for contract size
if contract_amount >= 300:
    complexity = upgrade_one_level(complexity_base)
```

#### 3. Competition Parameters
```python
competition_params = {
    'Open': {'mean': 0.6, 'std': 0.15},       # High competition
    'Limited': {'mean': 0.4, 'std': 0.10},    # Medium competition
    'Negotiated': {'mean': 0.2, 'std': 0.05}  # Low competition
}
```

#### 4. Cost Ratio Base (by Firm Size)
```python
cost_ratio_base = {
    'Large': 0.87,   # 13.2% profit margin
    'Medium': 0.92,  # 7.8% profit margin
    'Small': 0.97    # 2.9% profit margin
}
```
Based on KENCA (Korea Engineering & Consulting Association) 2023 statistics.

#### 5. BIM Expertise (Learning Curve)
```python
if bim_years >= 10:
    bim_expertise = 1.0
else:
    bim_expertise = log(1 + bim_years) / log(11)
```
Logarithmic learning curve saturating at 10 years.

#### 6. Strategic Fit
```python
N = same_type_count
N_ref = 10
strategic_fit = 0.40 + 0.55 * min(N, N_ref) / N_ref
```
Range: 0.40 (no experience) to 0.95 (10+ similar projects)

---

## Tier 2: Probabilistic Sampling

Tier 2 parameters are sampled from probability distributions, with distribution parameters influenced by Tier 1 values.

### Distribution Specifications

| Parameter | Distribution | Base Parameters | Adjustments |
|-----------|--------------|-----------------|-------------|
| `cost_ratio` | Triangular | mode = cost_ratio_base | +competition, +design_phase |
| `follow_on_prob` | Beta | Basic: (4,2), Detail: (1.5,4) | - |
| `strategic_alignment` | Uniform → Adjusted | center = strategic_fit | ±10% variation |
| `volatility` | Log-normal | mean=0.22, sigma=0.05 | - |
| `capability_level` | Uniform → Adjusted | center = bim_expertise | ±5% variation |
| `resource_utilization` | Uniform → Adjusted | center = 1 - idle_ratio | ±5% variation |
| `competition_level` | Normal | from competition_params | clipped [0, 1] |
| `complexity` | Normal | from complexity_base | std = 0.1 |

### Monte Carlo Sampling Process

```python
for iteration in range(5000):
    # Sample all Tier 2 parameters
    tier2 = Tier2Sampler.sample(tier1)

    # Calculate NPV
    npv = contract * (1 - tier2['cost_ratio'])

    # Calculate 7 option values
    rov_components = calculate_all_options(tier1, tier2)

    # Apply adjustments
    rov_net = apply_adjustments(rov_components)

    # Calculate TPV
    tpv = npv + rov_net

    # Store results
    results.append(tpv)
```

---

## Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         TIER 0                                  │
│                    (Deterministic)                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Tender Docs: contract_amount, infra_type, design_phase, │   │
│  │              duration, procurement_type, client_type    │   │
│  │ Company:     firm_size, bim_years, same_type_count,     │   │
│  │              current_utilization                        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                    Rule-based Derivation
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TIER 1                                  │
│                        (Derived)                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ has_follow_on, complexity, competition_params,          │   │
│  │ cost_ratio_base, bim_expertise, strategic_fit,          │   │
│  │ n_milestones, follow_on_beta_params, client_reliability │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                    Probabilistic Sampling
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TIER 2                                  │
│                     (Probabilistic)                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ cost_ratio, follow_on_prob, strategic_alignment,        │   │
│  │ volatility, capability_level, resource_utilization,     │   │
│  │ competition_level, complexity, recovery_rate            │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │
                    Monte Carlo (5,000 iterations)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        OUTPUT                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ TPV Distribution, Decision Probabilities,               │   │
│  │ ROV Components, Confidence Intervals                    │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Code Reference

- **Tier0Input**: `src/tier_system.py` - Dataclass for Tier 0 inputs
- **Tier1Derivation**: `src/tier_system.py` - Static derivation rules
- **Tier2Sampler**: `src/tier_system.py` - Probability distribution sampling
