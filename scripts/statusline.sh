#!/bin/bash
input=$(cat)

# Persist the status JSON — OPT-IN: create ~/.claude/usage-data/statusline to
# enable. Lets the MAIN session read its own context fill and the account
# rate-limit meters. Subagents share the parent's session id
# (CLAUDE_CODE_CHILD_SESSION=1) and must not pace on this file. Values are as
# of the session's most recent API response; `written_at` is the write time.
# Private files (umask 077), atomic writes, sanitised id, non-object input
# skipped, prune once per session (>30 days), all errors silent.
(
  D="$HOME/.claude/usage-data/statusline"
  if [ -d "$D" ] && SID=$(printf '%s' "$input" | jq -er 'objects | .session_id // "unknown"'); then
    case "$SID" in *[!A-Za-z0-9._-]*|'') SID=unknown;; esac
    umask 077
    mkdir -p "$D/sessions"
    [ -f "$D/sessions/$SID.json" ] || find "$D" \( -name '*.json' -mtime +30 -o -name '*.tmp.*' -mtime +1 \) -delete
    printf '%s' "$input" | jq --arg t "$(date +%s)" '. + {written_at: ($t|tonumber)}' > "$D/sessions/$SID.json.tmp.$$" \
      && mv -f "$D/sessions/$SID.json.tmp.$$" "$D/sessions/$SID.json" \
      && cp "$D/sessions/$SID.json" "$D/latest.json.tmp.$$" && mv -f "$D/latest.json.tmp.$$" "$D/latest.json"
  fi
) 2>/dev/null

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
