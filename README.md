# Lightswitch Claude Workflow Kit

A complete Claude Code workflow system that transforms ephemeral AI sessions into a structured, trackable, autonomous development practice. Built over 2+ months of daily use at Lightswitch Labs.

## What This Is

This repo installs a **methodology layer** on top of Claude Code — behavioral guardrails (`CLAUDE.md`), automated tracking (hooks & scripts), and structured workflows (templates & slash commands). It doesn't change how Claude works; it changes how you *work with* Claude.

## What Gets Installed

| Component | Destination | Purpose |
|-----------|-------------|---------|
| `CLAUDE.md` | `~/CLAUDE.md` | Behavioral guardrails (~95 lines) — secrets, git, safeguards, continuous deliverable loop, orchestration cap, gates |
| `system-guide.md` | `~/Knowledge-Base/_system/reference/` | Detailed procedures the CLAUDE.md points to; loaded on demand, not every session |
| `settings.json` | `~/.claude/settings.json` | Permissions, hooks, statusline configuration |
| `/implement` | `~/.claude/commands/` | Feature implementation workflow (code → test → fresh-context review → report) |
| `/pr-review` | `~/.claude/commands/` | Fresh-context merge gate (correctness, authz, tests, ADR compliance, scope → PASS/CHANGES); required before any merge |
| `/handoff` | `~/.claude/commands/` | Re-surface the last thing a session copied for you (`~/.claude/handoffs/`) |
| `/loose-ends` | `~/.claude/commands/` | End-of-session sweep: finish what the rules allow, ask once, queue the rest in `<business>/queue.md` |
| `/project` | `~/Knowledge-Base/.claude/commands/` | Project lifecycle management (roadmaps, gates, autonomous runner) |
| `/log-work` | `~/Knowledge-Base/.claude/commands/` | Manual work log review/creation |
| `/case-study` | `~/Knowledge-Base/.claude/commands/` | Generate case studies from work logs |
| `/work-summary` | `~/Knowledge-Base/.claude/commands/` | Cross-entity work summary with ROI |
| `notify.sh` | `~/.claude/hooks/` | macOS notification sounds on permission prompts and task completion |
| `work-logger.py` | `~/Knowledge-Base/_system/hooks/` | Automatic JSONL activity logging per entity |
| `session-summary.py` | `~/Knowledge-Base/_system/hooks/` | Session summary generation on Claude stop |
| `statusline.sh` | `~/.claude/statusline.sh` | Model, context %, cost, and git branch in status bar; persists the status JSON per session for pacing checks |
| `daily-review.sh` | `~/.claude/scripts/` | Generate daily HTML work report |
| `run-project.py` | `~/Knowledge-Base/_system/scripts/` | Autonomous runner — one long run to the next gate, with a verifier subagent before the gate |
| `open-roadmap.sh` | `~/Knowledge-Base/_system/scripts/` | Open roadmap in Marked 2 (or default viewer) |
| `handoff.sh` | `~/Knowledge-Base/_system/scripts/` | Stores + pbcopys handoff prompts / "Need from you" blocks / commands under `~/.claude/handoffs/` |
| 6 templates | `~/Knowledge-Base/_system/Templates/` | Roadmap, brief, work log, case study, ROI, overview |
| `pre-commit-secrets` | `~/.scratch/hooks/` | Git hook to block accidental secret commits |

## Quickstart

```bash
# Clone this repo
git clone https://github.com/Zaronian/claude-workflow.git
cd claude-workflow

# Run the installer
bash setup.sh
```

The installer will:
1. Check prerequisites (macOS, Claude CLI, Python 3.10+, jq)
2. Detect existing configuration (fresh install vs. merge)
3. Install components — for merge installs, existing files are never overwritten
4. Print next steps

Use `--dry-run` to preview without writing files:
```bash
bash setup.sh --dry-run
```

## Prerequisites

- macOS
- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed
- Python 3.9+
- `jq` (installer will offer to install via Homebrew)
- `~/Knowledge-Base/` directory (set up via [kb-setup.sh](https://github.com/Zaronian/kb-setup) or manually)

## Understanding the System

Read **[PHILOSOPHY.md](PHILOSOPHY.md)** for a deep explanation of why each piece exists and how they work together. This is the most important file if you want to understand the system rather than just install it.

## For Existing Claude Users (Merge Install)

If you already have a `~/CLAUDE.md` or `~/.claude/settings.json`, the installer runs in merge mode:

- **CLAUDE.md**: Saved as `~/CLAUDE.team.md` — review and merge sections you want
- **settings.json**: Backed up, then merged — existing permissions/hooks preserved, new ones added
- **Commands/hooks/scripts**: Only installed if the file doesn't already exist
- **Templates**: Only installed if the file doesn't already exist

Your existing setup is never overwritten.

## What Changed in v2 (August 2026)

Re-tuned for current models (Claude Fable 5 / Opus 4.6+) following Anthropic's guidance that prior-model scaffolding degrades output:

- **CLAUDE.md cut from ~570 to ~80 lines.** Only rules the model can't infer stay always-loaded; procedures moved to `_system/reference/system-guide.md`.
- **Sessions declare a deliverable, not a type.** Plan, build, test, and review in one sitting when the approach is clear; plan mode is optional.
- **Runner runs to the gate in one invocation** (multi-hour timeout, `auto` permission mode, trimmed context) and has a fresh-context subagent verify the work before the human gate review.
- **`/implement` adds an adversarial review step** by a subagent that sees only the diff and the task.
- **Roadmap template** gains a Project Artifacts table, Session History, and `next_session_deliverable`; drops session-type fields.

Upgrading: rerun `bash setup.sh` (merge mode never overwrites existing files), then diff the new `~/CLAUDE.team.md` and `_system/reference/system-guide.md` against your copies. Existing roadmaps keep working; the runner tolerates the old format. **Pacing gauges need two extra steps on an existing install:** setup.sh replaces an old `~/.claude/statusline.sh` that does not yet persist the status JSON (a timestamped backup is kept) and creates `~/.claude/usage-data/statusline/` (persistence is opt-in by that directory existing) — check both happened, otherwise the pacing rule in CLAUDE.md fails silently.

## Key Concepts

- **Push forward autonomously** — Claude works independently, only pausing for security-sensitive, ambiguous, or design decisions
- **Roadmapped projects** — Multi-session work uses machine-readable roadmaps with `>>>` task markers and `GATE:` quality checkpoints
- **Automatic work logging** — Every tool use is logged to JSONL; every session gets a summary; manual work logs capture ROI
- **Continuous loop + handoffs** — Claude checkpoints after each deliverable and pulls the next one; it hands off (with a next-session prompt stored under `~/.claude/handoffs/`) at gates, budget thresholds, or a project switch
- **Discovery-to-issue** — Bugs and concerns found during work become GitHub issues immediately, not buried in notes
