#!/usr/bin/env python3
"""
run-project.py — Autonomous task runner for project roadmaps.

Reads a project roadmap, finds the current task (marked with >>>),
generates a prompt, and executes it via Claude CLI. Loops until it
hits a quality gate, completes all tasks, or reaches the session limit.

Usage:
    python3 run-project.py <entity/project> [--max-sessions N] [--dry-run]

Examples:
    python3 run-project.py burn-app/engineering-excellence
    python3 run-project.py burn-app/engineering-excellence --max-sessions 3
    python3 run-project.py snowline/some-project --dry-run
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
import sys
import time

KB_DIR = os.path.expanduser("~/Knowledge-Base")
LOG_DIR = os.path.expanduser("~/.claude/scripts")
LOG_FILE = os.path.join(LOG_DIR, "project-runner.log")
GATE_FILE = os.path.join(KB_DIR, "_system/active-gate.md")
VIEWER_APP = os.environ.get("ROADMAP_VIEWER", "Marked 2")
DEFAULT_MAX_SESSIONS = 5


def log(message: str) -> None:
    """Log a message to both stdout and the log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def notify(title: str, message: str) -> None:
    """Send a macOS notification and terminal bell."""
    print(f"\a")  # Terminal bell
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'display notification "{message}" with title "{title}"',
            ],
            check=False,
            capture_output=True,
        )
    except FileNotFoundError:
        pass


