# BIM 실물옵션 가치평가 모델

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**건설 BIM 설계용역 입찰 의사결정을 위한 실물옵션 기반 가치평가 프레임워크**

> **[English README](README.md)**

---

## 개요

본 모델은 건설 BIM 설계용역 입찰 시 전통적 NPV(순현재가치) 분석의 한계를 극복하고, 실물옵션 이론을 적용하여 전략적 유연성 가치를 정량화하는 평가 시스템입니다.

### 핵심 개념: TPV = NPV + ROV

```
총 프로젝트 가치 (TPV) = 순현재가치 (NPV) + 실물옵션 가치 (ROV)
```

- **NPV**: 전통적 현금흐름 할인법 기반 순현재가치
- **ROV**: 7개 실물옵션 가치의 합계 - 3개 조정요소

---

## 주요 기능

### 3-Tier 입력 시스템

입력 데이터의 불확실성을 체계적으로 관리하는 3단계 계층 시스템:

```
Tier 0 (확정)     →  Tier 1 (파생)      →  Tier 2 (확률적)
공고문 확정 정보      결정론적 파생          확률분포 샘플링
```

| Tier | 설명 | 예시 |
|------|------|------|
| **Tier 0** | 공고문에서 직접 추출 가능한 확정 정보 | 계약금액, 인프라유형, 설계단계, 계약기간, 조달방식, 발주처 |
| **Tier 1** | Tier 0에서 결정론적으로 파생되는 정보 | 후속설계 여부, 복잡도 등급, 경쟁수준 파라미터, 마일스톤 수 |
| **Tier 2** | 확률분포에서 샘플링되는 불확실 변수 | 비용비율, 후속확률, 전략적 정합성, 시장변동성 등 |

### 7개 실물옵션 (+)

| 옵션 | 설명 | 주요 파라미터 |
|------|------|---------------|
| **1. 후속설계 (Follow-on)** | 후속설계(실시설계) 참여 기회 | follow_on_prob, infra_type |
| **2. 역량축적 (Capability)** | BIM 역량 축적 및 학습효과 | capability_level, complexity |
| **3. 자원활용 (Resource)** | 유휴 자원 활용 기회 | resource_utilization |
| **4. 포기 (Abandonment)** | 조기 포기 및 손실 제한 | cost_ratio, strategic_alignment |
| **5. 축소 (Contract)** | 범위 축소 유연성 | infra_type, cost_ratio |
| **6. 전환 (Switch)** | 자원 재배치 옵션 | complexity, alternative_attractiveness |
| **7. 단계적 투자 (Staging)** | 단계적 투자 및 정보 획득 | n_milestones, time_to_decision |

### 3개 조정요소 (−)

| 조정요소 | 설명 | 이론적 근거 |
|----------|------|-------------|
| **상호작용 할인 (Interaction)** | 옵션 간 상호작용 할인 | Trigeorgis (1993) |
| **리스크 프리미엄 (Risk Premium)** | 변동성 및 복잡도 연동 리스크 | Borison (2005) |
| **연기비용 (Deferral Cost)** | 연기옵션의 기회비용 | Dixit & Pindyck (1994) |

---

## 설치 방법

### 요구사항

- Python 3.8 이상
- pip 패키지 관리자

### 소스에서 설치

```bash
# 저장소 복제
git clone https://github.com/ehxhf789789/01_Real_Options-Based_Bid_Decision_Support_Framework.git
cd 01_Real_Options-Based_Bid_Decision_Support_Framework

# 의존성 설치
pip install -r requirements.txt

# (선택) 패키지로 설치
pip install -e .
```

---

## 빠른 시작

### 방법 1: Python 스크립트 사용

```python
import pandas as pd
from src.valuation_engine import ValuationEngine

# 샘플 데이터 로드
df = pd.read_csv('data/sample_projects.csv')

# 엔진 초기화 및 평가 실행
engine = ValuationEngine(n_simulations=5000)
results, sensitivity = engine.run_valuation(df)

# 결과 출력
print(results[['project_id', 'npv', 'tpv', 'rov_net', 'decision_changed']])
```

### 방법 2: 포터블 실행파일 (Windows)

