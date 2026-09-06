# System Reference Guide

Detailed companion to `~/CLAUDE.md`. The global CLAUDE.md holds behavioral rules (what to do); this file holds reference material (how things work, where things are, step-by-step procedures).

**This file is NOT loaded every session.** Read it on demand when working on project lifecycle, session management, work logging, or system maintenance.

---

## Session Discipline

Sessions are organized around a **deliverable**, not a session *type*. A session may plan, write a PRD, code, test, and review in one sitting if the deliverable needs it. (Earlier versions of this kit used a six-type session taxonomy with hard boundaries; that was scaffolding for older models and is retired.)

### The Continuous Loop

The unit of work is the **deliverable**, not the session. A session runs this loop until a stop condition fires:

```
Declare → Execute → Deliver (tests + /pr-review PASS) → Merge + deploy + verify → Checkpoint (roadmap, work-log append, ADR) → pull the next `>>>` → …
```

1. **Declare** — Read the roadmap's Session Context and the current phase (not the whole file; link the rest). State the deliverable and a 2–3 sentence bigger picture. Repeat each time the next `>>>` is pulled.
2. **Execute** — Whatever the deliverable needs. Plan mode only when the approach is genuinely uncertain; if the diff could be described in one sentence, skip planning. Work outside the deliverable → roadmap Open Questions / future task, not in-place.
3. **Deliver** — Evidence it works (test output, a running command, a screenshot). Code: full suite green + `/pr-review` PASS is the merge condition; then merge, deploy (additive migrations included), verify live, note the deploy in the project's checklist/roadmap, tell the user in one paragraph. Two CHANGES verdicts → stop and ask.
4. **Checkpoint** — Mark `[x]`, move `>>>`, update Session Context (HTML block + human section), Progress table, **Project Artifacts**, **Session History**; append to the day's work log (`work-logs/YYYY-MM-DD-<project>.md`, one file per project per day, one section per deliverable); ADR if a design commitment was made; commit + push the KB.
5. **Continue or stop.** Stop conditions: a `GATE:` (demo what changed, evidence, what the gate decides); a decision only the user can make; a human-only action — post a numbered, click-by-click "Need from you" block through `handoff.sh need-from-you` and continue on the next unblocked item; a budget check (see Pacing); session end.
6. **Waiting well.** Time-resolved blocks → a scheduled wakeup / `/loop` and keep going. User-resolved blocks → work elsewhere in the roadmap. Nothing unblocked → hand off.
7. **Loose ends** — Before the handoff run `/loose-ends`: scan open PRs, uncommitted work and stale worktrees, pending deploys/migrations, unanswered "Need from you" items, owed docs/ADRs/work logs, dated follow-ups, orphan issues. Finish what the rules allow; ask the user once ("do now or queue?") only where it is a real choice; queue the rest in the business's `queue.md` (`~/Knowledge-Base/<business>/queue.md`) — one actionable line per item, newest first, moved to **## Done** when closed. Session start reads the queue's **## Open**. A future triage agent prioritizes across businesses.
8. **Handoff** — Only when the session ends, the business switches, or the user asks: next deliverable, 2–3 sentences of bigger picture, docs to read, the `>>>` task, through `handoff.sh handoff <business/project>` (pbcopy + `~/.claude/handoffs/`). `/handoff` re-surfaces it later for one file read.

### Pacing & budget gauges

`~/.claude/statusline.sh` writes Claude Code's status JSON to `~/.claude/usage-data/sessions/<session_id>.json` (and `latest.json`) on every event and every 30 s (`refreshInterval`); the session id is `$CLAUDE_CODE_SESSION_ID`. Read it at every checkpoint:

| Gauge | Rule |
|---|---|
| `context_window.used_percentage` < 50 | continue |
| 50–70 | finish + checkpoint; continue only if the next deliverable uses the loaded files, else hand off |
| ≥ 70 | checkpoint + hand off, always — auto-compaction is a pacing failure, not a tool |
| any | new session on business/project switch, after a GATE approval, or after ~1 h idle (prompt cache expired) |
| `rate_limits.five_hour.used_percentage` ≥ 80 | no new agents; finish the current deliverable; checkpoint; pause until `resets_at` and say so |
| `rate_limits.seven_day.used_percentage` ≥ 85 | same, and tell the user explicitly |

Why compaction is not a strategy: every turn re-sends the whole context, so a 70 %-full session costs several times a fresh one per turn, and the automatic summary is generic where the roadmap + handoff prompt are targeted.

### Orchestration (subagents)

Rules live in `~/CLAUDE.md` § Orchestration (two-agent standing cap, bounded brief, orchestrator holds gates/ADRs/roadmap/merges). Brief template:

```
Goal: <one sentence>
Done when: <tests/commands that must pass>
Scope: <files/dirs>; worktree: <path> (detached from origin/main)
Constraints: <ADRs, patterns, CLAUDE.local.md notes>
Stop and report if: tests fail after two attempts | a decision is needed | the approach changes
Report (≤1 page): outcome · evidence (actual test output) · PR link · open questions
```

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