def find_roadmap(project_path: str) -> str | None:
    """Locate the roadmap file for a project.

    Looks for [project-name]-roadmap.md in the project directory,
    checking both direct paths and under projects/ subdirectory.
    """
    project_name = project_path.split("/")[-1]
    roadmap_name = f"{project_name}-roadmap.md"
    candidates = [
        os.path.join(KB_DIR, project_path, roadmap_name),
        os.path.join(
            KB_DIR,
            project_path.split("/")[0],
            "projects",
            "/".join(project_path.split("/")[1:]),
            roadmap_name,
        ),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def parse_roadmap_meta(content: str) -> dict:
    """Extract ROADMAP-META fields from HTML comments."""
    meta = {}
    match = re.search(
        r"<!--\s*ROADMAP-META\s*\n(.*?)\n\s*-->", content, re.DOTALL
    )
    if match:
        for line in match.group(1).strip().splitlines():
            line = line.strip()
            if ":" in line:
                key, _, value = line.partition(":")
                meta[key.strip()] = value.strip()
    return meta


def parse_session_context(content: str) -> dict:
    """Extract SESSION-CONTEXT fields from HTML comments."""
    ctx = {}
    match = re.search(
        r"<!--\s*SESSION-CONTEXT\s*\n(.*?)\n\s*-->", content, re.DOTALL
    )
    if match:
        for line in match.group(1).strip().splitlines():
            line = line.strip()
            if ":" in line:
                key, _, value = line.partition(":")
                ctx[key.strip()] = value.strip()
    return ctx


def find_current_task(content: str) -> dict | None:
    """Find the line with >>> marker and parse the task."""
    for i, line in enumerate(content.splitlines()):
        if ">>>" in line and re.match(r"\s*-\s*\[\s*\]", line):
            # Extract task ID and description
            # Pattern: - [ ] >>> 1.2 Task description
            task_match = re.search(
                r"-\s*\[\s*\]\s*>>>\s*([\d.]+)\s+(.*)", line
            )
            if task_match:
                task_id = task_match.group(1)
                description = task_match.group(2).strip()
                is_gate = description.upper().startswith("GATE:")
                # Check for per-task repo override
                repo_override = None
                # Look at next lines for metadata
                lines = content.splitlines()
                for j in range(i + 1, min(i + 5, len(lines))):
                    repo_match = re.match(
                        r"\s*-\s*repo:\s*(.+)", lines[j]
                    )
                    if repo_match:
                        repo_override = os.path.expanduser(
                            repo_match.group(1).strip()
                        )
                        break
                    # Stop if we hit another task line
                    if re.match(r"\s*-\s*\[", lines[j]):
                        break
                return {
                    "id": task_id,
                    "description": description,
                    "is_gate": is_gate,
                    "line_number": i,
                    "repo_override": repo_override,
                }
    return None


def find_current_phase(content: str, task_id: str) -> str | None:
    """Find the phase section containing the current task."""
    phase_num = task_id.split(".")[0]
    # Look for Phase N heading
    match = re.search(
        rf"##\s*Phase\s*{phase_num}[:\s]+(.*?)(?=\n##\s|$)",
        content,
        re.DOTALL,
    )
    if match:
        return match.group(0)
    return None


def read_linked_prd(content: str, task_id: str) -> str | None:
    """Read the PRD linked to the current phase, if any."""
    phase_num = task_id.split(".")[0]
    # Find the phase section and look for PRD link
    phase = find_current_phase(content, task_id)
    if not phase:
        return None
    prd_match = re.search(r"\*\*PRD:\*\*\s*(?:`([^`]+)`|(\S+))", phase)
    if not prd_match:
        return None
    prd_path = prd_match.group(1) or prd_match.group(2)
    if not prd_path or prd_path.startswith("["):
        return None
    prd_path = os.path.expanduser(prd_path)
    # Resolve relative paths from the roadmap directory
    if not os.path.isabs(prd_path):
        roadmap_dir = os.path.dirname(
            find_roadmap(sys.argv[1]) or ""
        )
        prd_path = os.path.join(roadmap_dir, prd_path)
    if os.path.isfile(prd_path):
        with open(prd_path) as f:
            return f.read()
    return None


def generate_prompt(
    roadmap_content: str,
    roadmap_path: str,
    task: dict,
    meta: dict,
    session_ctx: dict,
) -> str:
    """Generate the full prompt for Claude CLI."""
    phase_context = find_current_phase(roadmap_content, task["id"]) or ""
    prd_content = read_linked_prd(roadmap_content, task["id"])

    prd_section = ""
    if prd_content:
        prd_section = f"""

## PRD for Current Phase

{prd_content}
"""

    return f"""You are executing a task from a project roadmap as part of an autonomous task runner.

## Your Task

**Task {task['id']}:** {task['description']}

## Instructions

1. Execute the task described above thoroughly and completely.
2. After completing the work, update the roadmap file at `{roadmap_path}`:
   a. Mark the current task as done: change `- [ ] >>> {task['id']}` to `- [x] {task['id']}`
   b. Move the `>>>` marker to the next uncompleted task (the next `- [ ]` item that is NOT a GATE)
   c. If the next item is a `GATE:` item, place `>>>` on the GATE item so the runner knows to stop
   d. Update the `SESSION-CONTEXT` HTML comment block with:
      - `last_session:` today's date
      - `last_task:` {task['id']}
      - `next_task:` the ID of the next task
      - `notes:` brief summary of what you did and what's next
   e. Update the human-readable Session Context section similarly
   f. Update the Progress table counts
3. Commit all changes (code + roadmap update) with a clear commit message.
4. Write a work log entry to `~/Knowledge-Base/snowline/work-logs/` following the standard template.

## Project Context

**Entity:** {meta.get('entity', 'unknown')}
**Project:** {meta.get('project', 'unknown')}

### Session Context
- Last session: {session_ctx.get('last_session', 'N/A')}
- Last task: {session_ctx.get('last_task', 'N/A')}
- Blockers: {session_ctx.get('blockers', 'none')}
- Notes: {session_ctx.get('notes', 'N/A')}

### Current Phase

{phase_context}
{prd_section}

## Full Roadmap

{roadmap_content}
"""


def write_gate_file(
    roadmap_path: str, task: dict, meta: dict, roadmap_content: str
) -> None:
    """Write the active-gate.md file for human review."""
    # Gather completed tasks from the roadmap
    completed = []
    for line in roadmap_content.splitlines():
        match = re.match(r"\s*-\s*\[x\]\s*([\d.]+)\s+(.*)", line)
        if match:
            completed.append(f"- {match.group(1)} {match.group(2)}")
    completed_list = "\n".join(completed) if completed else "- (none yet)"

    gate_content = f"""# Quality Gate Review

**Project:** {meta.get('project', 'Unknown')}
**Entity:** {meta.get('entity', 'Unknown')}
**Roadmap:** `{roadmap_path}`
**Gate:** {task['id']} — {task['description']}
**Reached:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

## What This Gate Asks You to Review

{task['description'].replace('GATE:', '').strip()}

## Completed Tasks Leading Up to This Gate

{completed_list}

## What Happens After Approval

Mark this gate as complete in the roadmap and the task runner will continue
with the next task. You can:

1. **Approve** — tell Claude "approved, continue" and it will update the roadmap
2. **Request changes** — describe what needs to change before proceeding
3. **Reject** — stop the project and explain why

## Roadmap File

Open the roadmap for full context: `{roadmap_path}`

## To Resume the Task Runner After Approval

```bash
python3 ~/Knowledge-Base/_system/scripts/run-project.py {meta.get('entity', 'entity')}/{meta.get('project', 'project')}
```
"""
    with open(GATE_FILE, "w") as f:
        f.write(gate_content)
    log(f"Gate file written to {GATE_FILE}")


def open_gate_session(roadmap_path: str) -> None:
    """Open the roadmap in viewer and a new Terminal with Claude for gate review."""
    # Open roadmap in viewer
    try:
        subprocess.run(
            ["open", "-a", VIEWER_APP, roadmap_path],
            check=False,
            capture_output=True,
        )
    except FileNotFoundError:
        subprocess.run(
            ["open", roadmap_path], check=False, capture_output=True
        )

    # Open a new Terminal window with an interactive Claude session
    gate_prompt = (
        f"Read {GATE_FILE} and present the gate review for my approval."
    )
    apple_script = f'''
    tell application "Terminal"
        activate
        do script "cd ~/Knowledge-Base && claude \\"{gate_prompt}\\""
    end tell
    '''
    try:
        subprocess.run(
            ["osascript", "-e", apple_script],
            check=False,
            capture_output=True,
        )
    except FileNotFoundError:
        log("Warning: Could not open Terminal via osascript")


def run_claude_session(prompt: str, working_dir: str) -> bool:
    """Run a Claude CLI session with the given prompt. Returns True on success."""
    log(f"Running Claude session in {working_dir}")
    log(f"Prompt length: {len(prompt)} chars")

    try:
        result = subprocess.run(
            [
                "claude",
                "-p",
                "--permission-mode",
                "acceptEdits",
                prompt,
            ],
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout per session
        )
        if result.returncode == 0:
            log("Claude session completed successfully")
            if result.stdout:
                # Log last few lines of output
                output_lines = result.stdout.strip().splitlines()
                for line in output_lines[-10:]:
                    log(f"  > {line}")
            return True
        else:
            log(f"Claude session failed with exit code {result.returncode}")
            if result.stderr:
                log(f"  stderr: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        log("Claude session timed out (10 min limit)")
        return False
    except FileNotFoundError:
        log("Error: 'claude' CLI not found in PATH")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous task runner for project roadmaps"
    )
    parser.add_argument(
        "project",
        help="Project path as entity/project (e.g., burn-app/engineering-excellence)",
    )
    parser.add_argument(
        "--max-sessions",
        type=int,
        default=DEFAULT_MAX_SESSIONS,
        help=f"Maximum sessions to run (default: {DEFAULT_MAX_SESSIONS})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without running",
    )
    args = parser.parse_args()

    log(f"=== Task Runner Start: {args.project} (max {args.max_sessions} sessions) ===")

    # Find roadmap
    roadmap_path = find_roadmap(args.project)
    if not roadmap_path:
        log(f"Error: No roadmap found for '{args.project}'")
        notify("Task Runner Error", f"No roadmap found for {args.project}")
        sys.exit(1)

    log(f"Roadmap: {roadmap_path}")

    sessions_run = 0
    previous_task_id = None

    while sessions_run < args.max_sessions:
        # Read roadmap fresh each iteration
        with open(roadmap_path) as f:
            content = f.read()

        meta = parse_roadmap_meta(content)
        session_ctx = parse_session_context(content)

        # Find current task
        task = find_current_task(content)
        if not task:
            log("No current task found (no >>> marker with unchecked item). Project may be complete.")
            notify("Task Runner", f"Project {args.project} — no more tasks found")
            break

        # Safety: prevent infinite loop on same task
        if task["id"] == previous_task_id:
            log(
                f"Error: Task {task['id']} was not updated after last session. "
                "Stopping to prevent infinite loop."
            )
            notify(
                "Task Runner Error",
                f"Task {task['id']} stuck — roadmap not updated",
            )
            break

        log(f"Current task: {task['id']} — {task['description']}")

        # Check for gate
        if task["is_gate"]:
            log(f"Gate reached: {task['description']}")
            write_gate_file(roadmap_path, task, meta, content)
            notify(
                "Quality Gate",
                f"{meta.get('project', args.project)}: {task['description']}",
            )
            open_gate_session(roadmap_path)
            log("Stopping at gate. Resume after approval.")
            break

        # Determine working directory
        working_dir = task.get("repo_override") or meta.get("repo")
        if working_dir:
            working_dir = os.path.expanduser(working_dir)
        else:
            working_dir = os.path.dirname(roadmap_path)

        if not os.path.isdir(working_dir):
            log(f"Warning: Working directory '{working_dir}' not found, using roadmap directory")
            working_dir = os.path.dirname(roadmap_path)

        # Generate prompt
        prompt = generate_prompt(content, roadmap_path, task, meta, session_ctx)

        if args.dry_run:
            log(f"[DRY RUN] Would execute task {task['id']} in {working_dir}")
            log(f"[DRY RUN] Prompt preview (first 200 chars): {prompt[:200]}...")
            previous_task_id = task["id"]
            sessions_run += 1
            continue

        # Execute
        success = run_claude_session(prompt, working_dir)
        sessions_run += 1
        previous_task_id = task["id"]

        if not success:
            log(f"Session failed for task {task['id']}. Stopping.")
            notify(
                "Task Runner Error",
                f"Session failed on task {task['id']}",
            )
            break

        # Brief pause between sessions
        if sessions_run < args.max_sessions:
            time.sleep(2)

    log(
        f"=== Task Runner End: {sessions_run} session(s) run for {args.project} ==="
    )

    if sessions_run >= args.max_sessions:
        log(f"Reached max sessions limit ({args.max_sessions})")
        notify(
            "Task Runner",
            f"Reached {args.max_sessions} session limit for {args.project}",
        )


if __name__ == "__main__":
    main()