[Releases](https://github.com/ehxhf789789/01_Real_Options-Based_Bid_Decision_Support_Framework/releases) 페이지에서 `BIM_ROV_System.exe`를 다운로드하세요.

---

## 입력 데이터 형식

필수 컬럼이 포함된 CSV 파일:

| 컬럼 | 타입 | 설명 | 예시 |
|------|------|------|------|
| project_id | str | 프로젝트 ID | R01 |
| contract_amount | float | 계약금액 (백만원) | 520 |
| infra_type | str | 인프라 유형 | Road, Bridge, Tunnel |
| design_phase | str | 설계 단계 | 기본설계, 실시설계 |
| contract_duration | float | 계약 기간 (년) | 1.5 |
| procurement_type | str | 조달 방식 | 일반경쟁, 제한경쟁, 지명경쟁 |
| client_type | str | 발주처 유형 | 중앙, 지방, 공기업 |
| firm_size | str | 기업 규모 | Large, Medium, Small |
| bim_years | int | BIM 경력 (년) | 5 |
| same_type_count | int | 동일 유형 실적 (최근 5년) | 8 |
| current_utilization | float | 현재 자원 가동률 | 0.65 |

---

## 프로젝트 구조

```
R01_Real_Options/
├── README.md                 # 영문 문서
├── README_KR.md              # 본 문서 (한글)
├── LICENSE                   # MIT 라이선스
├── requirements.txt          # Python 의존성
├── setup.py                  # 설치 스크립트
│
├── src/                      # 핵심 소스 코드
│   ├── __init__.py
│   ├── valuation_engine.py   # 메인 평가 엔진
│   └── tier_system.py        # 3-Tier 입력 시스템
│
├── data/
│   └── sample_projects.csv   # 샘플 프로젝트 데이터
│
├── figures/                  # 시각화 결과
│   ├── Figure_4-1_NPV_TPV_Comparison.png
│   ├── Figure_4-2_ROV_Decomposition.png
│   └── Figure_4-3_Sensitivity_Tornado.png
│
├── scripts/                  # 유틸리티 스크립트
│   └── generate_figures.py
│
├── tests/                    # 테스트 코드
│   └── test_valuation.py
│
└── docs/                     # 추가 문서
    └── DEVELOPMENT_LOG.md
```

---

## 모델 아키텍처

### ROV 계산 흐름

```
ROV Gross = Σ(7개 옵션)
    ↓
- 상호작용 할인 (8~22%)
    ↓
ROV Adjusted
    ↓
- 리스크 프리미엄 (10~25%)
- 연기비용
    ↓
ROV Net (상한: 0.80 × |NPV|)
```

### 몬테카를로 시뮬레이션

- **반복 횟수**: 5,000회 시뮬레이션
- **샘플링**: 매 반복마다 Tier 2 분포에서 독립 샘플링
- **출력**: TPV 분포, 의사결정 확률, 신뢰구간

### 의사결정 프레임워크

| 의사결정 | 조건 |
|----------|------|
| **적극 참여 (Strong Participate)** | TPV > NPV×1.5 AND TPV > 30M |
| **참여 (Participate)** | NPV×1.05 < TPV ≤ NPV×1.5 |
| **조건부 (Conditional)** | NPV×0.80 < TPV ≤ NPV×1.05 |
| **기각 (Reject)** | TPV ≤ NPV×0.80 OR TPV ≤ 0 |

---

## 시각화 예시

### Figure 4-1: NPV vs TPV 비교
![NPV vs TPV](figures/Figure_4-1_NPV_TPV_Comparison.png)

10개 프로젝트의 NPV와 TPV를 비교하여 실물옵션 가치의 영향을 시각화합니다. Decision Change 프로젝트(NPV<0, TPV>0)는 점선으로 하이라이트됩니다.

### Figure 4-2: ROV 분해
![ROV Decomposition](figures/Figure_4-2_ROV_Decomposition.png)

각 프로젝트별 7개 옵션 구성비와 3개 조정요소를 Stacked Bar + Waterfall 차트로 표현합니다.

### Figure 4-3: 민감도 분석
![Sensitivity Tornado](figures/Figure_4-3_Sensitivity_Tornado.png)

주요 파라미터의 ±20% 변동이 TPV에 미치는 영향을 토네이도 차트로 표현합니다.

---

## 참고문헌

- Trigeorgis, L. (1993). Real Options and Interactions with Financial Flexibility
- Dixit, A. K., & Pindyck, R. S. (1994). Investment under Uncertainty
- Borison, A. (2005). Real Options Analysis: Where Are the Emperor's Clothes?
- Argote, L., & Epple, D. (1990). Learning Curves in Manufacturing
- 조달청 (2023). 건설용역 발주 현황 통계

---

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

## 저자

**이한빈 (Hanbin Lee)**

---

## 기여하기

기여를 환영합니다! Pull Request를 제출해 주세요.

1. 저장소 Fork
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

---

## 인용

본 연구를 인용하실 경우 다음을 참조해 주세요:

```bibtex
@software{lee2024bim_rov,
  author = {Lee, Hanbin},
  title = {BIM Real Options Valuation Model},
  year = {2024},
  url = {https://github.com/ehxhf789789/01_Real_Options-Based_Bid_Decision_Support_Framework}
}
```
