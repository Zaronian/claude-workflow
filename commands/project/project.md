# /project — Project Lifecycle Management

Manage multi-session projects with roadmaps, quality gates, and autonomous execution.

## Subcommands

Detect which subcommand the user is invoking from their argument: "$ARGUMENTS"

If no argument or "help", show the available subcommands list below and stop.

---

### `new` — Create a New Project

1. Ask for: entity (which business), project name, and a 2-3 sentence description
2. Read the sizing assessment from `~/Knowledge-Base/_system/Templates/project-brief-template.md`
3. Ask Michael to assess the size (Small / Medium / Large / Strategic) or suggest one based on description
4. Create the project directory: `~/Knowledge-Base/[entity]/projects/[project-name]/`
5. Generate a project brief from the template, filled in with the answers
6. If Medium+, also generate a roadmap from `~/Knowledge-Base/_system/Templates/roadmap-template.md`
7. For Large/Strategic, note that a PRD should be written before execution begins
8. Open the roadmap in Marked 2 if created: `open -a "Marked 2" [roadmap-path]`

### `status` — Show Project Status

1. Find the active roadmap. Check `~/Knowledge-Base/_system/active-gate.md` for a pending gate first.
2. If a gate is pending, show gate details and ask for review.
3. Otherwise, read the roadmap and display:
   - Project name, entity, size, status
   - Current phase and progress (X/Y items done per phase)
   - Current task (the >>> item)
   - Blockers and open questions
   - Last session date and summary

### `start [entity/project]` — Load Project Context for Manual Session

1. Find and read the roadmap at `~/Knowledge-Base/[entity]/projects/[project]/[project]-roadmap.md`
   - Also check `~/Knowledge-Base/[entity]/[project]/[project]-roadmap.md` as fallback
2. Read the Session Context (both HTML comment and human-readable sections)
3. If there's a linked PRD for the current phase, read it
4. Present a brief summary: "Here's where we left off..." with current task, phase, and context
5. Ask "Ready to work on [current task]?" or let Michael redirect

### `end` — Wrap Up Current Session

1. Find the active roadmap (from the project being worked on in this session)
2. Update the roadmap:
   - Mark completed tasks as `[x]`
   - Move `>>>` to the next task
   - Update SESSION-CONTEXT and human-readable Session Context
   - Update Progress table counts
3. Commit the roadmap changes
4. Write a work log entry per standard process (ask strategic questions first)
5. Show what the next session will tackle

### `gate` — Review a Pending Quality Gate

1. Read `~/Knowledge-Base/_system/active-gate.md`
2. If no gate file exists, say "No pending gates" and show current project status instead
3. Present the gate review:
   - What was accomplished leading up to the gate
   - What the gate is asking to verify
   - Links to deliverables
4. Ask Michael to: Approve, Request Changes, or Reject
5. On **Approve**:
   - Mark the gate item as `[x]` in the roadmap
   - Move `>>>` to the next task
   - Delete `_system/active-gate.md`
   - Ask if Michael wants to restart the autonomous runner
6. On **Request Changes**: note what needs to change, keep gate open
7. On **Reject**: note the reason, mark project as paused

### `run [entity/project]` — Start Autonomous Task Runner

1. Find the roadmap for the specified project
2. Show current status: phase, next task, how many non-gate tasks remain
3. Confirm with Michael: "This will run up to N sessions autonomously, stopping at the next gate. Proceed?"
4. Execute: `python3 ~/Knowledge-Base/_system/scripts/run-project.py [entity/project] --max-sessions N`
5. Note: the runner will send macOS notifications at gates or on completion

---

## Available Subcommands Summary

| Command | Purpose |
|---------|---------|
| `/project new` | Create a new project with brief + roadmap |
| `/project status` | Show current project progress |
| `/project start [entity/project]` | Load context for a manual session |
| `/project end` | Update roadmap, write work log, wrap up |
| `/project gate` | Review and approve a pending quality gate |
| `/project run [entity/project]` | Kick off autonomous task runner |
