# Philosophy: The Snowline Claude Workflow System

This document explains **why** each piece of the workflow exists. Installing the files is the easy part — understanding the system is what makes it work.

---

## The Problem

Every Claude Code session starts from scratch. Decisions made, context gathered, and ROI generated all evaporate when the session ends. Over weeks of daily use, this creates three compounding problems:

1. **Context loss** — You re-explain the same project structure, preferences, and conventions every session
2. **Invisible ROI** — Hours saved and value created are never captured, making it impossible to justify or demonstrate the tool's impact
3. **Unstructured work** — Multi-session projects lose momentum because there's no system tracking what was done, what's next, and what was decided

The workflow system solves all three.

---

## The Solution: Three Layers

### Layer 1: CLAUDE.md (Behavioral Guardrails)

The `~/CLAUDE.md` file is Claude's operating manual — it reads this at the start of every session. Instead of re-explaining your preferences each time, you encode them once:

**Push forward autonomously.** The single biggest productivity gain. By default, Claude should do as much as possible without stopping. Every pause for permission is wasted time. The CLAUDE.md encodes precise rules for when to stop:
- Security-sensitive operations (production deploys, data deletion)
- Design decisions with multiple valid approaches
- Ambiguous requirements
- Explicit user request to slow down

Everything else — running tests, making commits, searching the web, executing builds — just do it.

**Gather credentials upfront.** Nothing kills momentum like discovering you need an API key mid-implementation. The CLAUDE.md instructs Claude to audit the full task for every dependency before starting execution, present the complete list, and let you gather them while it works on parts that don't need credentials.

**Session handoffs.** Claude proactively recognizes natural breakpoints (planning → building shift, heavy context window, entity/project switch) and suggests ending the session with a prompt ready for the next one. This prevents the degraded performance that comes from overloaded context windows.

**Safety as a system, not a prompt.** Instead of hoping Claude remembers to be careful, the CLAUDE.md defines structural safeguards: always check `git status` before destructive operations, never force-push to main, backup databases before modification. These are always-on — not things you need to remember to ask for.

### Layer 2: Hooks & Scripts (Automated Tracking)

Hooks run automatically without any human action:

**work-logger.py** (PostToolUse hook) — After every significant tool use (Edit, Write, Bash, Read, Grep, etc.), this hook logs a structured entry to a JSONL file. It detects which business entity the work belongs to based on file paths and routes the log to the correct entity's `work-logs/` directory. You never need to manually track what Claude did.

**session-summary.py** (Stop hook) — When Claude stops, this hook reads all the tool-use logs from the current session and writes a consolidated summary. This is the raw data that feeds into work logs and case studies.

**notify.sh** (Notification + Stop hook) — Plays different macOS sounds for different events: a ping when Claude needs permission approval, a funk sound when a task completes. This means you can work on something else while Claude runs and know when it's done or needs you.

**statusline.sh** — Shows the current model, context window usage percentage, session cost, and git branch in Claude's status bar. The context percentage is particularly valuable — when it hits 70%+, performance degrades, and you should consider a session handoff.

**daily-review.sh** — A script (run manually or via cron) that generates an HTML report analyzing the day's work across all entities, identifying patterns and suggesting improvements.

### Layer 3: Templates & Commands (Structured Workflows)

Templates provide consistent structure for recurring artifacts:

**Roadmap template** — The backbone of multi-session projects. Uses machine-readable HTML comments (`ROADMAP-META`, `SESSION-CONTEXT`, `PHASE`) alongside human-readable markdown. The `>>>` marker shows the current task; `GATE:` prefixes mark quality checkpoints.

**Project brief template** — A lightweight sizing document that determines how much ceremony a project needs. Small projects (< 1 day) skip everything and just build. Strategic projects (4+ weeks) get a full brief, PRD, and phased roadmap with gates.

**Work log template** — Captures what was accomplished, problems solved, time saved (with rate tiers: $35/hr for research, $75/hr for development), strategic impact, and carry-forward items.

**Case study template** — Transforms accumulated work logs into marketing-ready case studies with ROI calculations.

Slash commands provide one-invocation access to complex workflows:

- `/project new` — Creates a project with brief + roadmap based on sizing
- `/project start` — Loads context from the roadmap for a manual session
- `/project end` — Updates the roadmap, writes work log, preps next session
- `/project run` — Starts the autonomous task runner
- `/implement` — Full feature workflow: plan → code → test → report
- `/log-work` — Review or create a manual work log entry
- `/case-study` — Generate a case study from accumulated logs
- `/work-summary` — Cross-entity summary with ROI totals

---

## The Planning Workflow

This is the biggest productivity multiplier in the entire system. The key insight: **your time is 10x more valuable reviewing plans than generating code.**

