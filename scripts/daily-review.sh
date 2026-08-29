#!/bin/bash
# Daily Review Script
# Runs Claude to analyze the day's work and generate an HTML report

set -e

TODAY=$(date +%Y-%m-%d)
YEAR=$(date +%Y)
MONTH=$(date +%m)
REPORT_DIR="$HOME/Knowledge-Base/daily-reviews/${YEAR}/${MONTH}"
REPORT_FILE="${REPORT_DIR}/${TODAY}-review.html"
LOG_FILE="$HOME/.claude/scripts/daily-review.log"

# Ensure report directory exists
mkdir -p "${REPORT_DIR}"

echo "[$(date)] Starting daily review..." >> "${LOG_FILE}"

# Run Claude to generate the HTML report
claude -p --permission-mode acceptEdits "You are generating a daily review report. Do the following:

1. Read all work logs from today ($(date +%Y-%m-%d)) in ~/Knowledge-Base/lightswitch/work-logs/
2. Analyze the day's accomplishments across all businesses
3. Identify patterns - what went well, what could have been better
4. Suggest specific workflow improvements for tomorrow
5. Note any learnings about working with Claude effectively

Generate a beautiful, clean HTML report and write it to:
${REPORT_FILE}

The HTML should:
- Have a modern, clean design (dark background, light text, good typography)
- Include sections: Summary, Accomplishments, Analysis, Workflow Improvements, Claude Collaboration Tips
- Be self-contained (inline CSS, no external dependencies)
- Include the total time saved and dollar value across all sessions
- Be concise but insightful

Write the HTML file directly. Do not ask for confirmation." 2>> "${LOG_FILE}"

echo "[$(date)] Claude finished, opening report..." >> "${LOG_FILE}"

# Wait a moment for file to be written
sleep 2

# Open the report in the default browser
if [ -f "${REPORT_FILE}" ]; then
    open "${REPORT_FILE}"
    echo "[$(date)] Report opened: ${REPORT_FILE}" >> "${LOG_FILE}"
else
    echo "[$(date)] ERROR: Report file not found at ${REPORT_FILE}" >> "${LOG_FILE}"
fi
