#!/bin/bash
# open-roadmap.sh — Opens a project roadmap in the configured viewer
#
# Usage: open-roadmap.sh <entity/project>
# Example: open-roadmap.sh burn-app/engineering-excellence
#
# Configuration:
#   ROADMAP_VIEWER — app name (default: "Marked 2")
#   KB_DIR — Knowledge Base root (default: ~/Knowledge-Base)

set -euo pipefail

VIEWER_APP="${ROADMAP_VIEWER:-Marked 2}"
KB_DIR="${KB_DIR:-$HOME/Knowledge-Base}"

if [ $# -lt 1 ]; then
    echo "Usage: open-roadmap.sh <entity/project>"
    echo "Example: open-roadmap.sh burn-app/engineering-excellence"
    exit 1
fi

PROJECT_PATH="$1"
PROJECT_NAME="$(basename "$PROJECT_PATH")"
ROADMAP_NAME="${PROJECT_NAME}-roadmap.md"

ROADMAP="$KB_DIR/$PROJECT_PATH/$ROADMAP_NAME"

if [ ! -f "$ROADMAP" ]; then
    # Try under projects/ subdirectory
    ENTITY="$(echo "$PROJECT_PATH" | cut -d/ -f1)"
    REST="$(echo "$PROJECT_PATH" | cut -d/ -f2-)"
    ROADMAP="$KB_DIR/$ENTITY/projects/$REST/$ROADMAP_NAME"
fi

if [ ! -f "$ROADMAP" ]; then
    echo "Error: Roadmap not found. Looked for '$ROADMAP_NAME' at:"
    echo "  $KB_DIR/$PROJECT_PATH/$ROADMAP_NAME"
    echo "  $KB_DIR/$ENTITY/projects/$REST/$ROADMAP_NAME"
    exit 1
fi

echo "Opening: $ROADMAP"
echo "Viewer: $VIEWER_APP"

open -a "$VIEWER_APP" "$ROADMAP" 2>/dev/null || {
    echo "Warning: Could not open with '$VIEWER_APP', falling back to default app"
    open "$ROADMAP"
}
