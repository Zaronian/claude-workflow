#!/usr/bin/env python3
"""
Work Logger Hook for Claude Code
Captures tool usage and logs it to entity-specific work logs.

This hook is triggered after each tool use and logs relevant activity
to JSONL files organized by entity and month.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Single base path for all Knowledge Bases
KB_BASE = Path.home() / "Knowledge-Base"

# Entity detection patterns - maps path patterns to entity names
ENTITY_PATTERNS = {
    "Knowledge-Base/burn-app": "Burn App",
    "Knowledge-Base/snowline": "Snowline Consulting",
    "Knowledge-Base/v-school": "V School",
    "Knowledge-Base/smash-creative": "Smash Creative",
    "Knowledge-Base/volley": "Volley",
}

# Tools worth logging (significant work indicators)
SIGNIFICANT_TOOLS = {
    "Edit",
    "Write",
    "Bash",
    "Read",
    "Grep",
    "Glob",
    "Task",
    "WebFetch",
    "WebSearch",
}


def detect_entity(file_paths: list[str]) -> str | None:
    """Detect which entity the work belongs to based on file paths."""
    for path in file_paths:
        for pattern, entity in ENTITY_PATTERNS.items():
            if pattern in path:
                return entity
    return None


def get_work_log_path(entity: str) -> Path:
    """Get the path to the work log file for an entity."""
    entity_to_folder = {
        "Burn App": "burn-app",
        "Snowline Consulting": "snowline",
        "V School": "v-school",
        "Smash Creative": "smash-creative",
        "Volley": "volley",
    }

    folder = entity_to_folder.get(entity)
    if not folder:
        return None

    month = datetime.now().strftime("%Y-%m")
    log_dir = KB_BASE / folder / "work-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / f"{month}.jsonl"


def extract_file_paths(tool_input: dict) -> list[str]:
    """Extract file paths from tool input."""
    paths = []

    # Common parameter names for file paths
    path_keys = ["file_path", "path", "notebook_path", "command"]

    for key in path_keys:
        if key in tool_input:
            value = tool_input[key]
            if isinstance(value, str):
                # For commands, try to extract paths
                if key == "command":
                    # Simple heuristic: look for paths starting with /
                    words = value.split()
                    for word in words:
                        if word.startswith("/") and "Knowledge-Base" in word:
                            paths.append(word)
                else:
                    paths.append(value)

    return paths


def create_log_entry(hook_data: dict) -> dict:
    """Create a structured log entry from hook data."""
    tool_name = hook_data.get("tool_name", "unknown")
    tool_input = hook_data.get("tool_input", {})

    entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "session_id": hook_data.get("session_id", "unknown"),
    }

    # Add tool-specific details
    if tool_name == "Edit":
        entry["action"] = "edit"
        entry["file"] = tool_input.get("file_path", "")
        # Don't log actual content for privacy/size
        entry["has_changes"] = bool(tool_input.get("new_string"))

    elif tool_name == "Write":
        entry["action"] = "write"
        entry["file"] = tool_input.get("file_path", "")
        entry["content_length"] = len(tool_input.get("content", ""))

    elif tool_name == "Read":
        entry["action"] = "read"
        entry["file"] = tool_input.get("file_path", "")

    elif tool_name == "Bash":
        entry["action"] = "bash"
        command = tool_input.get("command", "")
        # Only log the first 100 chars of command
        entry["command_preview"] = command[:100] + ("..." if len(command) > 100 else "")

    elif tool_name == "Grep":
        entry["action"] = "search"
        entry["pattern"] = tool_input.get("pattern", "")
        entry["path"] = tool_input.get("path", "")

    elif tool_name == "Glob":
        entry["action"] = "glob"
        entry["pattern"] = tool_input.get("pattern", "")

    elif tool_name == "Task":
        entry["action"] = "task"
        entry["description"] = tool_input.get("description", "")
        entry["subagent_type"] = tool_input.get("subagent_type", "")

    elif tool_name in ("WebFetch", "WebSearch"):
        entry["action"] = "web"
        entry["url"] = tool_input.get("url", "")
        entry["query"] = tool_input.get("query", "")

    return entry


def main():
    """Main entry point for the hook."""
    try:
        # Read hook input from stdin
        input_data = sys.stdin.read()
        if not input_data:
            sys.exit(0)

        hook_data = json.loads(input_data)

        # Check if this is a significant tool
        tool_name = hook_data.get("tool_name", "")
        if tool_name not in SIGNIFICANT_TOOLS:
            sys.exit(0)

        # Extract file paths to detect entity
        tool_input = hook_data.get("tool_input", {})
        file_paths = extract_file_paths(tool_input)

        # Also check the working directory
        cwd = os.getcwd()
        if "Knowledge-Base" in cwd:
            file_paths.append(cwd)

        # Detect entity
        entity = detect_entity(file_paths)
        if not entity:
            # No entity detected, skip logging
            sys.exit(0)

        # Get log file path
        log_path = get_work_log_path(entity)
        if not log_path:
            sys.exit(0)

        # Create and append log entry
        entry = create_log_entry(hook_data)
        entry["entity"] = entity

        with open(log_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    except Exception as e:
        # Hooks should fail silently to not disrupt the user
        debug_log = KB_BASE / "_system" / "hooks" / "debug.log"
        try:
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now().isoformat()} - Error: {e}\n")
        except:
            pass
        sys.exit(0)


if __name__ == "__main__":
    main()
