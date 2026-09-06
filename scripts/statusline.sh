#!/bin/bash
input=$(cat)

# Persist the status JSON so agent sessions can read their own context fill
# and the account rate-limit meters at checkpoints.
# Atomic writes (a cancelled in-flight run never leaves a truncated file),
# session id sanitised (no path traversal), invalid/empty input skipped,
# files older than 7 days pruned.
D="$HOME/.claude/usage-data"
SID=$(echo "$input" | jq -r '.session_id // "unknown"' 2>/dev/null)
case "$SID" in *[!A-Za-z0-9._-]*|'') SID=unknown;; esac
if echo "$input" | jq -e . >/dev/null 2>&1 && mkdir -p "$D/sessions" 2>/dev/null; then
  printf '%s\n' "$input" > "$D/sessions/$SID.json.tmp.$$" && mv -f "$D/sessions/$SID.json.tmp.$$" "$D/sessions/$SID.json" \
    && cp "$D/sessions/$SID.json" "$D/latest.json.tmp.$$" && mv -f "$D/latest.json.tmp.$$" "$D/latest.json"
  find "$D/sessions" -name '*.json' -mtime +7 -delete 2>/dev/null
fi

MODEL=$(echo "$input" | jq -r '.model.display_name')
DIR=$(echo "$input" | jq -r '.workspace.current_dir')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
PCT=$(echo "$input" | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

CYAN='\033[36m'; GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'; RESET='\033[0m'

# Pick bar color based on context usage
if [ "$PCT" -ge 90 ]; then BAR_COLOR="$RED"
elif [ "$PCT" -ge 70 ]; then BAR_COLOR="$YELLOW"
else BAR_COLOR="$GREEN"; fi

FILLED=$((PCT / 10)); EMPTY=$((10 - FILLED))
BAR=$(printf "%${FILLED}s" | tr ' ' '█')$(printf "%${EMPTY}s" | tr ' ' '░')

MINS=$((DURATION_MS / 60000)); SECS=$(((DURATION_MS % 60000) / 1000))

BRANCH=""
git -C "$DIR" rev-parse --git-dir > /dev/null 2>&1 && BRANCH=" | 🌿 $(git -C "$DIR" branch --show-current 2>/dev/null)"

echo -e "${CYAN}[$MODEL]${RESET} 📁 ${DIR##*/}$BRANCH"
COST_FMT=$(printf '$%.2f' "$COST")
echo -e "${BAR_COLOR}${BAR}${RESET} ${PCT}% | ${YELLOW}${COST_FMT}${RESET} | ⏱️ ${MINS}m ${SECS}s"
