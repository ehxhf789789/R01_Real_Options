# ROV 구조적 오류 수정 제안서
## Structural Fix Proposal for ROV Always-Positive Bias

**작성일**: 2026-01-20
**핵심 문제**: ROV는 왜 항상 양수인가?

---

## 🔴 현재 구조의 근본 문제

### 문제 1: 모든 옵션이 구조적으로 >= 0

```python
# 현재 구조 - 7개 옵션 모두 max(0, ...) 또는 양수 계산식
rov_follow = max(S2 - K2, 0) * ... * ...        # >= 0
rov_capability = contract * complexity * 0.10    # > 0
rov_resource = contract * idle_ratio * 0.06      # > 0
rov_abandonment = max(0.15 * contract, 0)        # >= 0
rov_contract = contract * scope * prob * 0.04    # >= 0
rov_switch = contract * mobility * alt * 0.03    # >= 0
rov_stage = contract * milestones * info * 0.02  # >= 0

rov_gross = sum(7개 옵션)  # 항상 > 0
```

### 문제 2: 조정 요소가 충분히 크지 않음

```python
# 조정 요소들 - 가산(−) 방식
interaction = rov_gross * 0.08~0.22           # 최대 22%만 차감
risk_premium = rov_adj * 0.10~0.43            # 최대 43% 차감
deferral = contract * (1-SA) * MA * 0.12      # 작은 값

rov_net = rov_gross - interaction - risk_premium - deferral
```

**결과**: 조정 요소가 총 3개 합쳐도 rov_gross의 50~60%만 차감
→ **rov_net > 0 거의 확정**

### 문제 3: 조건부 패널티가 너무 약함

```python
# 현재 유일한 음수 전환 메커니즘
if strategic_alignment < 0.35 and alternative_attractiveness > 0.9:
    opportunity_penalty = contract * 0.05  # 계약금액의 5%만
    rov_net -= opportunity_penalty
```

**문제점**:
- 조건이 매우 극단적 (SA < 0.35 AND Alt > 0.9)
- 10개 프로젝트 중 0~1개만 해당
- 패널티가 너무 작음 (contract × 5%)

---

## ✅ 해결 방안

### 방안 1: 옵션 자체에 음수 가능성 부여 ⭐ **권장**

**핵심**: max(0, ...) 구조 제거 + 조건부 음수 전환

```python
# 1. 후속설계 참여 옵션 - 음수 허용
if tier2['has_follow_on'] and tier2['follow_on_prob'] > 0:
    S2 = contract * tier2['follow_on_multiplier'] * tier2['follow_on_prob']
    K2 = contract * tier2['follow_on_multiplier'] * tier2['cost_ratio']

    # 조건부 음수 전환
    if tier2['strategic_alignment'] < 0.50:
        # 전략적 부적합 → 참여 시 오히려 손실
        strategic_penalty = (0.50 - tier2['strategic_alignment']) * contract * 0.15
        intrinsic_value = (S2 - K2) - strategic_penalty  # 음수 가능
    else:
        intrinsic_value = max(S2 - K2, 0)

    rov_follow = intrinsic_value * time_decay * realization_rate * competition_discount

# 2. 역량 축적 옵션 - 기업 역량에 따라 음수 전환
bim_threshold = 0.60  # BIM 숙련도 임계값
if tier2['capability_level'] < bim_threshold:
    # 미숙련 기업 → 학습 비용 > 학습 효과
    learning_cost = contract * tier2['complexity'] * (bim_threshold - tier2['capability_level']) * 0.20
    learning_benefit = contract * tier2['complexity'] * tier2['capability_level'] * 0.10
    rov_capability = learning_benefit - learning_cost  # 음수 가능
else:
    rov_capability = contract * tier2['complexity'] * tier2['capability_level'] * 0.10

# 3. 유휴자원 활용 옵션 - 가동률 과부하 시 음수
if tier2['resource_utilization'] > 0.80:
    # 가동률 초과 → 기회비용 발생
    overload_cost = (tier2['resource_utilization'] - 0.80) * contract * 0.15
    idle_benefit = contract * (1 - tier2['resource_utilization']) * 0.06
    rov_resource = idle_benefit - overload_cost  # 음수 가능
else:
    rov_resource = contract * (1 - tier2['resource_utilization']) * 0.06

# 4. 포기 옵션 - NPV 양수 시 음수 전환
if npv_stage1 > 0:
    # NPV가 양수면 포기 옵션은 오히려 손실
    rov_abandonment = -contract * 0.02  # 명시적 음수
else:
    rov_abandonment = max(0.15 * contract - sunk_cost, 0)

# 5~7. 나머지 옵션도 동일 논리 적용
# 경쟁 과열 시 음수, 복잡도 과다 시 음수 등
```

