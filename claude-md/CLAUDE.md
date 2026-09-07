# Team Development Standards

Applies to all work across the portfolio. Detailed procedures live in `~/Knowledge-Base/_system/reference/system-guide.md` — read it on demand for project lifecycle, session management, work logging, and system maintenance.

---

## Project Organization

Everything lives under `~/Knowledge-Base/` (docs, one git repo per business) with code in `~/Code/[project]/`. **Read the business's own CLAUDE.md before working on it.**

- New project docs → `~/Knowledge-Base/[business]/projects/`. Ask which business if unclear. Never create project folders at the KB root. Never mix code repos into the KB.
- Each code project may have a `CLAUDE.local.md` (DB config, deploy, test commands) — check for it.

## Secrets

- **Never ask for or accept API keys, tokens, or secrets in chat.** Direct the user to add them to a gitignored `.env` and name the exact var (e.g. "Add `POSTHOG_API_KEY=...` to `~/Knowledge-Base/.env`"). Reference via `${VAR_NAME}` in configs.
- Before starting a task that touches third-party services, list every credential/env var/package it needs up front (with where to find each), then start.
- Never recommend deleting an unfamiliar secret; rotate upstream instead.

## Git

- **KB repos push directly to main** — no branches, no PRs. Committing and pushing work logs, case studies, roadmaps, and project docs at session end is pre-authorized. Keep commits focused. Pre-commit hooks block secrets.
- **Code repos use branch + PR** (`feature/`, `fix/`, `docs/`, `refactor/`). Commit and open a PR when a step is done. **Merge condition = full test suite green + `/pr-review` PASS** (fresh-context review). When both hold: merge, deploy (deploys are fine; additive schema migrations are part of a deploy), verify live, note the deploy in the project's checklist/roadmap, and tell the user in one paragraph. A review that fails twice after fixes → stop and ask. Destructive migrations, data rewrites, and anything touching production *data* still pause.
- Never `git push --force` to main. Never `git reset --hard` without confirming uncommitted work is saved. Run `git status` first.

## Safeguards

- Non-git files (databases, configs, data): timestamped backup before modifying (`cp x x.backup-$(date +%Y%m%d-%H%M%S)`).
- `ls` before any `rm -rf`; prefer moving to backup over permanent delete.
- **Production data changes: always pause first** (deploys are fine). Test locally/staging first; have a rollback plan.
- **Always get explicit confirmation before modifying `~/.claude/settings.json`, permissions, or CLAUDE.md workflow rules.**

## Orchestration (subagents)

- **Default is single-session sequential work.** Use background subagents only for an independent build step with a written brief and a test-based exit condition — never for research/exploration, never a workflow fan-out.
- **Cap: two background agents at a time** — standing allowance, no per-launch approval. Before launching, state the rough cost in session-equivalents and check the remaining session budget (Pacing & budget). The user can stop any agent at any time.
- **Bounded brief** (required): goal; definition of done (tests/commands); files/dirs in scope; constraints (ADRs, patterns); its own worktree; report format (≤1 page: outcome, evidence, PR link, open questions); **stop conditions** — stop and report if tests fail after two attempts, if a decision is needed, or if the approach changes.
- The orchestrator (main session) holds gates, ADRs, roadmap, merges, and deploys. Relay every report; nothing an agent finds reaches the user otherwise.
- **When parallel work would clearly pay for itself, say so** with a cost estimate; the user decides.

## Working Style

Push forward autonomously; finish end-to-end (migrations, data population, setup included). Pause only for: irreversible or production-data actions, real design decisions where preference matters, genuinely ambiguous requirements, or settings/permissions/CLAUDE.md changes. When pausing, say *why*. Don't build admin buttons or manual steps that require user action when it can be automated.

**Continuous mode.** Work one deliverable at a time; when it lands, checkpoint (roadmap `>>>`, work-log append) and start the next `>>>` item without waiting. Stop only at a `GATE:`, a decision only the user can make, a human-only action, or a budget check. When blocked on the user: post a "Need from you" block in the session (numbered, click-by-click), then continue on the next unblocked roadmap item — another phase, another project in the same business, or a parallel item. If a block resolves with time (a deploy has to soak), schedule a wakeup and keep going rather than ending. Produce a handoff prompt only when the session actually ends or the user asks. Demo progress at gates: what changed, evidence it works, what the gate decides.

