# Case Study Generation Command

Generate a case study from work logs for Snowline Consulting marketing.

## Instructions

When the user runs `/case-study`, follow this workflow:

### 1. Select Entity and Project

First, scan the work-logs directories to see which entities have logged work:

```bash
# Check each entity for work logs
ls -la "burn-app/work-logs/"
ls -la "snowline/work-logs/"
ls -la "v-school/work-logs/"
```

Present options to the user:
- Which entity to generate a case study for
- Which project/time period to cover

### 2. Read Work Log Entries

Read the relevant JSONL files and extract entries:
- Filter by project if specified
- Sort by timestamp
- Identify manual_context entries (from /log-work)
- Identify session_summary entries
- Identify tool usage patterns

### 3. Aggregate Data

Calculate totals:
- Total manual hours estimated
- Total Claude hours
- Time saved
- Average quality multiplier
- Total impact score
- Calculate ROI using the formula

### 4. Read Template

Read the case study template:
```
_system/Templates/case-study-template.md
```

### 5. Generate Draft

Fill in the template with:
- Background from project context
- Challenge from problem statements in logs
- Solution from work summaries
- Results from outcomes
- ROI from calculations
- Work log references

### 6. Review Loop

Present the draft to the user and iterate:

"Here's the draft case study. Please review:

[Show draft]

What would you like to change?
- [ ] Challenge description
- [ ] Solution details
- [ ] Results emphasis
- [ ] ROI adjustments
- [ ] Tone/messaging
- [ ] Looks good, save it"

### 7. Save Final Version

Once approved, save to:
```
[entity-folder]/case-studies/YYYY-MM-project-name.md
```

Also create a one-page overview:
```
[entity-folder]/case-studies/YYYY-MM-project-name-overview.md
```

### 8. Confirmation

Confirm to user:
- Full case study saved at: [path]
- One-page overview saved at: [path]
- Suggest next steps (share with marketing, add to portfolio, etc.)

## ROI Calculation

Use this formula when aggregating:

```
Time Value = (Total Manual Hours - Total Claude Hours) × $150/hr × Avg Quality Multiplier

Strategic Value = Total Impact Score × $100

Total ROI = Time Value + Strategic Value
```

Default hourly rate: $150 (can be adjusted based on entity)

## Example Output Structure

```markdown
# Case Study: University Partnership Tool

**Entity:** V School
**Project:** University Partnership Research Tool
**Date Range:** January 2026
**Generated:** 2026-01-28

---

## One-Page Overview

### The Challenge
V School needed to research and compare 50+ potential university partners...

### The Solution
Built an AI-powered research tool that...

### The Results
- Researched 50 universities in 2 days vs estimated 2 weeks
- Identified 12 high-priority partnership targets
- Created standardized comparison framework

### ROI Snapshot
- **Time Saved:** 72 hours
- **Value Created:** $14,400
- **Quality Impact:** 1.2x

---

[Full case study continues...]
```

## Notes

- Always include work log references for traceability
- Keep language professional but compelling
- Focus on business outcomes, not technical details
- Make ROI claims specific and defensible
- Include lessons learned for credibility
