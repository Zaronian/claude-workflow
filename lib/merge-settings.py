#!/usr/bin/env python3
"""
merge-settings.py — Merge workflow settings into an existing settings.json.

Takes the existing ~/.claude/settings.json and merges in entries from
settings-base.json, preserving all existing configuration while adding
new workflow components.

Usage:
    python3 merge-settings.py <existing-settings> <base-settings> <home-dir>

The merged result is written to stdout. The caller (setup.sh) handles
backup and file replacement.

Merge rules:
- permissions.allow: append entries not already present (exact string match)
- permissions.deny: append entries not already present (exact string match)
- hooks.*: add hook entries whose command doesn't already exist
- statusLine: add only if not already configured
- model: NEVER change (preserve user's choice)
"""

from __future__ import annotations

import json
import sys


def replace_placeholder(obj: object, home_dir: str) -> object:
    """Recursively replace $HOME_PLACEHOLDER with actual home directory."""
    if isinstance(obj, str):
        return obj.replace("$HOME_PLACEHOLDER", home_dir)
    elif isinstance(obj, list):
        return [replace_placeholder(item, home_dir) for item in obj]
    elif isinstance(obj, dict):
        return {k: replace_placeholder(v, home_dir) for k, v in obj.items()}
    return obj


def merge_permissions(existing: dict, base: dict) -> dict:
    """Merge permission allow/deny lists, deduplicating by exact string."""
    merged = {}

    for key in ("allow", "deny"):
        existing_list = existing.get(key, [])
        base_list = base.get(key, [])
        existing_set = set(existing_list)

        merged_list = list(existing_list)
        for entry in base_list:
            if entry not in existing_set:
                merged_list.append(entry)

        merged[key] = merged_list

    return merged


def get_hook_commands(hook_list: list[dict]) -> set[str]:
    """Extract command strings from a list of hook event entries."""
    commands = set()
    for event_entry in hook_list:
        for hook in event_entry.get("hooks", []):
            cmd = hook.get("command", "")
            if cmd:
                commands.add(cmd)
    return commands


def merge_hooks(existing: dict, base: dict) -> dict:
    """Merge hook configurations, skipping entries with duplicate commands."""
    merged = dict(existing)

    for event_type, base_entries in base.items():
        if event_type not in merged:
            merged[event_type] = base_entries
            continue

        existing_commands = get_hook_commands(merged[event_type])

        for base_entry in base_entries:
            base_commands = set()
            for hook in base_entry.get("hooks", []):
                cmd = hook.get("command", "")
                if cmd:
                    base_commands.add(cmd)

            # Only add if none of its commands already exist
            if not base_commands & existing_commands:
                merged[event_type].append(base_entry)
                existing_commands.update(base_commands)

    return merged


def merge_settings(existing: dict, base: dict) -> dict:
    """Merge base settings into existing, preserving all existing config."""
    merged = dict(existing)

    # Merge permissions
    if "permissions" in base:
        existing_perms = merged.get("permissions", {})
        merged["permissions"] = merge_permissions(existing_perms, base["permissions"])

    # Merge hooks
    if "hooks" in base:
        existing_hooks = merged.get("hooks", {})
        merged["hooks"] = merge_hooks(existing_hooks, base["hooks"])

    # Add statusLine only if not configured; on an existing block only add
    # refreshInterval (pacing gauges need the file refreshed while idle).
    if "statusLine" in base:
        if "statusLine" not in merged:
            merged["statusLine"] = base["statusLine"]
        elif isinstance(merged["statusLine"], dict) and "refreshInterval" in base["statusLine"] \
                and "refreshInterval" not in merged["statusLine"]:
            merged["statusLine"]["refreshInterval"] = base["statusLine"]["refreshInterval"]

    # NEVER touch model preference

    return merged


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python3 merge-settings.py <existing-settings> <base-settings> <home-dir>",
            file=sys.stderr,
        )
        sys.exit(1)

    existing_path = sys.argv[1]
    base_path = sys.argv[2]
    home_dir = sys.argv[3]

    with open(existing_path) as f:
        existing = json.load(f)

    with open(base_path) as f:
        base = json.load(f)

    # Replace placeholders with actual home directory
    base = replace_placeholder(base, home_dir)

    merged = merge_settings(existing, base)

    print(json.dumps(merged, indent=2))


if __name__ == "__main__":
    main()