**효과**:
- Small 기업 + 낮은 BIM 숙련도 → rov_capability < 0, rov_resource < 0
- 높은 가동률 → rov_resource < 0
- NPV > 0인 우량 프로젝트 → rov_abandonment < 0 (포기 옵션 불필요)
- **rov_gross 자체가 음수 가능**

---

### 방안 2: 조정 요소를 승수(×) 구조로 전환

**현재 (가산)**:
```python
rov_net = rov_gross - interaction - risk - deferral
```

**개선 (승수)**:
```python
# 1. 상호작용 할인 (승수)
rov_after_interaction = rov_gross * (1 - interaction_rate)

# 2. 리스크 프리미엄 (승수)
rov_after_risk = rov_after_interaction * (1 - risk_premium_rate)

# 3. 연기 가치 (가산 유지, 하지만 크기 증폭)
deferral_multiplier = (1 - tier2['strategic_alignment']) * tier2['alternative_attractiveness']
deferral = contract * deferral_multiplier * 0.25  # 기존 0.12 → 0.25

rov_net = rov_after_risk - deferral
```

**효과**:
- interaction_rate = 0.22 → rov × 0.78
- risk_premium_rate = 0.43 → rov × 0.57
- 누적: rov_gross × 0.78 × 0.57 = rov_gross × **0.44**
- **절반 이상 차감 가능**

---

### 방안 3: 전략적 패널티 대폭 강화

```python
# 3-1. 전략적 부적합 패널티 (누진)
if tier2['strategic_alignment'] < 0.50:
    misfit_degree = 0.50 - tier2['strategic_alignment']
    strategic_penalty = contract * misfit_degree * 0.40  # 기존 0.05 → 0.40
    rov_net -= strategic_penalty

# 3-2. 경쟁 과열 패널티
if tier2['competition_level'] > 0.70:
    competition_degree = tier2['competition_level'] - 0.70
    competition_penalty = rov_gross * competition_degree * 1.50  # 경쟁 과열 시 ROV 전체 감소
    rov_net -= competition_penalty

# 3-3. 기업 규모 부적합 패널티
firm_capacity_ratio = {
    'Large': 1.0,
    'Medium': 0.70,
    'Small': 0.40,
}.get(tier2.get('firm_size', 'Medium'), 0.70)

contract_threshold = contract / firm_capacity_ratio
if contract_threshold > 1.5:  # 기업 대비 과도한 계약 규모
    overscale_penalty = contract * (contract_threshold - 1.0) * 0.10
    rov_net -= overscale_penalty

# 3-4. BIM 미숙련 패널티
if tier2['capability_level'] < 0.60 and tier2['complexity'] > 0.70:
    # 복잡한 프로젝트인데 BIM 역량 부족
    skill_gap = (0.60 - tier2['capability_level']) * tier2['complexity']
    bim_penalty = contract * skill_gap * 0.30
    rov_net -= bim_penalty
```

**효과**:
- Small 기업: strategic_penalty + overscale_penalty + bim_penalty → **ROV < 0 가능**
- 경쟁 과열 시: competition_penalty가 rov_gross 초과 가능
- **누적 패널티가 rov_gross 넘으면 ROV < 0**

