# ROI Calculation Worksheet

## Project Information
- **Entity:** {{ENTITY}}
- **Project:** {{PROJECT}}
- **Date:** {{DATE}}

---

## Time Value Calculation

### Time Estimates
| Metric | Value | Notes |
|--------|-------|-------|
| Manual Hours (estimated) | {{MANUAL_HOURS}} | How long this would take without AI |
| Claude Hours (actual) | {{CLAUDE_HOURS}} | Actual time spent with Claude |
| Time Saved | {{TIME_SAVED}} | Manual - Claude |

### Hourly Rate
- **Rate Used:** ${{HOURLY_RATE}}/hour
- **Basis:** {{RATE_BASIS}} (e.g., consultant rate, internal cost, opportunity cost)

### Quality Multiplier
Choose one:
- [ ] **1.0x** - Same quality as manual work
- [ ] **1.2x** - Fewer errors, bugs, or issues than manual
- [ ] **1.5x** - Would not have been feasible to do manually

**Selected:** {{QUALITY_MULTIPLIER}}x

**Justification:** {{QUALITY_JUSTIFICATION}}

### Time Value Formula
```
Time Value = (Manual Hours - Claude Hours) × Hourly Rate × Quality Multiplier
           = ({{MANUAL_HOURS}} - {{CLAUDE_HOURS}}) × ${{HOURLY_RATE}} × {{QUALITY_MULTIPLIER}}
           = {{TIME_SAVED}} × ${{HOURLY_RATE}} × {{QUALITY_MULTIPLIER}}
           = ${{TIME_VALUE}}
```

---

## Strategic Value Calculation

### Impact Score (0-25 points each)

#### 1. Enabled Something New
**Score:** {{IMPACT_NEW}}/25

Did this work enable something that wouldn't have happened otherwise?
- 0 = No, this was routine work
- 12 = Partially, it made something possible that was borderline
- 25 = Absolutely, this unlocked a new capability or opportunity

**Evidence:** {{IMPACT_NEW_EVIDENCE}}

#### 2. Reduced Risk
**Score:** {{IMPACT_RISK}}/25

Did this work reduce business, technical, or operational risk?
- 0 = No risk reduction
- 12 = Moderate risk reduction
- 25 = Significant risk eliminated or mitigated

**Evidence:** {{IMPACT_RISK_EVIDENCE}}

#### 3. Accelerated Timeline
**Score:** {{IMPACT_TIMELINE}}/25

Did this significantly speed up delivery or decision-making?
- 0 = No acceleration
- 12 = Moderate speedup (days saved)
- 25 = Major acceleration (weeks/months saved)

**Evidence:** {{IMPACT_TIMELINE_EVIDENCE}}

#### 4. Improved Decision Quality
**Score:** {{IMPACT_DECISIONS}}/25

Did this lead to better decisions through analysis or insight?
- 0 = No decision impact
- 12 = Informed one or more decisions
- 25 = Fundamentally changed strategy or approach

**Evidence:** {{IMPACT_DECISIONS_EVIDENCE}}

### Strategic Value Formula
```
Total Impact Score = {{IMPACT_NEW}} + {{IMPACT_RISK}} + {{IMPACT_TIMELINE}} + {{IMPACT_DECISIONS}}
                   = {{IMPACT_SCORE}}/100

Strategic Value = Impact Score × $100
                = {{IMPACT_SCORE}} × $100
                = ${{STRATEGIC_VALUE}}
```

---

## Total ROI

```
Total ROI = Time Value + Strategic Value
          = ${{TIME_VALUE}} + ${{STRATEGIC_VALUE}}
          = ${{TOTAL_ROI}}
```

### ROI Summary
| Component | Value |
|-----------|-------|
| Time Value | ${{TIME_VALUE}} |
| Strategic Value | ${{STRATEGIC_VALUE}} |
| **Total ROI** | **${{TOTAL_ROI}}** |

### Context Notes
{{CONTEXT_NOTES}}

---

## Validation Checklist

- [ ] Time estimates are realistic and documented
- [ ] Hourly rate is justified
- [ ] Quality multiplier has clear rationale
- [ ] Impact scores have supporting evidence
- [ ] Total seems reasonable given the scope of work

**Validated by:** {{VALIDATOR}}
**Date:** {{VALIDATION_DATE}}
