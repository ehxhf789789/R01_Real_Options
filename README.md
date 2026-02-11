# BIM Real Options Valuation Model

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**A Python-based valuation framework for BIM design service bidding decisions using Real Options Analysis (ROA)**

> **[한국어 README](README_KR.md)**

---

## Overview

This model overcomes the limitations of traditional NPV (Net Present Value) analysis in construction BIM design service bidding by quantifying strategic flexibility value through Real Options theory.

### Core Concept: TPV = NPV + ROV

```
Total Project Value (TPV) = Net Present Value (NPV) + Real Option Value (ROV)
```

- **NPV**: Traditional discounted cash flow based net present value
- **ROV**: Sum of 7 real option values minus 3 adjustment factors

---

## Key Features

### 3-Tier Input System

A hierarchical system that systematically manages input data uncertainty:

```
Tier 0 (Deterministic) → Tier 1 (Derived) → Tier 2 (Probabilistic)
   Confirmed data          Deterministic        Probability
   from tender docs        derivation           sampling
```

| Tier | Description | Examples |
|------|-------------|----------|
| **Tier 0** | Confirmed information from tender documents | Contract amount, Infrastructure type, Design phase, Duration, Procurement type, Client type |
| **Tier 1** | Deterministically derived from Tier 0 | Follow-on existence, Complexity grade, Competition parameters, Milestones |
| **Tier 2** | Sampled from probability distributions | Cost ratio, Follow-on probability, Strategic alignment, Volatility |

### 7 Real Options (+)

| Option | Description | Key Parameters |
|--------|-------------|----------------|
| **1. Follow-on** | Opportunity to participate in follow-on design | follow_on_prob, infra_type |
| **2. Capability** | BIM capability accumulation & learning effects | capability_level, complexity |
| **3. Resource** | Idle resource utilization opportunity | resource_utilization |
| **4. Abandonment** | Early termination & loss limitation | cost_ratio, strategic_alignment |
| **5. Contract** | Scope reduction flexibility | infra_type, cost_ratio |
| **6. Switch** | Resource reallocation option | complexity, alternative_attractiveness |
| **7. Staging** | Staged investment & information acquisition | n_milestones, time_to_decision |

### 3 Adjustment Factors (−)

| Adjustment | Description | Theoretical Basis |
|------------|-------------|-------------------|
| **Interaction** | Option interaction discount | Trigeorgis (1993) |
| **Risk Premium** | Volatility & complexity linked risk | Borison (2005) |
| **Deferral Cost** | Opportunity cost of deferral option | Dixit & Pindyck (1994) |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from source

```bash
# Clone the repository
git clone https://github.com/ehxhf789789/R01_Real_Options.git
cd R01_Real_Options

# Install dependencies
pip install -r requirements.txt

# (Optional) Install as package
pip install -e .
```

---

## Quick Start

### Option 1: Using Python Script

```python
import pandas as pd
from src.valuation_engine import ValuationEngine

# Load sample data
df = pd.read_csv('data/sample_projects.csv')

# Initialize engine and run valuation
engine = ValuationEngine(n_simulations=5000)
results, sensitivity = engine.run_valuation(df)

# Display results
print(results[['project_id', 'npv', 'tpv', 'rov_net', 'decision_changed']])
```

### Option 2: Portable Executable (Windows)

