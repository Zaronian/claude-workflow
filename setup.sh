#!/bin/bash
# setup.sh — Lightswitch Claude Workflow Kit installer
#
# Installs the Claude Code workflow system: CLAUDE.md, hooks, scripts,
# templates, slash commands, and settings. Safe for both fresh installs
# and merging into existing setups.
#
# Usage:
#   bash setup.sh              # Interactive install
#   bash setup.sh --dry-run    # Show what would be installed without writing

set -euo pipefail

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOME_DIR="$HOME"
KB_DIR="$HOME_DIR/Knowledge-Base"
CLAUDE_DIR="$HOME_DIR/.claude"
SCRATCH_DIR="$HOME_DIR/.scratch"
DRY_RUN=false

# Colors
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
CYAN='\033[36m'
BOLD='\033[1m'
RESET='\033[0m'

# Tracking
INSTALLED=()
SKIPPED=()

# --- Argument parsing ---
for arg in "$@"; do
    case "$arg" in
        --dry-run) DRY_RUN=true ;;
        --help|-h)
            echo "Usage: bash setup.sh [--dry-run]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Show what would be installed without writing files"
            echo "  --help       Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown argument: $arg"
            echo "Usage: bash setup.sh [--dry-run]"
            exit 1
            ;;
    esac
done

# --- Helpers ---
info()  { echo -e "${CYAN}ℹ${RESET}  $1"; }
ok()    { echo -e "${GREEN}✓${RESET}  $1"; }
warn()  { echo -e "${YELLOW}⚠${RESET}  $1"; }
err()   { echo -e "${RED}✗${RESET}  $1"; }
header() { echo -e "\n${BOLD}═══ $1 ═══${RESET}\n"; }

# Copy a file with optional chmod
# Usage: install_file <source> <dest> [mode]
install_file() {
    local src="$1"
    local dest="$2"
    local mode="${3:-}"

    if $DRY_RUN; then
        info "[DRY RUN] Would copy: $src → $dest"
        INSTALLED+=("$dest (dry-run)")
        return
    fi

    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    if [[ -n "$mode" ]]; then
        chmod "$mode" "$dest"
    fi
    ok "Installed: $dest"
    INSTALLED+=("$dest")
}

# Copy only if destination doesn't exist
# Usage: install_if_new <source> <dest> [mode]
install_if_new() {
    local src="$1"
    local dest="$2"
    local mode="${3:-}"

    if [[ -f "$dest" ]]; then
        warn "Skipped (exists): $dest"
        SKIPPED+=("$dest (already exists)")
        return
    fi

    install_file "$src" "$dest" "$mode"
}

# --- Pre-flight checks ---
header "Pre-flight Checks"

# macOS check
if [[ "$(uname)" != "Darwin" ]]; then
    err "This installer is designed for macOS. Detected: $(uname)"
    exit 1
fi
ok "macOS detected"

# Claude CLI
if ! command -v claude &>/dev/null; then
    err "Claude CLI not found. Install it first: https://docs.anthropic.com/en/docs/claude-code"
    exit 1
fi
ok "Claude CLI found: $(which claude)"

# jq
if ! command -v jq &>/dev/null; then
    warn "jq not found (needed for statusline)"
    read -rp "Install jq via Homebrew? [Y/n] " JQ_ANSWER
    if [[ "${JQ_ANSWER:-Y}" =~ ^[Yy]$ ]]; then
        if $DRY_RUN; then
            info "[DRY RUN] Would run: brew install jq"
        else
            brew install jq
            ok "jq installed"
        fi
    else
        warn "Skipping jq install — statusline won't work without it"
    fi
else
    ok "jq found: $(which jq)"
fi

# Python 3.10+
if ! command -v python3 &>/dev/null; then
    err "Python 3 not found. Install Python 3.10+ first."
    exit 1