For non-trivial work, use a multi-layered planning approach:

### 1. Size the Project (Brief)

Use the project brief template to assess: is this Small (just build it), Medium (brief + roadmap), Large (brief + PRD + roadmap + gates), or Strategic (all of the above + research)?

### 2. Roadmap

For Medium+ projects, create a roadmap with phases, tasks, and gates. The roadmap is the single source of truth for project state — the "project brain." It uses machine-readable HTML comments so the autonomous runner can parse it, and human-readable markdown so you can review it in a viewer.

### 3. Phase PRD

For Large/Strategic projects, write a PRD for each phase before execution. This captures testing philosophy, source files to modify, design decisions, and acceptance criteria. Claude reads this before starting work, which dramatically reduces wrong turns.

### 4. Execute — one deliverable per session

Each session declares one deliverable and does whatever that deliverable needs: planning, coding, testing, and reviewing can all happen in one sitting. Plan mode is optional — reach for it when the approach is genuinely uncertain, skip it when the diff could be described in one sentence. Current models plan well on their own; the artifacts (roadmap, PRD, CLAUDE.md) carry the context, and your role shifts from generating instructions to reviewing output at gates.

### 5. Verify before the gate

Before a gate, a fresh-context subagent reviews the work against the PRD/phase goal and reports gaps that affect correctness. Self-review by the agent that wrote the code is unreliable; a reviewer that sees only the diff and the spec is not. The runner does this automatically and surfaces the findings in the gate review.

> **Why the kit got thinner in v2 (Aug 2026).** Every component in a workflow encodes an assumption about what the model can't do on its own. The original kit split work into typed sessions (plan → implement → review) and ran one task per short invocation. Current models don't need that decomposition, and long always-loaded rulebooks make the rules that matter get lost. v2 keeps the durable artifacts — roadmap, gates, ADRs, work logs — and cuts the choreography. Revisit this whenever models step up again.

---

## How Roadmaps Work

A roadmap is a markdown file with embedded machine-readable metadata:

```markdown
<!-- ROADMAP-META
project: My Project
entity: burn-app
size: large
repo: ~/Code/my-project/
status: active
-->

<!-- SESSION-CONTEXT
last_session: 2026-02-15
last_task: 1.3
next_task: 1.4
blockers: none
notes: Completed auth system, next is the dashboard
-->

## Phase 1: Foundation

- [x] 1.1 Set up project structure
- [x] 1.2 Implement authentication
- [x] 1.3 Add user management
- [ ] >>> 1.4 Build dashboard layout
- [ ] 1.5 Add data visualization
- [ ] GATE: Review Phase 1 deliverables
```

Key mechanics:
- **`>>>`** — Marks the current in-progress task. Only one at a time. The autonomous runner looks for this.
- **`GATE:`** — Quality gate. The task runner stops here and sends a macOS notification for human review. Use `/project gate` to approve, request changes, or reject.
- **`SESSION-CONTEXT`** — Machine-readable state that carries between sessions. Updated at the end of each session.
- **Task IDs** — `[phase].[sequence]` format (e.g., 1.4, 2.1). Referenced in session context.

