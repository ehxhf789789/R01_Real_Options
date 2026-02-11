# BIM Real Options Valuation Model - Wiki

Welcome to the BIM-ROVS (BIM Real Options Valuation System) wiki!

## About This Project

This project provides a Python-based decision support system for BIM engineering project bid/no-bid decisions using Real Options Analysis (ROA). It helps engineering firms make better bidding decisions by quantifying the strategic flexibility value that traditional DCF/NPV analysis fails to capture.

### Research Paper

> **실물옵션 기반의 BIM 엔지니어링 프로젝트 입찰 참여여부 의사결정 지원 모형**
> (A Real Options–Based Decision Support Model for Bid/No-Bid Decisions in BIM Engineering Projects)
>
> Han-Bin Lee, Hyoun-Seok Moon
> Korea University of Science and Technology / Korea Institute of Civil Engineering and Building Technology

### Core Concept

```
TPV = NPV + ROV                                     ... Eq.(1)

Where:
  TPV = Total Project Value (총 프로젝트 가치)
  NPV = Net Present Value (확정적 수익)
  ROV = Real Option Value (기회 가치) = Σ(7 Options) - Σ(3 Adjustments)
```

---

## Wiki Contents

### Theory & Concepts
- [Real Options Theory](Real-Options-Theory) - Understanding the 7 real options and 3 adjustments
- [5-Level Hierarchical System](3-Tier-System) - How the input transformation hierarchy works

### Technical Documentation
- [Model Architecture](Model-Architecture) - Detailed system structure and calculation flow
- [API Reference](API-Reference) - Function and class documentation

### User Guides
- [Installation Guide](Installation-Guide) - Setting up the environment
- [Usage Examples](Usage-Examples) - Practical examples with sample data

---

## Key Features

### 7 Real Options (+)

| Category | Option | Symbol | Description |
|----------|--------|--------|-------------|
| Growth | Follow-on | O_exp | Information advantage for subsequent projects |
| Growth | Capability | O_grw | BIM capability accumulation & learning effects |
| Flexibility | Resource | O_swi | Idle resource utilization opportunity |
| Flexibility | Contract | O_cnt | Scope adjustment flexibility |
| Flexibility | Switch | O_swo | Resource reallocation option |
| Control | Abandonment | O_abn | Early termination & loss limitation |
| Control | Staging | O_stg | Phased investment & information acquisition |

### 3 Adjustment Factors (−)

| Adjustment | Symbol | Formula | Theoretical Basis |
|------------|--------|---------|-------------------|
| Interaction | I_int | γ ∈ [0.08, 0.30] | Trigeorgis (1993) |
| Risk Premium | P_risk | 0.15 + σ×0.30 + κ×0.10 | Borison (2005) |
| Deferral Cost | C_wait | f(S, A, T) | Dixit & Pindyck (1994) |

---

## Quick Links

- [GitHub Repository](https://github.com/ehxhf789789/R01_Real_Options)
- [README (English)](https://github.com/ehxhf789789/R01_Real_Options/blob/main/README.md)
- [README (Korean)](https://github.com/ehxhf789789/R01_Real_Options/blob/main/README_KR.md)
- [Releases](https://github.com/ehxhf789789/R01_Real_Options/releases)

---

## Key Parameters (Literature-Based)

### Infrastructure Type Parameters

| Parameter | Road | Bridge | Tunnel | Source |
|-----------|------|--------|--------|--------|
| Base Complexity (κ₀) | 0.60 | 0.85 | 1.00 | Flyvbjerg (2003) |
| Design Flexibility (f_scope) | 1.00 | 0.65 | 0.48 | Flyvbjerg (2003) |
| Base Volatility (σ₀) | 0.22 | 0.35 | 0.42 | Flyvbjerg (2003) |
| Design Reviews (n) | 3 | 4 | 4 | MOLIT (2024) |
| Value Multiplier (m_f) | 1.67 | 1.84 | 1.84 | MOTIE (2024) |

### Decision Framework (Table 7)

| Decision | Condition | Interpretation |
|----------|-----------|----------------|
| Strong Participate | TPV > NPV×1.5 AND TPV > 300M | High strategic value |
| Participate | TPV > NPV×1.05 | Favorable opportunity |
| Conditional | TPV > NPV×0.80 | Marginal value |
| Reject | TPV ≤ NPV×0.80 OR TPV ≤ 0 | Conserve resources |
