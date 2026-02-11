# BIM Real Options Valuation Model (BIM-ROVS)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**A Real Options–Based Decision Support Model for Bid/No-Bid Decisions in BIM Engineering Projects**

> **[한국어 README](README_KR.md)**

---

## Overview

This model provides a Python-based valuation framework for BIM design service bidding decisions using Real Options Analysis (ROA). It overcomes the limitations of traditional NPV analysis by quantifying strategic flexibility value that DCF-based methods fail to capture.

### Research Background

As BIM becomes mandatory in public construction projects, engineering firms face intensifying bid competition. Traditional DCF methods cannot value managerial flexibility to expand, contract, or abandon projects in response to market changes, leading to undervaluation of projects with high long-term growth potential despite low short-term profitability.

### Core Concept: TPV = NPV + ROV

```
Total Project Value (TPV) = Net Present Value (NPV) + Real Option Value (ROV)     ... Eq.(1)

Where:
  ROV = Σ(7 Options) - Σ(3 Adjustments)                                           ... Eq.(2)
```

- **NPV**: Deterministic revenue from traditional discounted cash flow (Eq.12)
- **ROV**: Opportunity value from 7 real options minus 3 adjustment factors

---

## Key Features

### 5-Level Hierarchical Framework

A systematic approach that transforms raw tender document information into probabilistic parameters:

```
Level 1        Level 2           Level 3             Level 4          Level 5
Data Input → Parameter    →  Probabilistic   →  Value        →  Decision
             Mapping          Modeling           Evaluation      Making
```

| Level | Description | Implementation |
|-------|-------------|----------------|
| **Level 1** | Confirmed data from tender documents (6 variables) + Company characteristics (4 variables) | Tier0Input |
| **Level 2** | Rule-based parameter derivation from literature | Tier1Derivation |
| **Level 3** | Probability distribution sampling | Tier2Sampler |
| **Level 4** | Monte Carlo simulation (5,000 iterations) | ValuationEngine |
| **Level 5** | Decision signal classification | Decision Logic |

### 7 Real Options (+)

| Option | Symbol | Description | Theoretical Basis |
|--------|--------|-------------|-------------------|
| **1. Follow-on** | O_exp | Information advantage for subsequent projects | Geske (1979) |
| **2. Capability** | O_grw | BIM capability accumulation & learning effects | Argote & Epple (1990) |
| **3. Resource** | O_swi | Idle resource utilization opportunity | - |
| **4. Contract** | O_cnt | Scope adjustment flexibility | Flyvbjerg (2003) |
| **5. Switch** | O_swo | Resource reallocation option | - |
| **6. Abandonment** | O_abn | Early termination & loss limitation | Triantis (2005) |
| **7. Staging** | O_stg | Phased investment & information acquisition | Sequential Investment |

### 3 Adjustment Factors (−)

| Adjustment | Symbol | Description | Theoretical Basis |
|------------|--------|-------------|-------------------|
| **Interaction** | I_int | Option overlap discount (γ ∈ [0.08, 0.30]) | Trigeorgis (1993) |
| **Risk Premium** | P_risk | ρ = 0.15 + σ×0.30 + κ×0.10 | Borison (2005) |
| **Deferral Cost** | C_wait | Opportunity cost of waiting option | Dixit & Pindyck (1994) |

---

## Key Parameters (Literature-Based)

### Infrastructure Type Parameters (Flyvbjerg et al. 2003)

| Parameter | Road | Bridge | Tunnel | Source |
|-----------|------|--------|--------|--------|
| Base Complexity (κ₀) | 0.60 | 0.85 | 1.00 | Cost overrun data |
| Design Flexibility (f_scope) | 1.00 | 0.65 | 0.48 | Eq.(4) |
| Base Volatility (σ₀) | 0.22 | 0.35 | 0.42 | Eq.(5) |
| Design Reviews (n) | 3 | 4 | 4 | MOLIT (2024) |
| Value Multiplier (m_f) | 1.67 | 1.84 | 1.84 | MOTIE (2024) |

### Competition Parameters (KENCA 2023)

| Procurement Type | Mean (μ_c) | Std (σ_c) |
|------------------|------------|-----------|
| Open | 0.72 | 0.14 |
| Limited | 0.48 | 0.10 |
| Nominated | 0.21 | 0.04 |

### Client Reliability (KENCA 2023)