Download `BIM_ROV_System.exe` from the [Releases](https://github.com/ehxhf789789/R01_Real_Options/releases) page.

---

## Input Data Format

CSV file with the following required columns:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| project_id | str | Project identifier | R01 |
| contract_amount | float | Contract amount (million KRW) | 520 |
| infra_type | str | Infrastructure type | Road, Bridge, Tunnel |
| design_phase | str | Design phase | Basic Design, Detail Design |
| contract_duration | float | Duration (years) | 1.5 |
| procurement_type | str | Procurement method | Open, Limited, Nominated |
| client_type | str | Client type | Central, Local, Public Corp |
| firm_size | str | Firm size | Large, Medium, Small |
| bim_years | int | Years of BIM experience | 5 |
| same_type_count | int | Similar project count (5 years) | 8 |
| current_utilization | float | Current resource utilization | 0.65 |

---

## Project Structure

```
R01_Real_Options/
├── README.md                 # This file (English)
├── README_KR.md              # Korean documentation
├── LICENSE                   # MIT License
├── requirements.txt          # Python dependencies
├── setup.py                  # Installation script
│
├── src/                      # Core source code
│   ├── __init__.py
│   ├── valuation_engine.py   # Main valuation engine
│   └── tier_system.py        # 3-Tier input system
│
├── data/
│   └── sample_projects.csv   # Sample project data
│
├── figures/                  # Visualization outputs
│   ├── Figure_4-1_NPV_TPV_Comparison.png
│   ├── Figure_4-2_ROV_Decomposition.png
│   └── Figure_4-3_Sensitivity_Tornado.png
│
├── scripts/                  # Utility scripts
│   └── generate_figures.py
│
├── tests/                    # Test suite
│   └── test_valuation.py
│
└── docs/                     # Additional documentation
    └── DEVELOPMENT_LOG.md
```

---

## Model Architecture

### ROV Calculation Flow

```
ROV Gross = Σ(7 Options)
    ↓
- Interaction Discount (8~22%)
    ↓
ROV Adjusted
    ↓
- Risk Premium (10~25%)
- Deferral Cost
    ↓
ROV Net (capped at 0.80 × |NPV|)
```

### Monte Carlo Simulation

- **Iterations**: 5,000 simulations
- **Sampling**: Independent sampling from Tier 2 distributions per iteration
- **Output**: TPV distribution, Decision probabilities, Confidence intervals

### Decision Framework

| Decision | Condition |
|----------|-----------|
| **Strong Participate** | TPV > NPV×1.5 AND TPV > 30M |
| **Participate** | NPV×1.05 < TPV ≤ NPV×1.5 |
| **Conditional** | NPV×0.80 < TPV ≤ NPV×1.05 |
| **Reject** | TPV ≤ NPV×0.80 OR TPV ≤ 0 |

### Decision Change Detection

Detects cases where NPV-based and TPV-based decisions differ:
- **Up**: NPV < 0 (Reject) → TPV > 0 (Participate)
- **Down**: NPV > 0 (Participate) → TPV < 0 (Reject)

---

## Visualization Examples

### Figure 4-1: NPV vs TPV Comparison
![NPV vs TPV](figures/Figure_4-1_NPV_TPV_Comparison.png)

Compares NPV and TPV across 10 projects to visualize the impact of real option values. Decision Change projects (NPV<0, TPV>0) are highlighted.

### Figure 4-2: ROV Decomposition
![ROV Decomposition](figures/Figure_4-2_ROV_Decomposition.png)

Displays the composition of 7 options and 3 adjustment factors per project using Stacked Bar + Waterfall charts.

### Figure 4-3: Sensitivity Analysis
![Sensitivity Tornado](figures/Figure_4-3_Sensitivity_Tornado.png)

Tornado chart showing the impact of ±20% parameter variations on TPV.

---

## References

- Trigeorgis, L. (1993). Real Options and Interactions with Financial Flexibility
- Dixit, A. K., & Pindyck, R. S. (1994). Investment under Uncertainty
- Borison, A. (2005). Real Options Analysis: Where Are the Emperor's Clothes?
- Argote, L., & Epple, D. (1990). Learning Curves in Manufacturing
- Korea Public Procurement Service (2023). Construction Service Procurement Statistics

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Hanbin Lee**

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## Citation

If you use this work in your research, please cite:

```bibtex
@software{lee2024bim_rov,
  author = {Lee, Hanbin},
  title = {BIM Real Options Valuation Model},
  year = {2024},
  url = {https://github.com/ehxhf789789/R01_Real_Options}
}
```
