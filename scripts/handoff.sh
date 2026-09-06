#!/bin/bash
# handoff.sh — store + copy anything a Claude session hands to the user.
#
# Usage:  <body on stdin> | handoff.sh <kind> <business/project> [--session ID] [--no-copy]
#   kind: handoff | need-from-you | command | note
#
# Writes ~/.claude/handoffs/sessions/<session_id>.md (latest item: header +
# body), appends the same item to sessions/<session_id>.history.md (nothing
# is lost when a session copies again), refreshes latest.md and index.md,
# and pbcopys the body. Sessions identify themselves via
# $CLAUDE_CODE_SESSION_ID (set in Claude Code's Bash tool); --session
# overrides. Retrieval: /handoff, or
#   alias hand='tail -n +7 ~/.claude/handoffs/latest.md | pbcopy'
set -uo pipefail

usage() { echo "usage: <body> | handoff.sh <kind> <business/project> [--session ID] [--no-copy]" >&2; exit 2; }

KIND="${1:-}"; PROJECT="${2:-}"
[ -z "$KIND" ] || [ -z "$PROJECT" ] && usage
shift 2
SESSION="${CLAUDE_CODE_SESSION_ID:-}"; COPY=1
while [ $# -gt 0 ]; do
  case "$1" in
    --session) SESSION="${2:?--session needs a value}"; shift 2 ;;
    --no-copy) COPY=0; shift ;;
    *) echo "unknown option: $1" >&2; usage ;;
  esac
done
[ -z "$SESSION" ] && SESSION="unknown-$(date +%Y%m%d-%H%M%S)"
case "$SESSION" in *[!A-Za-z0-9._-]*) echo "invalid session id (allowed: A-Z a-z 0-9 . _ -): $SESSION" >&2; exit 2 ;; esac
case "$KIND" in handoff|need-from-you|command|note) ;; *) echo "kind must be handoff|need-from-you|command|note" >&2; exit 2 ;; esac

ROOT="$HOME/.claude/handoffs"
mkdir -p "$ROOT/sessions" || { echo "cannot create $ROOT/sessions" >&2; exit 1; }
BODY="$(cat)"
[ -z "$BODY" ] && { echo "empty body on stdin" >&2; exit 2; }
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
FILE="$ROOT/sessions/$SESSION.md"
HIST="$ROOT/sessions/$SESSION.history.md"

# Latest item for this session — written atomically.
TMP="$FILE.tmp.$$"
{
  printf 'session: %s\nproject: %s\ncwd: %s\nwritten: %s\nkind: %s\n\n' "$SESSION" "$PROJECT" "$PWD" "$NOW" "$KIND"
  printf '%s\n' "$BODY"
} > "$TMP" && mv -f "$TMP" "$FILE" || { echo "write failed: $FILE" >&2; rm -f "$TMP"; exit 1; }

# Full history for this session — append-only, so an earlier "Need from you"
# survives a later copied command.
{ printf '\n---\n'; cat "$FILE"; } >> "$HIST"

# latest.md across all sessions.
cp "$FILE" "$ROOT/latest.md.tmp.$$" && mv -f "$ROOT/latest.md.tmp.$$" "$ROOT/latest.md"

# index.md — one line per session, newest first. Tolerates unreadable files.
ITMP="$ROOT/index.md.tmp.$$"
{
  echo "# Handoff registry — newest first (written by _system/scripts/handoff.sh)"
  echo
  ls -t "$ROOT"/sessions/*.md 2>/dev/null | grep -v '\.history\.md$' | while IFS= read -r f; do
    s=$(sed -n 's/^session: //p' "$f" 2>/dev/null | head -1)
    p=$(sed -n 's/^project: //p' "$f" 2>/dev/null | head -1)
    k=$(sed -n 's/^kind: //p' "$f" 2>/dev/null | head -1)
    w=$(sed -n 's/^written: //p' "$f" 2>/dev/null | head -1)
    echo "- ${w:-?} · ${p:-?} · ${k:-?} · ${s:-?}"
  done
} > "$ITMP" && mv -f "$ITMP" "$ROOT/index.md"

if [ "$COPY" -eq 1 ] && command -v pbcopy >/dev/null 2>&1; then
  printf '%s' "$BODY" | pbcopy
fi
echo "stored: $FILE ($KIND, $PROJECT); history: $HIST"
