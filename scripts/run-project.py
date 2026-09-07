#!/usr/bin/env python3
"""
run-project.py — Autonomous task runner for project roadmaps.

Rebuilt 2026-08-29 for long-turn models. One invocation runs Claude to the
next quality gate: it hands Claude the current task and every remaining task
before the gate, lets Claude work through them (updating the roadmap's >>>
marker after each), and on reaching the gate has Claude run a fresh-context
verifier subagent before the human review.

Usage:
    python3 run-project.py <entity/project> [--timeout-hours N] [--max-runs N]
                           [--permission-mode MODE] [--dry-run]

Examples:
    python3 run-project.py burn-app/engineering-excellence
    python3 run-project.py lightswitch/some-project --timeout-hours 8
    python3 run-project.py lightswitch/some-project --dry-run

Log: ~/.claude/scripts/project-runner.log
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import subprocess
import sys
import time

KB_DIR = os.path.expanduser(os.environ.get("KB_DIR", "~/Knowledge-Base"))
WORKLOG_DIR = os.environ.get("KB_WORKLOG_DIR", os.path.join(KB_DIR, "lightswitch/work-logs"))
LOG_DIR = os.path.expanduser("~/.claude/scripts")
LOG_FILE = os.path.join(LOG_DIR, "project-runner.log")
GATE_FILE = os.path.join(KB_DIR, "_system/active-gate.md")
VIEWER_APP = os.environ.get("ROADMAP_VIEWER", "Marked 2")
DEFAULT_TIMEOUT_HOURS = 4.0
DEFAULT_MAX_RUNS = 3
DEFAULT_PERMISSION_MODE = "auto"
VERIFICATION_FILENAME = "gate-verification.md"


def log(message: str) -> None:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def notify(title: str, message: str) -> None:
    print("\a", end="", flush=True)
    try:
        subprocess.run(
            ["osascript", "-e", f'display notification "{message}" with title "{title}"'],
            check=False,
            capture_output=True,
        )
    except FileNotFoundError:
        pass


# ---------------------------------------------------------------------------
# Roadmap parsing
# ---------------------------------------------------------------------------


def find_roadmap(project_path: str) -> str | None:
    project_name = project_path.split("/")[-1]
    roadmap_name = f"{project_name}-roadmap.md"
    parts = project_path.split("/")
    candidates = [
        os.path.join(KB_DIR, project_path, roadmap_name),
        os.path.join(KB_DIR, parts[0], "kb", "projects", "/".join(parts[1:]), roadmap_name),
        os.path.join(KB_DIR, parts[0], "projects", "/".join(parts[1:]), roadmap_name),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


def _parse_comment_block(content: str, name: str) -> dict:
    out = {}
    match = re.search(rf"<!--\s*{name}\s*\n(.*?)\n\s*-->", content, re.DOTALL)
    if match:
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                key, _, value = line.strip().partition(":")
                out[key.strip()] = value.strip()
    return out


def parse_roadmap_meta(content: str) -> dict:
    return _parse_comment_block(content, "ROADMAP-META")


def parse_session_context(content: str) -> dict:
    return _parse_comment_block(content, "SESSION-CONTEXT")


TASK_RE = re.compile(r"^\s*-\s*\[\s*\]\s*(>>>\s*)?(?:([\d.]+)\s+)?(.*)$")


def parse_tasks(content: str) -> list[dict]:
    """All unchecked tasks in roadmap order.

    A task line is `- [ ] [>>>] ID description`. `GATE:` lines are accepted
    without an ID (the template writes them that way) and get a synthetic id.
    Other ID-less checkboxes (deliverable checklists, open questions) are skipped.
    """
    lines = content.splitlines()
    tasks = []
    for i, line in enumerate(lines):
        m = TASK_RE.match(line)
        if not m:
            continue
        description = m.group(3).strip()
        task_id = m.group(2)
        is_gate = description.upper().startswith("GATE:")
        if task_id is None:
            if not is_gate:
                continue
            task_id = f"GATE@L{i + 1}"
        repo_override = None
        for j in range(i + 1, min(i + 5, len(lines))):
            rm = re.match(r"\s*-\s*repo:\s*(.+)", lines[j])
            if rm:
                repo_override = os.path.expanduser(rm.group(1).strip())
                break
            if re.match(r"\s*-\s*\[", lines[j]):
                break
        tasks.append(
            {
                "id": task_id,
                "description": description,
                "is_current": bool(m.group(1)),
                "is_gate": is_gate,
                "line_number": i,
                "repo_override": repo_override,
            }
        )
    return tasks


def find_current_task(content: str) -> dict | None:
    for t in parse_tasks(content):
        if t["is_current"]:
            return t
    return None


def tasks_until_gate(content: str) -> tuple[list[dict], dict | None]:
    """Tasks from >>> up to (not including) the next GATE, plus that gate."""
    tasks = parse_tasks(content)
    started = False
    batch: list[dict] = []
    for t in tasks:
        if t["is_current"]:
            started = True
        if not started:
            continue
        if t["is_gate"]:
            return batch, t
        batch.append(t)
    return batch, None


def find_phase_section(content: str, task_id: str) -> str | None:
    phase_num = task_id.split(".")[0]
    match = re.search(rf"##\s*Phase\s*{phase_num}[:\s]+(.*?)(?=\n##\s|$)", content, re.DOTALL)
    return match.group(0) if match else None


def read_linked_prd(content: str, task_id: str, roadmap_path: str) -> tuple[str | None, str | None]:
    phase = find_phase_section(content, task_id)
    if not phase:
        return None, None
    prd_match = re.search(r"\*\*PRD:\*\*\s*(?:`([^`]+)`|(\S+))", phase)
    if not prd_match:
        return None, None
    prd_path = prd_match.group(1) or prd_match.group(2)
    if not prd_path or prd_path.startswith("["):
        return None, None
    prd_path = os.path.expanduser(prd_path)
    if not os.path.isabs(prd_path):
        prd_path = os.path.join(os.path.dirname(roadmap_path), prd_path)
    if os.path.isfile(prd_path):
        with open(prd_path) as f:
            return f.read(), prd_path
    return None, prd_path


# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------


def generate_prompt(
    content: str,
    roadmap_path: str,
    batch: list[dict],
    gate: dict | None,
    meta: dict,
    session_ctx: dict,
) -> str:
    first = batch[0]
    phase_context = find_phase_section(content, first["id"]) or ""
    prd_content, prd_path = read_linked_prd(content, first["id"], roadmap_path)
    verification_path = os.path.join(os.path.dirname(roadmap_path), VERIFICATION_FILENAME)

    task_list = "\n".join(f"- **{t['id']}** {t['description']}" for t in batch)
    gate_line = (
        f"**Gate after this batch:** {gate['id']} — {gate['description']}"
        if gate
        else "**No gate follows this batch** — it ends the roadmap's open tasks."
    )

    prd_section = f"\n\n## PRD for Current Phase (`{prd_path}`)\n\n{prd_content}\n" if prd_content else ""

    gate_instructions = ""
    if gate:
        gate_ref = gate["id"] if not gate["id"].startswith("GATE@") else f"the `GATE:` line (roadmap line {gate['line_number'] + 1})"
        gate_instructions = f"""
