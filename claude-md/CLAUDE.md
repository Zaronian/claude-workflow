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
- **Code repos use branch + PR** (`feature/`, `fix/`, `docs/`, `refactor/`). Commit only when asked. Check the business CLAUDE.md for reviewers.
- Never `git push --force` to main. Never `git reset --hard` without confirming uncommitted work is saved. Run `git status` first.

## Safeguards

- Non-git files (databases, configs, data): timestamped backup before modifying (`cp x x.backup-$(date +%Y%m%d-%H%M%S)`).
- `ls` before any `rm -rf`; prefer moving to backup over permanent delete.
- **Production data changes: always pause first** (deploys are fine). Test locally/staging first; have a rollback plan.
- **Always get explicit confirmation before modifying `~/.claude/settings.json`, permissions, or CLAUDE.md workflow rules.**

## Working Style

Push forward autonomously; finish end-to-end (migrations, data population, setup included). Pause only for: irreversible or production-data actions, real design decisions where preference matters, genuinely ambiguous requirements, or settings/permissions/CLAUDE.md changes. When pausing, say *why*. Don't build admin buttons or manual steps that require user action when it can be automated.

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
- **Declare ONE deliverable per session** at the start and state the bigger picture in 2–3 sentences. Plan and implement in the same session when the approach is clear; use plan mode only when the approach is genuinely uncertain. If work outside the deliverable surfaces, note it in the roadmap (Open Questions / future task) rather than doing it in-place.
- **Gates** (`GATE:` items) force a human pause at phase boundaries, before production deploys, and after outputs that need judgment. Defer a gate that can't fire yet; never redefine it weaker.
- **Handoff**: when the deliverable is done, the context is heavy, or the business/project switches — update the roadmap, write the work log, and produce a handoff prompt (deliverable, bigger picture, doc paths, `>>>` task). `pbcopy` it and say "It's on your clipboard."
- `/project new|status|start|end|gate|run` manages the lifecycle. Templates: `~/Knowledge-Base/_system/Templates/`.

## Decision Logs (ADRs)

Projects may keep an append-only ADR log (`decisions/index.md`). **Read the index before design changes in a project that has one**; write a new ADR at session end when the session made a design commitment ("would a future session ask 'why did we do this?'"). Never edit a published ADR — supersede it. ≤1 page each.

## Work Logs

Write a work log at the end of every substantive session (produced a deliverable, made a decision, solved a problem, advanced a project) to the practice's `work-logs/YYYY-MM-DD-[slug].md` using `_system/Templates/work-log-entry-template.md`, naming the business inside. Push to main. Draft the strategic-context section yourself; ask the user the strategic questions only at project milestones. Rates: $35/hr research/admin/planning, $75/hr coding/debugging.

## Communication

- **Tier claims by evidence**: mark each as **Established** (documented/observed), **Plausible** (sound reasoning, thin evidence), or **Inferred** (analogy/judgment). Lead with the strongest. Distinguish "I have data" from "I'm guessing"; ask rather than pad estimates.
- Don't guess without saying so.
- Shell commands the user must run: `pbcopy` them. HTML files: `open` in browser after creating.
- Repeated corrections or streamlinable workflows → suggest a CLAUDE.md/skill change at a natural moment.

## Documentation

After installing tools, cloning repos, changing folder structure, adding credentials, or changing a project's status — update the relevant CLAUDE.md/README. READMEs for automation, multi-file systems, and cross-session work: purpose, status, usage, structure, key decisions.

## Skills

- `/implement <feature>` — plan → code → tests → fresh-context review → report.
