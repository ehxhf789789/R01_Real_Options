# Development Log - BIM Real Options Valuation Model

## Claude Code 작업 기록

**작성일**: 2024년 12월 8일
**작업 도구**: Claude Code (Anthropic Claude Opus 4.5)

### 버전 체계
| 구성요소 | 버전 | 설명 |
|----------|------|------|
| **GUI Application** | v15 | CustomTkinter 기반 Modern UI |
| **Valuation Engine** | v14 | 핵심 평가 로직 (7옵션 + 3조정요소) |
| **Tier System** | - | 3-Tier 입력 시스템 |

> **Note**: EXE 파일명 `BIM_ROV_System_v15.exe`는 GUI 앱 버전(v15)을 따름.
> 내부 평가 엔진은 `valuation_engine_v14.py`를 사용.

---

## 1. 프로젝트 개요

### 목적
BIM 설계용역 입찰 의사결정을 위한 실물옵션 기반 가치평가 모델 개발

### 핵심 프레임워크
```
TPV (Total Project Value) = NPV (Net Present Value) + ROV (Real Option Value)
```

---

## 2. 주요 개발 단계

### Phase 1: 평가 엔진 개발 (valuation_engine_v14.py)

#### 2.1 3-Tier 입력 시스템 설계
- **Tier 0**: 공고문에서 직접 추출 가능한 확정 정보 (6개 변수)
  - project_id, contract_amount, infra_type, design_phase, contract_duration, procurement_type, client_type
- **Tier 1**: Tier 0에서 결정론적으로 파생되는 정보
  - has_follow_on, complexity, competition_params, n_milestones 등
- **Tier 2**: 확률분포에서 샘플링되는 불확실 변수
  - cost_ratio, follow_on_prob, strategic_alignment, volatility 등

#### 2.2 7개 실물옵션 모델링
| 옵션 | 이론적 기반 | 핵심 수식 |
|------|-------------|-----------|
| Follow-on | 조달청 2023 분리발주율 | S0 - K (행사가치) × 인프라별 연계율 |
| Capability | Argote & Epple 1990 학습곡선 | contract × complexity × growth_rate × (1 - cap^1.5) |
| Resource | 자원기반관점 | contract × (1 - utilization) × premium × complexity |
| Abandonment | Triantis 2005 | salvage + reallocation - sunk_cost |
| Contract | 범위 축소 유연성 | contract × scope_flex × adverse_prob × flex_rate |
| Switch | 자원 재배치 | contract × mobility × alternative × switch_rate |
| Staging | Dixit & Pindyck 1994 | contract × milestones × info_factor × checkpoint_value |

#### 2.3 3개 조정요소
| 조정요소 | 이론적 기반 | 적용 비율 |
|----------|-------------|-----------|
| Interaction | Trigeorgis 1993 | 8~22% (활성 옵션 수에 비례) |
| Risk Premium | Borison 2005 | 10% + volatility×0.25 + complexity×0.08 |
| Deferral Cost | Dixit & Pindyck 1994 | 연기 기회비용 |

#### 2.4 Monte Carlo 시뮬레이션
- **반복 횟수**: 5,000회
- **샘플링 방식**: Tier 2 확률분포에서 독립 샘플링
- **출력**: TPV 분포, 의사결정 확률, 90% 신뢰구간

---

### Phase 2: GUI 애플리케이션 개발 (main_app_v15.py)

#### 2.5 주요 기능
- CSV 파일 로드 및 검증
- 실시간 평가 진행률 표시
- 결과 테이블 및 차트 시각화
- Excel/CSV 내보내기

#### 2.6 PyInstaller 빌드
```bash
pyinstaller --onefile --windowed --name BIM_ROV_System_v15 main_app_v15.py
```
- 결과물: `BIM_ROV_System_v15.exe` (73MB 포터블)

---

### Phase 3: 시각화 Figure 개발 (generate_chapter4_figures.py)

#### 2.7 Figure 4-1: NPV vs TPV Comparison
- **목적**: 10개 프로젝트의 NPV와 TPV 비교
- **하이라이트**: Decision Change 프로젝트 (NPV<0, TPV>0)
- **데이터**: v14 엔진 실제 평가 결과 (R01~R10)

#### 2.8 Figure 4-2: ROV Decomposition Waterfall
- **목적**: 7개 옵션 구성비 + 3개 조정요소 시각화
- **차트 유형**: Stacked Bar (옵션) + Waterfall (조정요소)
- **범례**: 3그룹 분리 (Real Options / Adjustments / Common)
- **데이터 라벨**: 각 옵션/조정요소의 비중(%) 표시

#### 2.9 Figure 4-3: Sensitivity Tornado
- **목적**: 주요 파라미터의 TPV 영향도 분석
- **변동 범위**: ±20%
- **Key Drivers**: Cost Ratio, Follow-on Probability

---

## 3. 실제 평가 결과 (R01~R10)

### 3.1 v14 엔진 평가 결과 요약

| Project | Infra | Phase | NPV (M) | TPV (M) | ROV Net | Decision Change |
|---------|-------|-------|---------|---------|---------|-----------------|
| R01 | Road | P | 65.09 | 87.09 | 22.00 | No |
| R02 | Road | D | -4.31 | 6.36 | 10.67 | **Yes (Up)** |
| R03 | Road | P | 6.80 | 22.44 | 15.64 | No |
| R04 | Bridge | P | 33.46 | 58.95 | 25.49 | No |
| R05 | Bridge | D | -7.23 | 0.39 | 7.62 | **Yes (Up)** |
| R06 | Bridge | D | -5.71 | 0.54 | 6.25 | **Yes (Up)** |
| R07 | Tunnel | P | 85.21 | 130.20 | 44.99 | No |
| R08 | Tunnel | D | -5.66 | 9.85 | 15.51 | **Yes (Up)** |
| R09 | Tunnel | P | 105.82 | 152.42 | 46.60 | No |
| R10 | Tunnel | D | 7.76 | 29.73 | 21.97 | No |