fi
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)
if [[ "$PY_MAJOR" -lt 3 ]] || [[ "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 9 ]]; then
    err "Python 3.9+ required, found $PY_VERSION"
    exit 1
fi
ok "Python $PY_VERSION found"

# Knowledge Base directory
if [[ ! -d "$KB_DIR" ]]; then
    err "~/Knowledge-Base/ not found."
    echo "   Run kb-setup.sh first to clone the Knowledge Base repos,"
    echo "   or create the directory manually: mkdir ~/Knowledge-Base"
    exit 1
fi
ok "Knowledge Base directory found"

# --- Detect existing setup ---
header "Detecting Existing Configuration"

INSTALL_MODE="fresh"

EXISTING_CLAUDE_MD=false
EXISTING_SETTINGS=false
EXISTING_COMMANDS=()
EXISTING_HOOKS=()

if [[ -f "$HOME_DIR/CLAUDE.md" ]]; then
    EXISTING_CLAUDE_MD=true
    info "Found existing ~/CLAUDE.md"
fi

if [[ -f "$CLAUDE_DIR/settings.json" ]]; then
    EXISTING_SETTINGS=true
    info "Found existing ~/.claude/settings.json"
fi

if [[ -d "$CLAUDE_DIR/commands" ]]; then
    while IFS= read -r f; do
        EXISTING_COMMANDS+=("$(basename "$f")")
    done < <(find "$CLAUDE_DIR/commands" -name "*.md" -type f 2>/dev/null)
    if [[ ${#EXISTING_COMMANDS[@]} -gt 0 ]]; then
        info "Found existing commands: ${EXISTING_COMMANDS[*]}"
    fi
fi

if [[ -d "$CLAUDE_DIR/hooks" ]]; then
    while IFS= read -r f; do
        EXISTING_HOOKS+=("$(basename "$f")")
    done < <(find "$CLAUDE_DIR/hooks" -type f 2>/dev/null)
    if [[ ${#EXISTING_HOOKS[@]} -gt 0 ]]; then
        info "Found existing hooks: ${EXISTING_HOOKS[*]}"
    fi
fi

# Determine install mode
if $EXISTING_CLAUDE_MD || $EXISTING_SETTINGS || [[ ${#EXISTING_COMMANDS[@]} -gt 0 ]] || [[ ${#EXISTING_HOOKS[@]} -gt 0 ]]; then
    INSTALL_MODE="merge"
    echo ""
    warn "Existing Claude configuration detected — using MERGE mode"
    info "Existing files will be preserved. New components will be added alongside them."
else
    echo ""
    ok "No existing configuration — using FRESH install mode"
fi

echo ""
if $DRY_RUN; then
    info "DRY RUN — no files will be written"
fi

read -rp "Proceed with ${INSTALL_MODE} install? [Y/n] " PROCEED
if [[ ! "${PROCEED:-Y}" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# --- Component 1: ~/CLAUDE.md ---
header "Component 1/6: CLAUDE.md"

if [[ "$INSTALL_MODE" == "fresh" ]]; then
    install_file "$SCRIPT_DIR/claude-md/CLAUDE.md" "$HOME_DIR/CLAUDE.md"
else
    if $EXISTING_CLAUDE_MD; then
        # Save team version alongside existing
        if $DRY_RUN; then
            info "[DRY RUN] Would save team CLAUDE.md as ~/CLAUDE.team.md"
            INSTALLED+=("~/CLAUDE.team.md (dry-run)")
        else
            cp "$SCRIPT_DIR/claude-md/CLAUDE.md" "$HOME_DIR/CLAUDE.team.md"
            ok "Saved team CLAUDE.md as ~/CLAUDE.team.md"
            INSTALLED+=("~/CLAUDE.team.md")
        fi
        echo ""
        info "Your existing ~/CLAUDE.md was preserved."
        info "Review ~/CLAUDE.team.md and merge relevant sections into ~/CLAUDE.md."
        info "Key sections to consider adding:"
        info "  - Secrets, Git, Safeguards"
        info "  - Working Style (push forward autonomously)"
        info "  - Projects & Sessions (continuous deliverable loop, gates)"
        info "  - Work Logs, Communication (evidence tiering)"
        info "The team CLAUDE.md is ~95 lines by design; detail lives in _system/reference/system-guide.md."
    else
        install_file "$SCRIPT_DIR/claude-md/CLAUDE.md" "$HOME_DIR/CLAUDE.md"
    fi
fi

# --- Component 2: settings.json ---
header "Component 2/6: Settings"

if [[ "$INSTALL_MODE" == "fresh" ]]; then
    mkdir -p "$CLAUDE_DIR"
    if $DRY_RUN; then
        info "[DRY RUN] Would create ~/.claude/settings.json with path substitution"
        INSTALLED+=("~/.claude/settings.json (dry-run)")
    else
        # Replace placeholder with actual home directory
        sed "s|\\\$HOME_PLACEHOLDER|$HOME_DIR|g" "$SCRIPT_DIR/settings/settings-base.json" > "$CLAUDE_DIR/settings.json"
        ok "Created ~/.claude/settings.json"
        INSTALLED+=("~/.claude/settings.json")
    fi
else
    if $EXISTING_SETTINGS; then
        if $DRY_RUN; then
            info "[DRY RUN] Would merge settings-base.json into existing settings.json"
            INSTALLED+=("~/.claude/settings.json (dry-run merge)")
        else
            # Create backup
            BACKUP="$CLAUDE_DIR/settings.json.backup-$(date +%Y%m%d-%H%M%S)"
            cp "$CLAUDE_DIR/settings.json" "$BACKUP"
            ok "Backed up settings to: $BACKUP"

            # Create a temp file with placeholders resolved for the base
            TEMP_BASE=$(mktemp)
            sed "s|\\\$HOME_PLACEHOLDER|$HOME_DIR|g" "$SCRIPT_DIR/settings/settings-base.json" > "$TEMP_BASE"

            # Run the merger
            MERGED=$(python3 "$SCRIPT_DIR/lib/merge-settings.py" "$CLAUDE_DIR/settings.json" "$TEMP_BASE" "$HOME_DIR")
            echo "$MERGED" > "$CLAUDE_DIR/settings.json"
            rm -f "$TEMP_BASE"
            ok "Merged workflow settings into ~/.claude/settings.json"
            INSTALLED+=("~/.claude/settings.json (merged)")
        fi
    else
        mkdir -p "$CLAUDE_DIR"
        if $DRY_RUN; then
            info "[DRY RUN] Would create ~/.claude/settings.json"
            INSTALLED+=("~/.claude/settings.json (dry-run)")
        else
            sed "s|\\\$HOME_PLACEHOLDER|$HOME_DIR|g" "$SCRIPT_DIR/settings/settings-base.json" > "$CLAUDE_DIR/settings.json"
            ok "Created ~/.claude/settings.json"
            INSTALLED+=("~/.claude/settings.json")
        fi
    fi
fi

# --- Component 3: Slash Commands ---
header "Component 3/6: Slash Commands"

# Global commands → ~/.claude/commands/
install_if_new "$SCRIPT_DIR/commands/global/implement.md" "$CLAUDE_DIR/commands/implement.md"
install_if_new "$SCRIPT_DIR/commands/global/pr-review.md" "$CLAUDE_DIR/commands/pr-review.md"
install_if_new "$SCRIPT_DIR/commands/global/handoff.md" "$CLAUDE_DIR/commands/handoff.md"
install_if_new "$SCRIPT_DIR/commands/global/loose-ends.md" "$CLAUDE_DIR/commands/loose-ends.md"

# Project commands → ~/Knowledge-Base/.claude/commands/
KB_CMD_DIR="$KB_DIR/.claude/commands"
install_if_new "$SCRIPT_DIR/commands/project/project.md" "$KB_CMD_DIR/project.md"
install_if_new "$SCRIPT_DIR/commands/project/log-work.md" "$KB_CMD_DIR/log-work.md"
install_if_new "$SCRIPT_DIR/commands/project/case-study.md" "$KB_CMD_DIR/case-study.md"
install_if_new "$SCRIPT_DIR/commands/project/work-summary.md" "$KB_CMD_DIR/work-summary.md"

# --- Component 4: Hooks & Scripts ---
header "Component 4/6: Hooks & Scripts"

# Hooks → ~/.claude/hooks/
install_if_new "$SCRIPT_DIR/hooks/notify.sh" "$CLAUDE_DIR/hooks/notify.sh" "+x"

# KB hooks → ~/Knowledge-Base/_system/hooks/
install_if_new "$SCRIPT_DIR/hooks/work-logger.py" "$KB_DIR/_system/hooks/work-logger.py" "+x"
install_if_new "$SCRIPT_DIR/hooks/session-summary.py" "$KB_DIR/_system/hooks/session-summary.py" "+x"

# Scripts → various locations
# statusline.sh is kit-owned: replace an older copy that does not persist the
# status JSON (pacing gauges depend on it); keep a timestamped backup.
if [[ -f "$CLAUDE_DIR/statusline.sh" ]] && ! grep -q "usage-data" "$CLAUDE_DIR/statusline.sh"; then
    if $DRY_RUN; then
        info "[dry-run] Would replace ~/.claude/statusline.sh with the gauge-persisting version (backup kept)"
    else
        cp "$CLAUDE_DIR/statusline.sh" "$CLAUDE_DIR/statusline.sh.backup-$(date +%Y%m%d-%H%M%S)"
        install_file "$SCRIPT_DIR/scripts/statusline.sh" "$CLAUDE_DIR/statusline.sh" "+x"
        info "Replaced ~/.claude/statusline.sh with the gauge-persisting version (backup kept)"
    fi
else
    install_if_new "$SCRIPT_DIR/scripts/statusline.sh" "$CLAUDE_DIR/statusline.sh" "+x"
fi
# Persistence of the status JSON is opt-in by this directory existing.
$DRY_RUN || mkdir -p "$HOME/.claude/usage-data/statusline"
install_if_new "$SCRIPT_DIR/scripts/daily-review.sh" "$CLAUDE_DIR/scripts/daily-review.sh" "+x"
install_if_new "$SCRIPT_DIR/scripts/run-project.py" "$KB_DIR/_system/scripts/run-project.py" "+x"
install_if_new "$SCRIPT_DIR/scripts/open-roadmap.sh" "$KB_DIR/_system/scripts/open-roadmap.sh" "+x"
install_if_new "$SCRIPT_DIR/scripts/handoff.sh" "$KB_DIR/_system/scripts/handoff.sh" "+x"

# Reference guide → ~/Knowledge-Base/_system/reference/ (CLAUDE.md points here for detail)
install_if_new "$SCRIPT_DIR/reference/system-guide.md" "$KB_DIR/_system/reference/system-guide.md"

# --- Component 5: Templates ---
header "Component 5/6: Templates"

TEMPLATE_DIR="$KB_DIR/_system/Templates"
install_if_new "$SCRIPT_DIR/templates/roadmap-template.md" "$TEMPLATE_DIR/roadmap-template.md"
install_if_new "$SCRIPT_DIR/templates/project-brief-template.md" "$TEMPLATE_DIR/project-brief-template.md"
install_if_new "$SCRIPT_DIR/templates/work-log-entry-template.md" "$TEMPLATE_DIR/work-log-entry-template.md"
install_if_new "$SCRIPT_DIR/templates/case-study-template.md" "$TEMPLATE_DIR/case-study-template.md"
install_if_new "$SCRIPT_DIR/templates/roi-calculation-template.md" "$TEMPLATE_DIR/roi-calculation-template.md"
install_if_new "$SCRIPT_DIR/templates/one-page-overview-template.md" "$TEMPLATE_DIR/one-page-overview-template.md"

# --- Component 6: Pre-commit Hook ---
header "Component 6/6: Pre-commit Secret Detection"

HOOK_DEST="$SCRATCH_DIR/hooks/pre-commit-secrets"
install_if_new "$SCRIPT_DIR/safety/pre-commit-secrets" "$HOOK_DEST" "+x"

# --- Summary ---
header "Setup Complete"

if [[ ${#INSTALLED[@]} -gt 0 ]]; then
    echo -e "${GREEN}${BOLD}Installed:${RESET}"
    for item in "${INSTALLED[@]}"; do
        echo "  ✓ $item"
    done
fi

if [[ ${#SKIPPED[@]} -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}${BOLD}Skipped:${RESET}"
    for item in "${SKIPPED[@]}"; do
        echo "  ⚠ $item"
    done
fi

echo ""
echo -e "${BOLD}Next steps:${RESET}"
if [[ "$INSTALL_MODE" == "merge" ]] && $EXISTING_CLAUDE_MD; then
    echo "  1. Review ~/CLAUDE.team.md and merge relevant sections into ~/CLAUDE.md"
    echo "  2. Run 'claude' to verify hooks are working (you should hear a sound when it stops)"
    echo "  3. Read PHILOSOPHY.md to understand the full system"
    echo "  4. Try '/project new' to create your first roadmapped project"
else
    echo "  1. Run 'claude' to verify hooks are working (you should hear a sound when it stops)"
    echo "  2. Read PHILOSOPHY.md to understand the full system"
    echo "  3. Try '/project new' to create your first roadmapped project"
fi
echo ""
