<!-- ROADMAP-META
project: [Project Name]
entity: [burn-app | v-school | smash-creative | snowline | volley]
size: [small | medium | large | strategic]
repo: ~/Code/[project]/
status: [planning | active | paused | complete]
created: YYYY-MM-DD
target: YYYY-MM-DD
-->

# [Project Name] — Roadmap

**Entity:** [Business Name]
**Size:** [Small/Medium/Large/Strategic]
**Status:** [Planning/Active/Paused/Complete]
**Target:** YYYY-MM-DD

<!-- SESSION-CONTEXT
last_session: YYYY-MM-DD
last_task: [ID of last completed task, e.g. 1.3]
next_task: [ID of next task, e.g. 1.4]
blockers: [none | description of blocker]
notes: [Brief context for the next session — what happened, what to do next]
-->

## Session Context

**Last session:** YYYY-MM-DD — [one-line summary of what was accomplished]
**Next up:** [description of what the next session should tackle]
**Blockers:** None

---

## Progress

| Phase | Status | Items Done | Items Total |
|-------|--------|------------|-------------|
| 1. [Phase Name] | Not Started | 0 | X |
| 2. [Phase Name] | Not Started | 0 | X |
| 3. [Phase Name] | Not Started | 0 | X |

---

## Phase 1: [Phase Name]

**Goal:** [What this phase delivers]
**PRD:** [Link to PRD if applicable, e.g. `../docs/phase-1-prd.md`]

<!-- PHASE id=1 status=not_started -->

- [ ] >>> 1.1 [First task description]
- [ ] 1.2 [Second task description]
- [ ] 1.3 [Third task description]
- [ ] GATE: [Review/approval checkpoint — describe what to verify]

### Phase 1 Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

---

## Phase 2: [Phase Name]

**Goal:** [What this phase delivers]
**PRD:** [Link to PRD if applicable]

<!-- PHASE id=2 status=not_started -->

- [ ] 2.1 [First task description]
- [ ] 2.2 [Second task description]
- [ ] 2.3 [Third task description]
- [ ] GATE: [Review/approval checkpoint]

### Phase 2 Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

---

## Phase 3: [Phase Name]

**Goal:** [What this phase delivers]

<!-- PHASE id=3 status=not_started -->

- [ ] 3.1 [First task description]
- [ ] 3.2 [Second task description]
- [ ] GATE: [Final review checkpoint]

### Phase 3 Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

---

## Timeline Overview

| Milestone | Target Date | Status |
|-----------|------------|--------|
| Phase 1 complete | YYYY-MM-DD | Pending |
| Phase 2 complete | YYYY-MM-DD | Pending |
| Phase 3 complete | YYYY-MM-DD | Pending |
| Project complete | YYYY-MM-DD | Pending |

---

## Decisions Log

| # | Date | Decision | Rationale |
|---|------|----------|-----------|
| 1 | YYYY-MM-DD | [What was decided] | [Why] |

---

## Open Questions

- [ ] [Question that needs answering before proceeding]
- [ ] [Another open question]

---

## Linked Artifacts

- **Project Brief:** [path to brief]
- **PRD(s):** [paths to PRDs]
- **Work Logs:** [paths or glob pattern, e.g. `~/Knowledge-Base/snowline/work-logs/2026-*-project-name*`]
- **Code Repo:** [path to code repository]

---

<!--
USAGE NOTES (delete this section when creating a real roadmap):

File naming:
  Save as [project-name]-roadmap.md (e.g., command-center-roadmap.md)
  This ensures the project name is visible in Marked 2's title bar.

Markers:
  >>> — Place before the current in-progress task (only one at a time)
  GATE: — Quality gate; the task runner stops here for human review
  [x] — Completed item
  [ ] — Pending item

Machine-readable blocks:
  ROADMAP-META — Project-level metadata (top of file)
  SESSION-CONTEXT — State for cross-session continuity (updated after each session)
  PHASE — Phase-level metadata (before each phase's task list)

Task IDs:
  Use [phase].[sequence] format (e.g., 1.1, 1.2, 2.1)
  Referenced in SESSION-CONTEXT for tracking

The task runner (run-project.py) reads this file to:
  1. Find the >>> current task
  2. Check if it's a GATE (stop) or regular task (execute)
  3. Generate a prompt with full context
  4. After execution, verify the roadmap was updated

Keep the Session Context section within the first 30 lines so Claude
finds current state immediately when loading the roadmap.
-->