### 3.2 주요 발견
- **Decision Change 비율**: 10개 중 4개 (40%)
- **최대 ROV 프로젝트**: R09 (해저터널, ROV Net = 46.60M)
- **인프라 유형별 ROV**: Tunnel > Bridge > Road

---

## 4. 작업 세부 이력

### Session 1: 평가 엔진 개발
```
[작업 내용]
- tier_system.py 생성: 3-Tier 입력 시스템 구현
- valuation_engine_v14.py 생성: 7개 옵션 + 3개 조정요소 모델링
- Monte Carlo 시뮬레이션 구현 (5,000회)

[수정 사항]
- deferral_multiplier: 0.30 → 0.05 (과도한 연기비용 보정)
- interaction_discount: 옵션 수에 따른 차등 적용 (8~22%)
```

### Session 2: GUI 및 포터블 빌드
```
[작업 내용]
- main_app_v15.py: tkinter 기반 GUI 애플리케이션
- PyInstaller로 EXE 빌드

[이슈 해결]
- 한글 인코딩 문제: utf-8-sig 사용
- matplotlib 백엔드 충돌: TkAgg 명시적 지정
```

### Session 3: 시각화 Figure 개발
```
[작업 내용]
- Figure 4-1: NPV vs TPV 비교 차트
- Figure 4-2: ROV Decomposition Waterfall
- Figure 4-3: Sensitivity Tornado

[디자인 수정 이력]
1. 초기 버전: 하드코딩된 가짜 데이터 (P001~P010)
2. 수정 1: 실제 v14 엔진 결과로 데이터 교체 (R01~R10)
3. 수정 2: Figure 4-2 범례 3그룹 분리
4. 수정 3: 모든 옵션 비중(%) 라벨 추가
5. 수정 4: 폰트 크기 5.5~7pt로 통일
6. 수정 5: Figure 크기 축소 (가독성 향상)
   - 4-1: 14×8 → 10×5.5
   - 4-2: 20×11 → 12×6.5
   - 4-3: 14×9 → 10×6
```

### Session 4: Github 폴더 구성
```
[작업 내용]
- Github/ 폴더 구조 생성
- 핵심 소스 코드 복사
- README.md 작성 (모델 구조 및 알고리즘 설명)
- requirements.txt 생성
- DEVELOPMENT_LOG.md 작성 (본 문서)
```

---

## 5. 파일 구조 및 의존성

### 5.1 최종 폴더 구조
```
Github/
├── README.md                          # 모델 설명서
├── DEVELOPMENT_LOG.md                 # 개발 기록 (본 문서)
├── requirements.txt                   # Python 의존성
├── dist/
│   └── BIM_ROV_System_v15.exe         # 포터블 실행파일
├── src/
│   ├── valuation_engine_v14.py        # 핵심 평가 엔진
│   ├── tier_system.py                 # 3-Tier 입력 시스템
│   └── generate_chapter4_figures.py   # 시각화 코드
├── figures/
│   ├── Figure_4-1_NPV_TPV_Comparison.png
│   ├── Figure_4-2_ROV_Decomposition.png
│   └── Figure_4-3_Sensitivity_Tornado.png
└── data/
    └── realistic_projects_10.csv      # 샘플 데이터
```

### 5.2 모듈 의존성

```
valuation_engine_v14.py
    └── tier_system.py (import)
    └── numpy, pandas

generate_chapter4_figures.py
    └── numpy, matplotlib (독립 실행 가능)

main_app_v15.py (EXE 내부)
    └── valuation_engine_v14.py
    └── tier_system.py
    └── tkinter, numpy, pandas, matplotlib
```

### 5.3 실행 방법

#### Python 스크립트 실행
```bash
cd Github/src
python valuation_engine_v14.py      # 평가 엔진 테스트
python generate_chapter4_figures.py  # Figure 생성
```

#### 포터블 EXE 실행
```
Github/dist/BIM_ROV_System_v15.exe 더블클릭
```

---

## 6. 알려진 제한사항

1. **민감도 분석**: 현재 플레이스홀더로 구현됨 (실제 재평가 미수행)
2. **Figure 4-3**: 하드코딩된 민감도 데이터 사용
3. **EXE 크기**: 73MB (PyInstaller onefile 모드 한계)

---

## 7. 향후 개선 방향

1. 실제 민감도 분석 구현 (Tier 2 파라미터 변동 → 재평가)
2. 웹 기반 인터페이스 개발 (Streamlit/Flask)
3. 데이터베이스 연동 (프로젝트 이력 관리)
4. 보고서 자동 생성 기능

---

## 8. 참고 문헌

- Trigeorgis, L. (1993). Real Options and Interactions with Financial Flexibility
- Dixit, A. K., & Pindyck, R. S. (1994). Investment under Uncertainty
- Borison, A. (2005). Real Options Analysis: Where Are the Emperor's Clothes?
- Argote, L., & Epple, D. (1990). Learning Curves in Manufacturing
- 조달청 (2023). 건설용역 발주 현황 통계

---

*Generated by Claude Code (Anthropic Claude Opus 4.5)*