## When you reach the gate

Before stopping, run a verification pass with a **fresh-context subagent** (Agent tool). Give it only: the phase goal, the PRD (if any), the list of tasks you completed, and the diff / files changed. Ask it to check that every requirement is implemented and tested and that nothing outside scope changed — gaps that affect correctness, not style. Write its findings to `{verification_path}` (overwrite), fix anything real, and re-run if you fixed something.

Then leave `>>>` on {gate_ref} and end your turn.
"""

    return f"""I'm running the roadmap for **{meta.get('project', 'unknown')}** ({meta.get('entity', 'unknown')}) autonomously. Nobody is watching; work end to end and stop only at the gate or when you are blocked on input only the user can provide.

## Tasks to complete, in order

{task_list}

{gate_line}

## Working rules

- Roadmap: `{roadmap_path}`. Read more of it if you need context beyond what is below.
- After finishing **each** task: change its line from `- [ ] >>> ID` to `- [x] ID`, move `>>>` to the next unchecked task (or onto the gate item), update the SESSION-CONTEXT block (`last_session_date`, `last_task`, `next_task`, `notes`) and the human Session Context section, update the Progress table, and register any new documents in Project Artifacts. Commit after each task (KB repos push to main; code repos commit on a branch).
- Before reporting progress, audit each claim against a tool result from this session. Only report work you can point to evidence for; if something is not yet verified, say so. If tests fail, say so with the output; if a step was skipped, say that.
- Pause for the user only when the work genuinely requires it: a destructive or irreversible action, a real scope change, or input only they can provide. If you hit one, write it into the roadmap's `blockers:` field and Open Questions, leave `>>>` where it is, and end the turn.
- If a task is impossible as written, note why in the roadmap (Open Questions), leave it unchecked, move `>>>` past it, and continue.
- After each task, append a section to the day's work log `{WORKLOG_DIR}/YYYY-MM-DD-<project>.md` (create it from `{KB_DIR}/_system/Templates/work-log-entry-template.md` if absent; one file per project per day).
{gate_instructions}
## Context