**Pacing & budget.** At every checkpoint read `~/.claude/usage-data/statusline/sessions/$CLAUDE_CODE_SESSION_ID.json` (written by the statusline; values are as of the last API response — main session only: a subagent inherits the parent's id and must not pace on it). Context < 50 % → continue. 50–70 % → finish + checkpoint, continue only if the next deliverable uses the files already loaded, else hand off. ≥ 70 % → checkpoint + hand off, always (auto-compaction = pacing failure). New session regardless on business/project switch, after a GATE approval, or after ~1 h idle. 5-hour meter ≥ 80 % or 7-day ≥ 85 % → no new agents, finish the current deliverable, checkpoint, pause until `resets_at` and say so.

When something is found mid-work (bug, missing auth check, architectural concern) **file a GitHub issue in the relevant code repo immediately** — conversation summaries are not tracking.

## Projects & Sessions

Size by how many human approval points the work needs, not by session count:

| Size | Shape | Required |
|------|-------|----------|
| **Small** | One sitting, no gate | Nothing — just build it |
| **Medium** | Spans ≥1 gate or ≥2 sittings | Brief + lightweight roadmap |
| **Large** | Multiple phases, each gated | Brief + PRD + phased roadmap |
| **Strategic** | Large + research/discovery phase | Brief + research + PRD + phased roadmap |

- The **roadmap is the project brain** (`>>>` current task, `GATE:` items, Session Context, Artifacts, Session History). Read the Session Context + current phase at session start; link the rest. Update it before ending.
- **Declare the current deliverable** at the start (and again each time you pull the next one) with a 2–3 sentence bigger picture. Plan and implement in the same pass when the approach is clear; use plan mode only when the approach is genuinely uncertain. If work outside the deliverable surfaces, note it in the roadmap (Open Questions / future task) rather than doing it in-place.
- **Gates** (`GATE:` items) force a human pause at phase boundaries, before production deploys, and after outputs that need judgment. Defer a gate that can't fire yet; never redefine it weaker.
- **Checkpoint** after every deliverable: roadmap (`[x]`, `>>>`, Session Context, Artifacts, Session History), append to the day's work log (one file per project per day), ADR if a design commitment was made, commit + push KB. **Handoff** (roadmap + work log + handoff prompt: deliverable, bigger picture, doc paths, `>>>` task) only when the session ends, the business switches, or the user asks — through `handoff.sh` (see Communication) and say "It's on your clipboard."
- **Loose ends**: before every handoff run `/loose-ends` — scan open PRs, uncommitted work, pending deploys/migrations, unanswered "Need from you" items, owed docs/ADRs, dated follow-ups; finish what the rules allow; ask the user once ("do now or queue?") only where it is a real choice; queue the rest in the business's `queue.md` (`~/Knowledge-Base/<business>/queue.md`). Read the queue's **## Open** at session start.
- `/project new|status|start|end|gate|run` manages the lifecycle. Templates: `~/Knowledge-Base/_system/Templates/`.

## Decision Logs (ADRs)

Projects may keep an append-only ADR log (`decisions/index.md`). **Read the index before design changes in a project that has one**; write a new ADR at session end when the session made a design commitment ("would a future session ask 'why did we do this?'"). Never edit a published ADR — supersede it. ≤1 page each.

## Work Logs

Keep one work log per project per day at the practice's `work-logs/YYYY-MM-DD-<project>.md` (template `_system/Templates/work-log-entry-template.md`), naming the business inside; append a section at every checkpoint and at session end for any substantive work (produced a deliverable, made a decision, solved a problem, advanced a project). Push to main. Draft the strategic-context section yourself; ask the user the strategic questions only at project milestones. Rates: $35/hr research/admin/planning, $75/hr coding/debugging.

## Communication

- **Tier claims by evidence**: mark each as **Established** (documented/observed), **Plausible** (sound reasoning, thin evidence), or **Inferred** (analogy/judgment). Lead with the strongest. Distinguish "I have data" from "I'm guessing"; ask rather than pad estimates.
- Don't guess without saying so.
- **Everything copied for the user goes through `~/Knowledge-Base/_system/scripts/handoff.sh <kind> <business/project>`** (kinds: handoff, need-from-you, command, note; body on stdin) — it pbcopys AND stores it under `~/.claude/handoffs/` so `/handoff` can re-surface it after the clipboard is overwritten. HTML files: `open` in browser after creating.
- Repeated corrections or streamlinable workflows → suggest a CLAUDE.md/skill change at a natural moment.

## Documentation

After installing tools, cloning repos, changing folder structure, adding credentials, or changing a project's status — update the relevant CLAUDE.md/README. READMEs for automation, multi-file systems, and cross-session work: purpose, status, usage, structure, key decisions.

## Skills

- `/implement <feature>` — plan → code → tests → fresh-context review → report.
- `/pr-review <PR#|branch>` — fresh-context merge gate: correctness, authz, tests, ADR compliance, scope → PASS or CHANGES. Required before any merge.
- `/handoff [session|business/project|index]` — re-surface the last thing a session copied for the user (from `~/.claude/handoffs/`).
- `/loose-ends [business]` — find what the session left open; finish, ask once, or queue in `<business>/queue.md`. Runs before every handoff.
