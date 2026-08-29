# System Reference Guide

Detailed companion to `~/CLAUDE.md`. The global CLAUDE.md holds behavioral rules (what to do); this file holds reference material (how things work, where things are, step-by-step procedures).

**This file is NOT loaded every session.** Read it on demand when working on project lifecycle, session management, work logging, or system maintenance.

---

## Session Discipline

Sessions are organized around a **deliverable**, not a session *type*. A session may plan, write a PRD, code, test, and review in one sitting if the deliverable needs it. (Earlier versions of this kit used a six-type session taxonomy with hard boundaries; that was scaffolding for older models and is retired.)

### Session Lifecycle

1. **Declare** — Read the roadmap's Session Context and the current phase (not the whole file; link the rest). State the one deliverable this session will produce and a 2–3 sentence bigger picture (project status, current phase, what comes after).
2. **Execute** — Do whatever the deliverable needs. Use plan mode only when the approach is genuinely uncertain; if the diff could be described in one sentence, skip planning. If work outside the deliverable surfaces (scope creep, a PRD issue, a new idea), note it in the roadmap's Open Questions or as a future task rather than doing it in-place.
3. **Deliver** — Produce the deliverable and show evidence it works (test output, a running command, a screenshot). Before declaring done on non-trivial code, have a fresh-context subagent review the diff against the plan/PRD for gaps that affect correctness.
4. **Update Roadmap** — Mark completed tasks `[x]`, move `>>>`, update Session Context (both the HTML block and the human section), update the Progress table, register new docs in **Project Artifacts**, add a **Session History** row. Commit.
5. **Handoff** — When ending: a handoff prompt naming the next deliverable, 2–3 sentences of bigger picture, the docs to read, and the current `>>>` task. `pbcopy` it.

### The Roadmap as Project Brain

At any point a reader should know: what's been done (tasks + Session History), what remains (unchecked tasks + Progress), the next step (`>>>` + Session Context), which documents exist (Project Artifacts) and which are relevant now (per-phase links, `next_session_docs`). Every document produced during the project gets registered in Project Artifacts when created.

### Keeping the Bigger Picture

- The Session Context section stays within the first 40 lines of the roadmap.
- Handoff prompts always carry bigger-picture context.
- **Gates** at phase boundaries are where human review happens; a fresh-context verifier subagent runs before each gate (the runner does this automatically; do it manually in interactive sessions).
- Roadmap updates happen every session.

### Autonomy Detail

Default: push forward and finish end-to-end. Pause only for irreversible/production-data actions, real design choices, genuine ambiguity, or settings/permissions/CLAUDE.md changes — and say why. Do not pause for dev servers, tests, builds, routine code changes, standard git operations on KB repos, searches, or the obvious next step.

Before starting a task involving third-party services: audit the full task for every credential, env var, package, or external service; present the complete list once (with where to find each); then begin. Never accept secrets in chat.

---

## Work Logging — Process Detail

Work logs and case studies live in the practice's KB folder (e.g. `~/Knowledge-Base/<practice>/work-logs/`) regardless of which business the work was for — the practice is where progress, ROI, and case studies aggregate. Name the business in the entry.

- Write one at the end of every substantive session; skip only trivial/conversational sessions.
- Follow `_system/Templates/work-log-entry-template.md`. Draft the Strategic Impact section yourself and mark it as drafted; ask the user "What does this unlock?" / "How does it fit the bigger picture?" only at project milestones (phase completion, gates, project close).
- Push directly to main. `/log-work` reviews or supplements an entry.
- Hook-generated activity data (`work-logger.py` PostToolUse → `<business>/work-logs/YYYY-MM.jsonl`; `session-summary.py` Stop → per-session rollup) is the raw layer; the markdown entry captures outcomes, decisions, time saved, and learnings that hooks can't.

---

## Architectural Decision Logs — Discipline Rules

1. **Read at session start.** Any session touching a project with a decision log begins by reading `index.md`; grep it for the area you're about to work on.
2. **Append-only.** Never edit a published ADR. If a decision changes, write a new ADR that supersedes it and mark the old one `Superseded by ADR-NNN`.
3. **Write at session end.** A new design commitment (A over B, a locked constraint, a non-goal, a codified lesson) gets an ADR before wrapping up.
4. **The trigger.** "Would a future session ask 'wait, why did we do this?'" If it fits in a one-line commit message, it's too small.
5. **Short.** ≤1 page.

