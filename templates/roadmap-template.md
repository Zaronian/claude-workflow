<!-- ROADMAP-META
project: [Project Name]
entity: [business-a | business-b | practice]
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
last_session_date: YYYY-MM-DD
last_task: [ID of last completed task, e.g. 1.3]
next_task: [ID of next task, e.g. 1.4]
next_session_deliverable: [What the next session should produce]
next_session_docs: [Comma-separated paths to docs the next session needs]
blockers: [none | description of blocker]
notes: [Brief context for the next session]
-->

## Session Context

**Tool:** [which coding agent currently owns this project; switch only at a checkpoint]
**Last session:** YYYY-MM-DD — [one-line summary of what was accomplished]
**Next session deliverable:** [what the next session should produce]
**Relevant docs:** [links to documents needed for the next session]
**Blockers:** None

---

## Project Artifacts

All documents produced during this project. Updated every session.

| Document | Type | Status | Phase | Path |
|----------|------|--------|-------|------|
| Project Brief | brief | final | — | [project-name]-brief.md |
| _[Add rows as documents are created]_ | | | | |

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
**PRD:** [Link to PRD if applicable, e.g. `docs/phase-1-prd.md`]
**Relevant docs:** [Links to specs, designs, or other docs for this phase]

<!-- PHASE id=1 status=not_started -->

- [ ] >>> 1.1 [First task description] `roadmap`
- [ ] 1.2 [Second task description]
- [ ] 1.3 [Third task description] `prd`
- [ ] 1.4 [Fourth task description] `plan`
- [ ] 1.5 [Fifth task description] `implement`
- [ ] GATE: [Review/approval checkpoint — describe what to verify] `review`

### Phase 1 Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

---

## Phase 2: [Phase Name]

**Goal:** [What this phase delivers]
**PRD:** [Link to PRD if applicable]
**Relevant docs:** [Links to relevant docs]

<!-- PHASE id=2 status=not_started -->

- [ ] 2.1 [First task description] `[session-type]`
- [ ] 2.2 [Second task description] `[session-type]`
- [ ] 2.3 [Third task description] `[session-type]`
- [ ] GATE: [Review/approval checkpoint] `review`

### Phase 2 Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

---

## Phase 3: [Phase Name]

**Goal:** [What this phase delivers]
**Relevant docs:** [Links to relevant docs]

<!-- PHASE id=3 status=not_started -->

- [ ] 3.1 [First task description] `[session-type]`
- [ ] 3.2 [Second task description] `[session-type]`
- [ ] GATE: [Final review checkpoint] `review`

### Phase 3 Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

---

## Session History

| # | Date | Type | Deliverable | Tasks |
|---|------|------|-------------|-------|
| 1 | YYYY-MM-DD | roadmap | Initial roadmap created | — |

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

<!--
USAGE NOTES (delete this section when creating a real roadmap):

File naming:
  Save as [project-name]-roadmap.md (e.g., command-center-roadmap.md)
  This ensures the project name is visible in Marked 2's title bar.

Task tags (optional hints, e.g. `prd`, `implement`, `review`):
  Sessions are organized by deliverable, not type (revised 2026-08-29).
  A tag may note what kind of work a task is, but a session may plan,
  write, code, test, and review in one sitting if the deliverable needs it.

Markers:
  >>> — Place before the current in-progress task (only one at a time)
  GATE: — Quality gate; the task runner stops here for human review
  [x] — Completed item
  [ ] — Pending item

Project Artifacts table:
  Register every document produced during the project (PRDs, plans, READMEs,
  specs, designs). Update this table whenever a new document is created.
  Types: brief, prd, plan, spec, design, readme, guide, other

Session History table:
  Add a row at the end of every session. This creates an audit trail and
  helps future sessions understand the project's progression.

Machine-readable blocks:
  ROADMAP-META — Project-level metadata (top of file)
  SESSION-CONTEXT — State for cross-session continuity (updated after each session)
    - next_task / next_session_deliverable tell the next session what to produce
    - next_session_docs lists documents the next session needs to read
    - The runner (run-project.py) reads this block plus the current phase
  PHASE — Phase-level metadata (before each phase's task list)

Task IDs:
  Use [phase].[sequence] format (e.g., 1.1, 1.2, 2.1)
  Referenced in SESSION-CONTEXT for tracking

The task runner (run-project.py) reads this file to:
  1. Find the >>> current task
  2. Check if it's a GATE (stop) or regular task (execute)
  3. Generate a prompt with full context
  4. After execution, verify the roadmap was updated

Keep the Session Context section within the first 40 lines so Claude
finds current state immediately when loading the roadmap.
-->
