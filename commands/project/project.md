# /project — Project Lifecycle Management

Manage multi-session projects with roadmaps, quality gates, and autonomous execution. Sessions are organized around a **deliverable**, not a session type (see `_system/reference/system-guide.md`).

## Subcommands

Detect which subcommand the user is invoking from their argument: "$ARGUMENTS"

If no argument or "help", show the subcommands summary at the bottom and stop.

---

### `new` — Create a New Project

1. Ask for: business (entity), project name, and a 2-3 sentence description
2. Read the sizing assessment in `~/Knowledge-Base/_system/Templates/project-brief-template.md` (size = how many human approval points the work needs, not session count)
3. Suggest a size (Small / Medium / Large / Strategic) and confirm with the user
4. Create `~/Knowledge-Base/[entity]/projects/[project-name]/`
5. Generate the project brief from the template
6. If Medium+, generate a roadmap from `~/Knowledge-Base/_system/Templates/roadmap-template.md`:
   - Phase each task; put a `GATE:` item at every phase boundary and before any production deploy
   - Initialize Project Artifacts with the brief; set `next_task` and `next_session_deliverable` in SESSION-CONTEXT; add row 1 to Session History
   - Task tags are optional hints, not required
7. For Large/Strategic, note that a PRD is written before execution begins (can be the first session's deliverable)
8. Open the roadmap in the viewer: `bash ~/Knowledge-Base/_system/scripts/open-roadmap.sh [roadmap-path]`

### `status` — Show Project Status

1. Check `~/Knowledge-Base/_system/active-gate.md` first. If a gate is pending, show it and offer `/project gate`.
2. Otherwise read the roadmap's Session Context + Progress table and display: name, entity, size, status; current phase and per-phase progress; the `>>>` task; next deliverable; blockers and open questions; last session date and summary; artifact count.

### `start [entity/project]` — Load Project Context

0. Read the business's queue (`~/Knowledge-Base/<business>/queue.md` **## Open**) — short by design; surface anything relevant to the deliverable.

1. Find the roadmap at `~/Knowledge-Base/[entity]/projects/[project]/[project]-roadmap.md` (fallback `~/Knowledge-Base/[entity]/[project]/...`)
2. Read the Session Context (HTML block + human section) and the **current phase section** — not the whole roadmap; read further only if needed
3. Read `next_session_docs` and any linked PRD for the current phase
4. If the project has a decision log, grep its index for the area about to be touched
5. Present:
   > **This session's deliverable:** [from `next_session_deliverable` / the `>>>` task]
   > **Bigger picture:** 2-3 sentences — overall progress (e.g. "Phase 1: 4/8 done, Phases 2-3 not started"), where this session fits, what comes after
6. Ask "Start on [current task]?" or let the user redirect

### `end` — Wrap Up Current Session

Use when the session is actually ending (continuous mode otherwise checkpoints and pulls the next `>>>` — see `~/CLAUDE.md` § Working Style).

1. Find the active roadmap
2. **Verify the deliverable** was produced; point to evidence (test output, files, commands run)
3. Update the roadmap: mark `[x]`, move `>>>`, update SESSION-CONTEXT (`last_session_date`, `next_task`, `next_session_deliverable`, `next_session_docs`, `blockers`, `notes`) and the human Session Context, update Progress counts, register new docs in Project Artifacts, add a Session History row
4. Commit the roadmap (KB repos push to main directly)
5. If the session made a design commitment and the project has a decision log, write the ADR
6. Write the work log (draft strategic context yourself; ask the strategic questions only at milestones)
6b. Run `/loose-ends` — finish what the rules allow, ask once where it is a real choice, queue the rest in `<business>/queue.md`
7. Generate the handoff prompt — next deliverable, 2-3 sentences of bigger picture, docs to read, the `>>>` task — pipe it through `~/Knowledge-Base/_system/scripts/handoff.sh handoff <entity/project>` (pbcopy + `~/.claude/handoffs/`), show it, and say "It's on your clipboard."

### `gate` — Review a Pending Quality Gate

1. Read `~/Knowledge-Base/_system/active-gate.md`. If absent: "No pending gates" + `status`.
2. Present: what was accomplished leading to the gate, what the gate verifies, links to deliverables, the **verifier findings** (`gate-verification.md` next to the roadmap, if present), and Session History for this phase
3. Ask the user: Approve / Request Changes / Reject
4. **Approve** → mark the gate `[x]`, move `>>>`, delete `_system/active-gate.md`, set `next_session_deliverable` for the next phase, offer to restart the runner
5. **Request Changes** → record what must change; keep the gate open
6. **Reject** → record the reason; mark the project paused

### `run [entity/project]` — Start Autonomous Runner

1. Find the roadmap; show phase, `>>>` task, and how many tasks remain before the next gate
2. Confirm: "This will run autonomously to the next gate (up to N hours). Proceed?"
3. Execute in the background: `python3 ~/Knowledge-Base/_system/scripts/run-project.py [entity/project] [--timeout-hours N]`
4. The runner notifies at the gate, on error, or on completion; log at `~/.claude/scripts/project-runner.log`

---

## Available Subcommands Summary

| Command | Purpose |
|---------|---------|
| `/project new` | Create a project with brief + roadmap |
| `/project status` | Show progress and next deliverable |
| `/project start [entity/project]` | Load context, declare the deliverable, begin |
| `/project end` | Verify deliverable, update roadmap, work log, handoff |
| `/project gate` | Review and approve a pending quality gate |
| `/project run [entity/project]` | Run autonomously to the next gate |
