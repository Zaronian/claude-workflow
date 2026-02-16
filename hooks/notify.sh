#!/bin/bash
# Claude Code notification hook for macOS
# Rings terminal bell (for VS Code tab indicator) and plays a sound

TYPE="${1:-complete}"

# Ring the bell in the parent terminal (Claude Code's terminal)
# This triggers VS Code's yellow bell icon on the terminal tab
PARENT_TTY=$(ps -p $PPID -o tty= 2>/dev/null)
if [[ -n "$PARENT_TTY" && "$PARENT_TTY" != "??" ]]; then
    echo -ne "\a" > /dev/$PARENT_TTY 2>/dev/null
fi

# Play sound based on notification type
case "$TYPE" in
  approval)
    afplay /System/Library/Sounds/Ping.aiff
    ;;
  complete)
    afplay /System/Library/Sounds/Funk.aiff
    ;;
  *)
    afplay /System/Library/Sounds/Glass.aiff
    ;;
esac
