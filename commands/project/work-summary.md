# Work Summary Command

Show a summary of recent work across all entities.

## Instructions

When the user runs `/work-summary`, generate a comprehensive overview of recent work.

### 1. Scan All Work Logs

Check each entity's work-logs directory:
- burn-app/work-logs/
- lightswitch/work-logs/
- v-school/work-logs/
- smash-creative/work-logs/
- volley/work-logs/

### 2. Read Recent Entries

For each entity with work logs:
- Read the current month's JSONL file (YYYY-MM.jsonl)
- Also check last month if near the beginning of a month
- Parse all entries

### 3. Generate Summary

Create a summary organized by entity:

```markdown
# Work Summary

**Period:** [Date range covered]
**Generated:** [Current date]

---

## Overview

| Entity | Sessions | Projects | Hours Saved | Est. ROI |
|--------|----------|----------|-------------|----------|
| V School | 5 | 2 | 36 hrs | $5,400 |
| Burn App | 3 | 1 | 12 hrs | $1,800 |
| **Total** | **8** | **3** | **48 hrs** | **$7,200** |

---

## By Entity

### V School

**Projects:**
- University Partnership Tool (3 sessions)
  - Research and comparison framework
  - 50 universities analyzed
  - ROI: $4,200

- Curriculum Documentation (2 sessions)
  - Course outlines standardized
  - ROI: $1,200

**Recent Activity:**
- Jan 28: Built university search interface
- Jan 27: Completed partnership criteria matrix
- Jan 26: Initial research framework

---

### Burn App

**Projects:**
- Feature Planning (3 sessions)
  - Product roadmap review
  - ROI: $1,800

**Recent Activity:**
- Jan 25: Competitor analysis
- Jan 24: Feature prioritization

---

## Ready for Case Studies

The following have enough logged context for case study generation:

1. **V School - University Partnership Tool** (3 sessions, ROI logged)
   Run: `/case-study` and select V School

2. **Burn App - Feature Planning** (3 sessions, ROI logged)
   Run: `/case-study` and select Burn App

---

## Notes

- Run `/log-work` to add context to recent sessions
- Run `/case-study` to generate marketing materials
```

### 4. Highlight Opportunities

Call out:
- Entities/projects ready for case study generation
- Sessions without manual context (suggest /log-work)
- High-ROI work that should be documented

### 5. Display Summary

Present the summary in a clear, scannable format.

## Data Aggregation

When calculating totals:

**Hours Saved:**
```
Sum of (manual_hours - claude_hours) across all manual_context entries
```

**Estimated ROI:**
```
Time Value = Hours Saved × $150 × Avg Quality Multiplier
Strategic Value = Sum of Impact Scores × $100
```

**Session Count:**
- Count unique session_ids
- Or count session_summary entries

## Notes

- Keep the summary scannable and actionable
- Highlight what's ready for case studies
- Show trends if multiple months of data exist
- Default to current month, offer to expand range if asked
