# [Business Name] — Company Facts

**KB owner:** [name — the one person whose sessions write to this KB] · **Verified:** YYYY-MM-DD

Single source for the facts below. Harness entry files (`CLAUDE.md`, and `AGENTS.md` if another agent is used) point here instead of restating them. When a fact changes, change it here and bump the date. Rules live in `CLAUDE.md`; facts live here.

## Overview

[One paragraph: what the business does, legal entity, ownership, current status.]

## Team

| Name | Role | Organization |
|------|------|-------------|
| | | |

*Dated corrections go here as italics, e.g. "Roster corrected YYYY-MM-DD: …" — keep history, don't rewrite it.*

## Accounts & Ownership

Secret values live in a gitignored `.env` or a password manager; **only variable names appear here.**

| Service | Account owner | Used by | Reference (env var name / location) |
|---|---|---|---|
| | | | |

**Rule:** the account follows the delivery owner, not the customer name. Work delivered by an outside firm runs on that firm's client-scoped accounts; work the business owns runs on its own. Never use another business's key.

## Active Projects

- `projects/<slug>/` — one line: what it is, phase/status, blocker if any.

## Code Repos

| Repo | Location | Remote | Stack | Package manager |
|------|----------|--------|-------|---|
| | | | | (from the lockfile) |
