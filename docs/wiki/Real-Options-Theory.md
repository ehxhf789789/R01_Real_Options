# Real Options Theory

## Why Real Options?

### Limitations of Traditional NPV

Traditional Net Present Value (NPV) analysis has significant limitations when evaluating projects with high uncertainty:

1. **Static Assumption**: NPV assumes a fixed project plan that cannot be changed
2. **Ignores Flexibility**: Management's ability to adapt decisions is not valued
3. **Binary Decision**: Projects are either accepted or rejected, with no middle ground
4. **Undervalues Uncertainty**: Higher uncertainty is always seen as negative

### What are Real Options?

Real Options extend financial option theory to real (physical) assets and strategic decisions. Just as a financial call option gives the holder the right (but not obligation) to buy a stock at a predetermined price, a real option gives management the right to take certain actions in the future.

**Key Insight**: Uncertainty + Flexibility = Value

When a company has the flexibility to respond to uncertainty, that uncertainty actually creates value!

---

## The 7 Real Options in This Model

### 1. Follow-on Option (후속설계 옵션)

**Definition**: The opportunity to participate in subsequent design phases (e.g., detailed design after basic design)

**When it's valuable**:
- Basic design phase with high probability of detailed design follow-up
- Strong relationship with client
- Good project performance

**Theoretical Basis**: Compound Option Theory (Geske 1979)

```
Value = f(follow_on_probability, multiplier, infrastructure_type)
```

---

### 2. Capability Option (역량 축적 옵션)

**Definition**: The value of BIM capability accumulation and learning effects from project execution

**When it's valuable**:
- Early stage of BIM adoption
- Complex projects that accelerate learning
- Strategic importance for future capabilities

**Theoretical Basis**: Learning Curve Theory (Argote & Epple 1990)

```
Learning Effect = Complexity × Capability Growth Rate × (1 - Diminishing Factor)
```

---

### 3. Resource Option (자원 활용 옵션)

**Definition**: The opportunity to utilize idle resources that would otherwise be unproductive

**When it's valuable**:
- Low current resource utilization
- Matching resource requirements with available capacity
- Avoiding fixed cost absorption issues

---

### 4. Abandonment Option (포기 옵션)

**Definition**: The right to terminate a project early and salvage remaining value

**When it's valuable**:
- Projects with high cost uncertainty
- Clear exit mechanisms (milestone-based contracts)
- Alternative uses for freed resources

**Theoretical Basis**: Triantis (2005)

---

### 5. Contract Flexibility Option (축소 옵션)

**Definition**: The ability to reduce project scope when conditions are unfavorable

**When it's valuable**:
- Infrastructure types with modular designs
- Contracts with scope adjustment clauses
- High cost ratio uncertainty

---

### 6. Switch Option (전환 옵션)

**Definition**: The option to reallocate resources to more attractive alternatives

**When it's valuable**:
- High resource mobility
- Attractive alternative projects available
- Low switching costs

---

### 7. Staging Option (단계적 투자 옵션)

**Definition**: The value of staged investment that allows information gathering before full commitment

**When it's valuable**:
- Projects with multiple milestones
- High uncertainty that resolves over time
- Ability to adjust based on interim results

**Theoretical Basis**: Sequential Investment Theory

---

## The 3 Adjustment Factors

To prevent overvaluation of real options, three adjustment factors are applied:

### 1. Interaction Discount (상호작용 할인)

Multiple options cannot be fully additive because exercising one may affect others.

**Formula**: 8-22% discount based on number of active options

**Theoretical Basis**: Trigeorgis (1993)

### 2. Risk Premium (리스크 프리미엄)

Higher volatility and complexity require additional risk compensation.

**Formula**: Base premium + Volatility premium + Complexity premium

**Theoretical Basis**: Borison (2005)

### 3. Deferral Cost (연기 비용)

The opportunity cost of not deferring the investment decision.

**Formula**: Based on strategic alignment and market opportunity

**Theoretical Basis**: Dixit & Pindyck (1994)

---

## Core Formula

```
TPV = NPV + ROV

Where:
  ROV = (Sum of 7 Options) - Interaction Discount - Risk Premium - Deferral Cost

  ROV is capped at 0.80 × |NPV| to prevent unrealistic valuations
```

---

## References

1. Trigeorgis, L. (1993). Real Options and Interactions with Financial Flexibility. Financial Management.
2. Dixit, A. K., & Pindyck, R. S. (1994). Investment under Uncertainty. Princeton University Press.
3. Borison, A. (2005). Real Options Analysis: Where Are the Emperor's Clothes? Journal of Applied Corporate Finance.
4. Argote, L., & Epple, D. (1990). Learning Curves in Manufacturing. Science.
5. Geske, R. (1979). The Valuation of Compound Options. Journal of Financial Economics.