### Session Context
- Last session: {session_ctx.get('last_session_date', session_ctx.get('last_session', 'N/A'))}
- Last task: {session_ctx.get('last_task', 'N/A')}
- Blockers: {session_ctx.get('blockers', 'none')}
- Notes: {session_ctx.get('notes', 'N/A')}

### Current Phase

{phase_context}
{prd_section}"""


# ---------------------------------------------------------------------------
# Gate handling
# ---------------------------------------------------------------------------


def write_gate_file(roadmap_path: str, gate: dict, meta: dict, content: str, project_arg: str) -> None:
    completed = [
        f"- {m.group(1)} {m.group(2)}"
        for m in (re.match(r"\s*-\s*\[x\]\s*([\d.]+)\s+(.*)", ln) for ln in content.splitlines())
        if m
    ]
    completed_list = "\n".join(completed) if completed else "- (none yet)"

    verification_path = os.path.join(os.path.dirname(roadmap_path), VERIFICATION_FILENAME)
    verification = ""
    if os.path.isfile(verification_path):
        with open(verification_path) as f:
            verification = f.read().strip()
    verification_section = (
        f"## Verifier Findings (`{verification_path}`)\n\n{verification}\n"
        if verification
        else "## Verifier Findings\n\n_No gate-verification.md was produced — treat the gate with extra scrutiny._\n"
    )

    gate_content = f"""# Quality Gate Review

**Project:** {meta.get('project', 'Unknown')}
**Entity:** {meta.get('entity', 'Unknown')}
**Roadmap:** `{roadmap_path}`
**Gate:** {gate['id']} — {gate['description']}
**Reached:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}

## What This Gate Asks You to Review

{gate['description'].replace('GATE:', '').strip()}

{verification_section}
## Completed Tasks Leading Up to This Gate

{completed_list}

## Options

1. **Approve** — "approved, continue"; Claude marks the gate done and moves `>>>`
2. **Request changes** — describe what must change before proceeding
3. **Reject** — stop the project and explain why

## To Resume the Runner After Approval

