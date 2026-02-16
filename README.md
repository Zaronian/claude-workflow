# Snowline Claude Workflow Kit

A complete Claude Code workflow system that transforms ephemeral AI sessions into a structured, trackable, autonomous development practice. Built over 2+ months of daily use at Snowline Consulting.

## What This Is

This repo installs a **methodology layer** on top of Claude Code — behavioral guardrails (`CLAUDE.md`), automated tracking (hooks & scripts), and structured workflows (templates & slash commands). It doesn't change how Claude works; it changes how you *work with* Claude.

## What Gets Installed

| Component | Destination | Purpose |
|-----------|-------------|---------|
| `CLAUDE.md` | `~/CLAUDE.md` | Behavioral guardrails — when to push forward, when to pause, safety rules |
| `settings.json` | `~/.claude/settings.json` | Permissions, hooks, statusline configuration |
| `/implement` | `~/.claude/commands/` | Full feature implementation workflow (plan → code → test → report) |
| `/project` | `~/Knowledge-Base/.claude/commands/` | Project lifecycle management (roadmaps, gates, autonomous runner) |
| `/log-work` | `~/Knowledge-Base/.claude/commands/` | Manual work log review/creation |
| `/case-study` | `~/Knowledge-Base/.claude/commands/` | Generate case studies from work logs |
| `/work-summary` | `~/Knowledge-Base/.claude/commands/` | Cross-entity work summary with ROI |
| `notify.sh` | `~/.claude/hooks/` | macOS notification sounds on permission prompts and task completion |
| `work-logger.py` | `~/Knowledge-Base/_system/hooks/` | Automatic JSONL activity logging per entity |
| `session-summary.py` | `~/Knowledge-Base/_system/hooks/` | Session summary generation on Claude stop |
| `statusline.sh` | `~/.claude/statusline.sh` | Model, context %, cost, and git branch in status bar |
| `daily-review.sh` | `~/.claude/scripts/` | Generate daily HTML work report |
| `run-project.py` | `~/Knowledge-Base/_system/scripts/` | Autonomous task runner for roadmapped projects |
| `open-roadmap.sh` | `~/Knowledge-Base/_system/scripts/` | Open roadmap in Marked 2 (or default viewer) |
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
- Python 3.10+
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

## Key Concepts

- **Push forward autonomously** — Claude works independently, only pausing for security-sensitive, ambiguous, or design decisions
- **Roadmapped projects** — Multi-session work uses machine-readable roadmaps with `>>>` task markers and `GATE:` quality checkpoints
- **Automatic work logging** — Every tool use is logged to JSONL; every session gets a summary; manual work logs capture ROI
- **Session handoffs** — Claude proactively suggests ending sessions at natural breakpoints, providing next-session prompts
- **Discovery-to-issue** — Bugs and concerns found during work become GitHub issues immediately, not buried in notes