| Client Type | Reliability (φ_c) |
|-------------|-------------------|
| Central | 0.92 |
| Public Corp | 0.88 |
| Local | 0.81 |

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

### Tender Document Variables (6)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| project_id | str | Project identifier | P001 |
| contract_amount | float | Contract amount (million KRW) | 520 |
| infra_type | str | Infrastructure type | Road, Bridge, Tunnel |
| design_phase | str | Design phase | Basic Design, Detailed Design |
| contract_duration | float | Duration (years) | 1.5 |
| procurement_type | str | Procurement method | Open, Limited, Nominated |
| client_type | str | Client type | Central, Local, Public Corp |

### Company Characteristic Variables (4)

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| firm_size | str | Firm size | Large, Medium, Small |
| bim_years | int | Years of BIM experience | 5 |
| same_type_count | int | Similar project count (5 years) | 8 |
| current_utilization | float | Current resource utilization | 0.65 |

---

## Decision Framework (Table 7)

| Decision | Condition | Interpretation |
|----------|-----------|----------------|
| **Strong Participate** | TPV > NPV×1.5 AND TPV > 300M | High strategic value |
| **Participate** | TPV > NPV×1.05 | Favorable opportunity |
| **Conditional** | TPV > NPV×0.80 | Marginal value |
| **Reject** | TPV ≤ NPV×0.80 OR TPV ≤ 0 | Conserve resources |

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
│   ├── valuation_engine.py   # Main valuation engine (Level 4-5)
│   └── tier_system.py        # 5-Level input system (Level 1-3)
│
├── data/
│   └── sample_projects.csv   # Sample project data
│
├── figures/                  # Visualization outputs
│   ├── Figure_4-1_NPV_TPV_Comparison.png
│   ├── Figure_4-2_ROV_Decomposition.png
│   └── Figure_4-3_Sensitivity_Tornado.png
│
├── docs/                     # Documentation
│   └── wiki/                 # GitHub Wiki content
│       ├── Real-Options-Theory.md
│       ├── Model-Architecture.md
│       └── 3-Tier-System.md
│
├── scripts/                  # Utility scripts
│   └── generate_figures.py
│
└── tests/                    # Test suite
    └── test_valuation.py
```

---

## Visualization Examples

### Figure 4: NPV vs TPV Comparison
![NPV vs TPV](figures/Figure_4-1_NPV_TPV_Comparison.png)

### Figure 5: ROV Decomposition (Waterfall)
![ROV Decomposition](figures/Figure_4-2_ROV_Decomposition.png)

### Figure 6: Sensitivity Tornado Diagram
![Sensitivity Tornado](figures/Figure_4-3_Sensitivity_Tornado.png)

---

## References

1. Trigeorgis, L. (1993). The nature of option interactions. JFQA.
2. Dixit, A. K., & Pindyck, R. S. (1994). Investment under Uncertainty. Princeton.
3. Copeland, T., & Antikarov, V. (2001). Real options: A practitioner's guide.
4. Borison, A. (2005). Real Options Analysis. JACF.
5. Flyvbjerg, B., et al. (2003). Cost overruns in transport projects. Transport Reviews.
6. Geske, R. (1979). The Valuation of Compound Options. JFE.
7. Argote, L., & Epple, D. (1990). Learning Curves in Manufacturing. Science.
8. Jofre-Bonet, M., & Pesendorfer, M. (2003). Estimation of a dynamic auction game. Econometrica.
9. KENCA (2023). Engineering Service Industry Survey.
10. MOTIE (2024). Engineering Service Fee Standards.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Author

**Hanbin Lee** - Korea University of Science and Technology (UST)
- Email: ehxhf789@kict.re.kr
- Affiliation: Korea Institute of Civil Engineering and Building Technology (KICT)

**Hyoun-Seok Moon** (Corresponding Author)
- Email: hsmoon@kict.re.kr
- Affiliation: KICT / UST

---

## Citation

If you use this work in your research, please cite:

```bibtex
@article{lee2025bim_rov,
  author = {Lee, Han-Bin and Moon, Hyoun-Seok},
  title = {A Real Options–Based Decision Support Model for Bid/No-Bid Decisions in BIM Engineering Projects},
  journal = {Journal of the Korea Institute of Building Construction},
  year = {2025},
  note = {Under Review}
}
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