```bash
python3 ~/Knowledge-Base/_system/scripts/run-project.py {project_arg}
```
"""
    with open(GATE_FILE, "w") as f:
        f.write(gate_content)
    log(f"Gate file written to {GATE_FILE}")


def open_gate_session(roadmap_path: str) -> None:
    try:
        subprocess.run(["open", "-a", VIEWER_APP, roadmap_path], check=False, capture_output=True)
    except FileNotFoundError:
        subprocess.run(["open", roadmap_path], check=False, capture_output=True)

    gate_prompt = f"Read {GATE_FILE} and present the gate review for my approval."
    apple_script = f'''
    tell application "Terminal"
        activate
        do script "cd ~/Knowledge-Base && claude \\"{gate_prompt}\\""
    end tell
    '''
    try:
        subprocess.run(["osascript", "-e", apple_script], check=False, capture_output=True)
    except FileNotFoundError:
        log("Warning: Could not open Terminal via osascript")


# ---------------------------------------------------------------------------
# Claude execution
# ---------------------------------------------------------------------------


def run_claude(prompt: str, working_dir: str, timeout_hours: float, permission_mode: str) -> str:
    """Run one Claude CLI invocation, streaming output to the log. Returns 'ok', 'failed', or 'timeout'."""
    log(f"Starting Claude run in {working_dir} (timeout {timeout_hours}h, permission-mode {permission_mode})")
    log(f"Prompt length: {len(prompt)} chars")
    os.makedirs(LOG_DIR, exist_ok=True)
    try:
        with open(LOG_FILE, "a") as logf:
            proc = subprocess.Popen(
                ["claude", "-p", "--permission-mode", permission_mode, prompt],
                cwd=working_dir,
                stdout=logf,
                stderr=subprocess.STDOUT,
                text=True,
            )
            try:
                proc.wait(timeout=timeout_hours * 3600)
            except subprocess.TimeoutExpired:
                proc.kill()
                log(f"Claude run timed out after {timeout_hours}h")
                return "timeout"
        if proc.returncode == 0:
            log("Claude run completed")
            return "ok"
        log(f"Claude run exited with code {proc.returncode}")
        return "failed"
    except FileNotFoundError:
        log("Error: 'claude' CLI not found in PATH")
        return "failed"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Autonomous task runner for project roadmaps")
    parser.add_argument("project", help="entity/project (e.g. burn-app/engineering-excellence)")
    parser.add_argument("--timeout-hours", type=float, default=DEFAULT_TIMEOUT_HOURS,
                        help=f"Max hours per Claude run (default {DEFAULT_TIMEOUT_HOURS})")
    parser.add_argument("--max-runs", type=int, default=DEFAULT_MAX_RUNS,
                        help=f"Max Claude invocations before giving up (default {DEFAULT_MAX_RUNS})")
    parser.add_argument("--permission-mode", default=DEFAULT_PERMISSION_MODE,
                        help=f"Claude permission mode (default {DEFAULT_PERMISSION_MODE})")
    parser.add_argument("--dry-run", action="store_true", help="Show the prompt without running")
    args = parser.parse_args()

    log(f"=== Runner start: {args.project} ===")

    roadmap_path = find_roadmap(args.project)
    if not roadmap_path:
        log(f"Error: no roadmap found for '{args.project}'")
        notify("Runner Error", f"No roadmap found for {args.project}")
        sys.exit(1)
    log(f"Roadmap: {roadmap_path}")

    runs = 0
    previous_current_id: str | None = None

    while runs < args.max_runs:
        with open(roadmap_path) as f:
            content = f.read()
        meta = parse_roadmap_meta(content)
        session_ctx = parse_session_context(content)

        current = find_current_task(content)
        if not current:
            log("No >>> marker on an unchecked task. Project may be complete.")
            notify("Runner", f"{args.project}: no open tasks found")
            break

        if current["is_gate"]:
            log(f"Gate reached: {current['id']} {current['description']}")
            write_gate_file(roadmap_path, current, meta, content, args.project)
            notify("Quality Gate", f"{meta.get('project', args.project)}: {current['description']}")
            open_gate_session(roadmap_path)
            break

        if current["id"] == previous_current_id:
            log(f"Task {current['id']} did not advance after the last run. Stopping to avoid a loop.")
            notify("Runner Error", f"Task {current['id']} stuck — roadmap not updated")
            break

        batch, gate = tasks_until_gate(content)
        if not batch:
            log("Nothing to run before the next gate.")
            break
        log(f"Batch: {', '.join(t['id'] for t in batch)}" + (f" → gate {gate['id']}" if gate else " (no gate)"))

        working_dir = batch[0].get("repo_override") or meta.get("repo") or os.path.dirname(roadmap_path)
        working_dir = os.path.expanduser(working_dir)
        if not os.path.isdir(working_dir):
            log(f"Warning: working dir '{working_dir}' missing; using roadmap dir")
            working_dir = os.path.dirname(roadmap_path)

        prompt = generate_prompt(content, roadmap_path, batch, gate, meta, session_ctx)

        if args.dry_run:
            log(f"[DRY RUN] would run in {working_dir}")
            print("\n" + prompt)
            break

        previous_current_id = current["id"]
        runs += 1
        result = run_claude(prompt, working_dir, args.timeout_hours, args.permission_mode)

        if result != "ok":
            notify("Runner Error", f"{args.project}: run {runs} {result}")
            break
        time.sleep(2)

    log(f"=== Runner end: {runs} run(s) for {args.project} ===")
    if runs >= args.max_runs:
        notify("Runner", f"Reached {args.max_runs} runs for {args.project} without hitting the gate")


if __name__ == "__main__":
    main()