---

## Documentation Maintenance

Update after: new tools installed, repos cloned, folder-structure changes, new credentials, new team members/processes, project status changes. Candidates: `~/CLAUDE.md`, `~/Knowledge-Base/[business]/CLAUDE.md`, project READMEs.

README needed for: automation/scripts/multi-file systems, multi-step workflows, cross-session work, new multi-file directories. Not needed for single-file obvious scripts or temporary work.

---

## Roadmap Format Specification

Roadmaps use machine-readable HTML comments and human-readable markdown:
- `<!-- ROADMAP-META -->` — project-level metadata (entity, repo, size, status)
- `<!-- SESSION-CONTEXT -->` — cross-session state (last task, next task, next deliverable, docs, blockers)
- `<!-- PHASE -->` — per-phase metadata
- `>>>` marker — current in-progress task (only one at a time)
- `GATE:` prefix — quality gate (task runner stops here)
- Standard `- [x]`/`- [ ]` checkboxes for progress tracking

See `_system/Templates/roadmap-template.md` for the full template.

---

## Autonomous Task Runner

`_system/scripts/run-project.py` reads the roadmap and runs Claude CLI **to the next gate in one invocation**:
- Finds the `>>>` task and every unchecked task up to the next `GATE:`; passes Session Context + current phase + linked PRD (not the full roadmap) and the roadmap path so Claude can read more if needed
- Runs `claude -p --permission-mode auto` with a multi-hour timeout (`--timeout-hours`, default 4), streaming output to `~/.claude/scripts/project-runner.log`
- Instructs Claude to update `>>>` after each task, ground every progress claim in a tool result, and — on reaching the gate — run a fresh-context verifier subagent that writes `gate-verification.md` next to the roadmap
- Writes `_system/active-gate.md` (including the verifier's findings) and opens a gate-review Claude session
- Re-invokes (up to `--max-runs`, default 3) only if a run ends before the gate; stops if `>>>` didn't move (stuck), on non-zero exit, or on timeout

Set `KB_WORKLOG_DIR` to override where the runner tells Claude to write the run's work log (default `~/Knowledge-Base/<practice>/work-logs/` per the kit's example config).

---

## Project Lifecycle Files

| File | Purpose |
|------|---------|
| `_system/Templates/roadmap-template.md` | Roadmap format with machine-readable metadata |
| `_system/Templates/project-brief-template.md` | Sizing assessment + kickoff document |
| `_system/scripts/run-project.py` | Autonomous task runner |
| `_system/scripts/open-roadmap.sh` | Open roadmap in viewer app |
| `.claude/commands/project.md` | `/project` slash command |
| `_system/active-gate.md` | Written by runner when a gate is reached |

---

## Git Workflow — Step by Step

```
1. git checkout -b feature/description-of-work
2. Edit, test locally
3. git add [files] && git commit -m "Description of what changed"
4. git push -u origin feature/description-of-work
5. gh pr create --title "Title" --body "Description"
6. Reviewer approves and merges
7. git checkout main && git pull && git branch -d feature/description-of-work
```

Recovery: `git reflog` (lost commits), `git stash list` / `git stash pop`, `git checkout -- <file>`.

---

## Safeguards — Details

- **Pre-commit secret detection** (`~/.scratch/hooks/pre-commit-secrets`): blocks `.env`, `*.pem`/`*.key`/credentials files, inline passwords/API keys, connection strings with credentials. Install per repo: `cp ~/.scratch/hooks/pre-commit-secrets .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit`. Bypass for false positives: `git commit --no-verify`.
- **Database backups**: `<project>/backups/database.db.backup-YYYYMMDD-HHMMSS-<reason>`, last 10 kept.
- **Scratch dir** `~/.scratch/` for reusable hooks and temporary backups of non-project files.

---

## Testing Conventions

Test the happy path, edge cases (empty data, missing fields, boundaries), error handling (invalid input, not found), and integration points. Check the project's `CLAUDE.local.md` for the test command. Run the suite before pushing.