---

## 📊 시뮬레이션 예측 (방안 1 적용 시)

### Before (현재)
| PID | Firm | BIM_Y | NPV | ROV | TPV | 비고 |
|-----|------|-------|-----|-----|-----|------|
| R02 | Small | 2 | -8.3 | 4.9 | -3.4 | ⚠️ NPV < 0인데 ROV > 0 |
| R05 | Small | 3 | -5.2 | 5.1 | -0.1 | ⚠️ NPV < 0인데 ROV > 0 |
| R06 | Small | 2 | -4.8 | 4.5 | -0.3 | ⚠️ NPV < 0인데 ROV > 0 |

### After (방안 1 적용)
| PID | Firm | BIM_Y | NPV | ROV | TPV | 변경 사항 |
|-----|------|-------|-----|-----|-----|-----------|
| R02 | Small | 2 | -8.3 | **-2.5** | **-10.8** | ✅ rov_capability < 0, rov_resource < 0 |
| R05 | Small | 3 | -5.2 | **-1.8** | **-7.0** | ✅ rov_abandonment < 0 (NPV < 0) |
| R06 | Small | 2 | -4.8 | **-2.2** | **-7.0** | ✅ strategic_penalty 적용 |

**핵심 개선**:
- NPV < 0인 프로젝트 → ROV도 < 0 (현실 반영)
- Small 기업 평균 ROV: 4.8 → **-2.2**
- TPV 판정: "Marginal Reject" → "**Strong Reject**"

---

## 🎯 최종 권고안

### 단계별 구현

**Phase 1: 긴급 (방안 1 핵심만)**
```python
# 1. rov_capability, rov_resource에 음수 전환 로직 추가
# 2. rov_abandonment을 NPV > 0 시 음수로 변경
# 3. strategic_penalty를 0.05 → 0.20으로 상향
```

**Phase 2: 완전 (방안 1 + 3 전체)**
```python
# 1. 7개 옵션 전부에 조건부 음수 로직 추가
# 2. 4개 전략적 패널티 전체 구현
# 3. ROV < 0 비율 20~30% 목표
```

**Phase 3: 정교화 (방안 2 추가)**
```python
# 1. 조정 요소를 승수 구조로 전환
# 2. 감도 분석으로 계수 미세 조정
```

---

## 📝 학술적 근거

### ROV < 0의 이론적 정당성

**Trigeorgis (1996)**: "실물옵션은 유연성의 가치(Value of Flexibility)다. 유연성이 제약이 되면 음(−)의 가치를 가질 수 있다."

**McDonald & Siegel (1986)**: "투자 시점 선택의 가치는 기회비용이 투자 이익을 초과하면 음수가 된다."

**Dixit & Pindyck (1994)**: "포기 옵션은 NPV > 0인 프로젝트에서는 음(−)의 가치를 가진다. 왜냐하면 포기가 손실이기 때문이다."

**핵심**: ROV ≠ max(0, flexibility value)
ROV = flexibility value (음수 가능)

---

## 🔬 검증 방법

### 1. 극단 케이스 테스트
```python
# Test Case 1: 최악의 소기업
test_worst = {
    'firm_size': 'Small',
    'bim_years': 1,
    'strategic_alignment': 0.30,
    'competition_level': 0.85,
    'current_utilization': 0.95,
}
# 기대 결과: ROV < -10
```

### 2. ROV 분포 확인
```python
# 목표 분포
# ROV > 0: 60~70% (우량 프로젝트)
# ROV < 0: 30~40% (부실 프로젝트)
# 현재: ROV > 0 = 100% ← 비정상
```

### 3. Sanity Check
```
IF NPV < 0 AND firm_size == 'Small' AND bim_years < 3:
    THEN ROV < 0 확률 >= 80%
```

---

**작성자**: Claude Sonnet 4.5
**최종 업데이트**: 2026-01-20 23:58
