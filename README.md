# BIM Real Options Valuation Model

**BIM 설계용역 입찰 의사결정을 위한 실물옵션 기반 가치평가 모델**

> **버전 정보**
> - GUI Application: v15 (CustomTkinter 기반)
> - Valuation Engine: v14 (핵심 평가 로직)

## Overview

본 모델은 건설 BIM 설계용역 입찰 시 전통적 NPV 분석의 한계를 극복하고, 실물옵션 이론을 적용하여 전략적 유연성 가치를 정량화하는 평가 시스템입니다.

### Core Concept: TPV = NPV + ROV

```
Total Project Value (TPV) = Net Present Value (NPV) + Real Option Value (ROV)
```

- **NPV**: 전통적 현금흐름 할인법 기반 순현재가치
- **ROV**: 7개 실물옵션 가치의 합계 - 3개 조정요소

## Model Architecture

### 3-Tier Input System

입력 데이터의 불확실성을 체계적으로 관리하는 3단계 계층 시스템:

```
Tier 0 (Deterministic)  →  Tier 1 (Derived)  →  Tier 2 (Probabilistic)
   공고문 확정 정보          결정론적 파생           확률분포 샘플링
```

| Tier | Description | Examples |
|------|-------------|----------|
| **Tier 0** | 공고문에서 직접 추출 가능한 확정 정보 | 계약금액, 인프라유형, 설계단계, 계약기간, 조달방식, 발주처 |
| **Tier 1** | Tier 0에서 결정론적으로 파생되는 정보 | 후속설계 여부, 복잡도 등급, 경쟁수준 파라미터, 마일스톤 수 |
| **Tier 2** | 확률분포에서 샘플링되는 불확실 변수 | 비용비율, 후속확률, 전략적 정합성, 시장변동성 등 |

### 7 Real Options (+)

| Option | Description | Key Parameters |
|--------|-------------|----------------|
| **1. Follow-on** | 후속설계(실시설계) 참여 기회 | follow_on_prob, infra_type |
| **2. Capability** | BIM 역량 축적 및 학습효과 | capability_level, complexity |
| **3. Resource** | 유휴 자원 활용 기회 | resource_utilization |
| **4. Abandonment** | 조기 포기 및 손실 제한 | cost_ratio, strategic_alignment |
| **5. Contract** | 범위 축소 유연성 | infra_type, cost_ratio |
| **6. Switch** | 자원 재배치 옵션 | complexity, alternative_attractiveness |
| **7. Staging** | 단계적 투자 및 정보 획득 | n_milestones, time_to_decision |

### 3 Adjustment Factors (−)

| Adjustment | Description | Formula Basis |
|------------|-------------|---------------|
| **Interaction** | 옵션 간 상호작용 할인 (Trigeorgis 1993) | 활성 옵션 수에 비례 (8~22%) |
| **Risk Premium** | 변동성 및 복잡도 연동 리스크 (Borison 2005) | base + volatility + complexity |
| **Deferral Cost** | 연기옵션의 기회비용 (Dixit & Pindyck 1994) | 전략적 정합성 역비례 |

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
ROV Net
```

## Monte Carlo Simulation

- **Iterations**: 5,000회 시뮬레이션
- **Sampling**: Tier 2 확률분포에서 매 반복마다 독립 샘플링
- **Output**: TPV 분포, 의사결정 확률, 신뢰구간

### Decision Probabilities

| Decision | Condition |
|----------|-----------|
| **Strong Participate** | TPV > NPV×1.5 AND TPV > 30M |
| **Participate** | NPV×1.05 < TPV ≤ NPV×1.5 |
| **Conditional** | NPV×0.80 < TPV ≤ NPV×1.05 |
| **Reject** | TPV ≤ NPV×0.80 OR TPV ≤ 0 |

### Decision Change Detection

NPV 기반 의사결정과 TPV 기반 의사결정이 다른 경우를 탐지:
- **Up**: NPV < 0 (Reject) → TPV > 0 (Participate)
- **Down**: NPV > 0 (Participate) → TPV < 0 (Reject)

## Project Structure

```
01_Real_Options/
├── README.md                         # 본 문서
├── requirements.txt                  # Python 의존성
├── DEVELOPMENT_LOG.md               # 개발 기록
├── src/
│   ├── valuation_engine_v14.py      # 핵심 평가 엔진
│   ├── tier_system.py               # 3-Tier 입력 시스템
│   ├── main_app_v15_en.py           # GUI 메인 애플리케이션 (영문)
│   ├── gui_app_english.py           # GUI 컴포넌트 (영문)
│   ├── model_dashboard.py           # 대시보드 생성기
│   ├── generate_chapter4_figures.py # 논문 Figure 생성
│   └── generate_figures_v2.py       # Figure 생성 v2
├── figures/                          # 생성된 시각화 결과
├── docs/                             # 문서 (HTML 대시보드 등)
├── data/
│   └── realistic_projects_10.csv    # 샘플 프로젝트 데이터
└── build/                            # PyInstaller 빌드 파일
```

## Quick Start

### Python 스크립트

```python
import pandas as pd
from valuation_engine_v14 import ValuationEngine

# 데이터 로드
df = pd.read_csv('data/realistic_projects_10.csv')

# 엔진 초기화 및 평가 실행
engine = ValuationEngine(n_simulations=5000)
results, sensitivity = engine.run_valuation(df)

# 결과 출력
print(results[['project_id', 'npv', 'tpv', 'rov_net', 'decision_changed']])
```

## Input Data Format

CSV 파일 필수 컬럼:

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| project_id | str | 프로젝트 ID | R01 |
| contract_amount | float | 계약금액 (백만원) | 520 |
| infra_type | str | 인프라 유형 | Road, Bridge, Tunnel |
| design_phase | str | 설계 단계 | 기본설계, 실시설계 |
| contract_duration | float | 계약 기간 (년) | 1.5 |
| procurement_type | str | 조달 방식 | 일반경쟁, 제한경쟁, 지명경쟁 |
| client_type | str | 발주처 유형 | 중앙, 지방, 공기업 |

## Visualization Examples

### Figure 4-1: NPV vs TPV Comparison
![NPV vs TPV](figures/Figure_4-1_NPV_TPV_Comparison.png)

10개 프로젝트의 NPV와 TPV를 비교하여 실물옵션 가치의 영향을 시각화합니다. Decision Change 프로젝트(NPV<0, TPV>0)는 점선으로 하이라이트됩니다.

### Figure 4-2: ROV Decomposition
![ROV Decomposition](figures/Figure_4-2_ROV_Decomposition.png)

각 프로젝트별 7개 옵션 구성비와 3개 조정요소를 Stacked Bar + Waterfall 차트로 표현합니다.

### Figure 4-3: Sensitivity Tornado
![Sensitivity Tornado](figures/Figure_4-3_Sensitivity_Tornado.png)

주요 파라미터의 ±20% 변동이 TPV에 미치는 영향을 토네이도 차트로 표현합니다.

## Key References

- Trigeorgis, L. (1993). Real Options and Interactions with Financial Flexibility
- Dixit, A. K., & Pindyck, R. S. (1994). Investment under Uncertainty
- Borison, A. (2005). Real Options Analysis: Where Are the Emperor's Clothes?
- Argote, L., & Epple, D. (1990). Learning Curves in Manufacturing
- 조달청 (2023). 건설용역 발주 현황 통계

## Requirements

- Python 3.8+
- numpy
- pandas
- matplotlib

## License

This project is for academic research purposes.

## Author

한빈 이 (Hanbin Lee)
