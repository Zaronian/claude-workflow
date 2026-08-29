#!/usr/bin/env python3
"""
Session Summary Hook for Claude Code
Generates a summary of the session's work when Claude stops.

This hook is triggered on the Stop event and creates a summary entry
that consolidates the session's activities.
"""

from __future__ import annotations

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Single base path for all Knowledge Bases
KB_BASE = Path.home() / "Knowledge-Base"


def get_session_logs(session_id: str) -> dict[str, list]:
    """Get all log entries for a session, organized by entity."""
    entity_logs = defaultdict(list)

    # Search all entity work-logs directories
    for entity_dir in KB_BASE.iterdir():
        if not entity_dir.is_dir() or entity_dir.name.startswith((".", "_")):
            continue

        work_logs_dir = entity_dir / "work-logs"
        if not work_logs_dir.exists():
            continue

        # Check current month's log file
        month = datetime.now().strftime("%Y-%m")
        log_file = work_logs_dir / f"{month}.jsonl"

        if not log_file.exists():
            continue

        # Read and filter entries for this session
        try:
            with open(log_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    entry = json.loads(line)
                    if entry.get("session_id") == session_id:
                        entity = entry.get("entity", "Unknown")
                        entity_logs[entity].append(entry)
        except Exception:
            continue

    return dict(entity_logs)


def create_session_summary(session_id: str, entity_logs: dict) -> dict:
    """Create a summary of the session's work."""
    summary = {
        "type": "session_summary",
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "entities_touched": list(entity_logs.keys()),
        "entity_summaries": {},
    }

    for entity, logs in entity_logs.items():
        # Aggregate actions
        actions = defaultdict(int)
        files_modified = set()
        files_read = set()
        searches = []
        tasks = []

        for entry in logs:
            action = entry.get("action", "unknown")
            actions[action] += 1

            if action in ("edit", "write"):
                if entry.get("file"):
                    files_modified.add(entry["file"])
            elif action == "read":
                if entry.get("file"):
                    files_read.add(entry["file"])
            elif action == "search":
                if entry.get("pattern"):
                    searches.append(entry["pattern"])
            elif action == "task":
                if entry.get("description"):
                    tasks.append(entry["description"])

        summary["entity_summaries"][entity] = {
            "action_counts": dict(actions),
            "files_modified": list(files_modified),
            "files_read": list(files_read)[:10],  # Limit to first 10
            "search_patterns": searches[:5],  # Limit to first 5
            "tasks_launched": tasks[:5],  # Limit to first 5
            "total_actions": len(logs),
        }

    return summary


def save_summary(summary: dict) -> None:
    """Save the session summary to each relevant entity's work log."""
    for entity in summary.get("entities_touched", []):
        # Map entity name to folder
        entity_to_folder = {
            "Burn App": "burn-app",
            "Lightswitch Labs": "lightswitch",
            "V School": "v-school",
            "Smash Creative": "smash-creative",
            "Volley": "volley",
        }

        folder = entity_to_folder.get(entity)
        if not folder:
            continue

        # Get log file path
        month = datetime.now().strftime("%Y-%m")
        log_path = KB_BASE / folder / "work-logs" / f"{month}.jsonl"

        if log_path.exists():
            # Create entity-specific summary
            entity_summary = {
                "type": "session_summary",
                "session_id": summary["session_id"],
                "timestamp": summary["timestamp"],
                "entity": entity,
                "summary": summary["entity_summaries"].get(entity, {}),
            }

            with open(log_path, "a") as f:
                f.write(json.dumps(entity_summary) + "\n")


def main():
    """Main entry point for the hook."""
    try:
        # Read hook input from stdin
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)

        hook_data = json.loads(input_data)
        session_id = hook_data.get("session_id", "unknown")

        # Get logs for this session
        entity_logs = get_session_logs(session_id)

        if not entity_logs:
            # No work logged for this session
            sys.exit(0)

        # Create and save summary
        summary = create_session_summary(session_id, entity_logs)
        save_summary(summary)

    except Exception as e:
        # Hooks should fail silently
        debug_log = KB_BASE / "_system" / "hooks" / "debug.log"
        try:
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now().isoformat()} - Session Summary Error: {e}\n")
        except:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()