The autonomous runner (`run-project.py`):
1. Reads the roadmap, finds the `>>>` task and every task before the next `GATE:`
2. If `>>>` is already on a GATE, writes `_system/active-gate.md` (with the verifier's findings) and opens a gate-review session
3. Otherwise, builds a prompt with Session Context, the current phase, and the linked PRD — not the whole roadmap; Claude reads more if it needs to
4. Runs one long `claude -p --permission-mode auto` invocation (default 4-hour timeout) that works through the batch, updating `>>>` after each task, grounding progress claims in tool results, and running a fresh-context verifier at the gate
5. Re-invokes only if the run ended early; stops if `>>>` didn't move (stuck), on error, or on timeout

---

## How Work Logging Works

Work logging operates at two levels:

### Automatic (JSONL)

The `work-logger.py` hook captures every significant tool use:
```json
{"timestamp": "2026-02-16T10:30:00", "tool": "Edit", "action": "edit", "file": "/path/to/file.py", "entity": "Burn App", "session_id": "abc123"}
```

These accumulate in `[entity]/work-logs/YYYY-MM.jsonl`. No human action required.

### Manual (Markdown)

At the end of every substantive session, Claude writes a work log entry following the template. It asks 1-2 brief questions to capture strategic context ("What does this unlock for the business?"), then writes the entry automatically. The entry includes:

- What was accomplished (outcome-focused)
- Problems solved and decisions made
- Time saved with rate tiers ($35/hr research, $75/hr development)
- Strategic impact (for case studies)
- Carry-forward items (next steps, blockers, open questions)

### Rate Tiers

- **$35/hr** — Research, admin, documentation, planning, strategy
- **$75/hr** — Coding, development, technical implementation, debugging

These are used in time-saved calculations: if Claude saved 4 hours of coding work, that's $300 in value.

### Case Study Pipeline

When enough work logs accumulate for a project, run `/case-study` to:
1. Aggregate all JSONL data and manual logs
2. Calculate total ROI (time value + strategic value)
3. Generate a case study from the template
4. Create a one-page overview for quick sharing

---

## System Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    ~/CLAUDE.md                           │
│          Behavioral guardrails (Layer 1)                │
│  Push forward • When to pause • Safety rules            │
│  Credential gathering • Session handoffs                │
└──────────────────────┬──────────────────────────────────┘
                       │ Claude reads at session start
                       ▼
┌─────────────────────────────────────────────────────────┐
│                 Claude Code Session                      │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │ /project │  │/implement│  │ /log-work│  Commands    │
│  │ /case-   │  │          │  │ /work-   │  (Layer 3)   │
│  │  study   │  │          │  │  summary │              │
│  └──────────┘  └──────────┘  └──────────┘             │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Every Tool Use                      │   │
│  │  Edit, Write, Bash, Read, Grep, Glob, ...       │   │
│  └──────────────────┬──────────────────────────────┘   │
│                     │                                   │
└─────────────────────┼───────────────────────────────────┘
                      │ PostToolUse hook
                      ▼
┌─────────────────────────────────────────────────────────┐
│              Automated Tracking (Layer 2)                │
│                                                         │
│  work-logger.py ──→ [entity]/work-logs/YYYY-MM.jsonl   │
│  session-summary.py ──→ session summary on Stop          │
│  notify.sh ──→ macOS sounds (approval, complete)        │
│  statusline.sh ──→ model, context%, cost, branch        │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                Templates (Layer 3)                       │
│                                                         │
│  roadmap-template.md     → Multi-session tracking       │
│  project-brief.md        → Sizing assessment            │
│  work-log-entry.md       → Session deliverables + ROI   │
│  case-study-template.md  → Marketing case studies       │
│  roi-calculation.md      → Value quantification         │
│  one-page-overview.md    → Quick-share summaries        │
└─────────────────────────────────────────────────────────┘
```

---

## Why These Design Decisions?

**Why `CLAUDE.md` instead of just remembering?** — `CLAUDE.md` is loaded at the start of every session automatically. Memory is fragile; a file is permanent. It also lets team members share the same operating rules.

**Why JSONL for work logs?** — Append-only, no schema conflicts, easy to parse, easy to aggregate. Each line is independent, so a corrupt entry doesn't break the file.

**Why machine-readable HTML comments in roadmaps?** — The autonomous runner needs to parse project state programmatically. HTML comments are invisible when viewing the markdown in any renderer, so the roadmap stays clean for humans while being machine-readable.

**Why quality gates?** — Autonomous execution is powerful but needs checkpoints. Gates force a human review at phase boundaries, preventing Claude from building on top of a flawed foundation. Without gates, a wrong decision in Phase 1 could cascade through the entire project.

**Why separate rate tiers?** — Research and coding have very different market values. A flat rate would over-count research value and under-count development value. The two tiers make ROI calculations more defensible.

**Why push work logs to main?** — Work logs are append-only records. There's no merge conflict risk, no review needed, and no value in gating them. The friction of branches + PRs would discourage logging, which defeats the purpose.

**Why `Bash(*)` excluded from default settings?** — It allows Claude to run any shell command without permission prompts. This is powerful but aggressive as a team default. Individual users can add it if they want that level of autonomy.

---

## Getting the Most Out of This System

1. **Read CLAUDE.md yourself** — Understand what Claude is told to do. If something feels wrong, it's probably a CLAUDE.md issue.

2. **Use roadmaps for anything multi-session** — Even "quick" projects often span 2-3 sessions. A roadmap takes 2 minutes to create and saves 15 minutes of context re-establishment per session.

3. **Answer the work log questions** — The 30-second strategic context you provide makes the difference between a useful log and a generic one. These answers become case study content.

4. **Review the daily review** — The HTML reports surface patterns you won't notice in the moment. "You spent 60% of this week on V School" is information that helps you allocate time better.

5. **Trust the autonomous runner** — For roadmapped projects, let `run-project.py` handle the mundane phases. Save your attention for gate reviews where human judgment matters.

6. **Let Claude suggest improvements** — The CLAUDE.md tells Claude to watch for repeated instructions, workflow inefficiencies, and better approaches. Take those suggestions seriously — they come from pattern matching across all your sessions.
