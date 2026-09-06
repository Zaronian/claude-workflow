# /loose-ends — Find, finish, or queue what this session left open

Run at the end of every session (before the handoff) and whenever the user asks. Argument `$ARGUMENTS` optional: an business name to limit the scan.

## 1. Find

Scan every place this session could have left something dangling. Ground each item in a tool result, not memory:

- **PRs**: `gh pr list --author @me --state open` in every code repo touched; branches pushed but no PR; PRs approved but unmerged.
- **Repos**: `git status --short` in every repo and worktree touched (uncommitted work, stray untracked files); worktrees whose branch already merged (`git worktree list`).
- **Deploys**: merged code not deployed; migrations written but not applied; a deploy done but not noted in the project's checklist/roadmap.
- **Human-only actions** already asked of the user ("Need from you" blocks) that are still unanswered.
- **Promised docs**: README / CLAUDE.md updates the Documentation rule requires; ADR owed for a design commitment; roadmap `>>>` / Session Context not updated; work log missing.
- **Dated follow-ups** created this session (soak ends, verify-after-first-real-run, retirements).
- **Issues** filed this session with no owner or roadmap link; epic checklists not updated.
- **Memory** notes that should exist for a decision made this session.

## 2. Finish

Do now whatever the rules already allow: commit + push KB work, run `/pr-review` and merge/deploy passing PRs, apply additive migrations, update docs/roadmaps, prune merged worktrees, comment on issues. Stay inside the two-agent cap and the pacing rules.

## 3. Ask once

Items that are doable now but cost real time or budget, or where the user might prefer to defer: put them in ONE `AskUserQuestion` — "do now, or queue?" per item. Do not ask about items the rules already decide.

## 4. Queue the rest

Append every remaining item to the business's queue file:
- KB businesses: `~/Knowledge-Base/<business>/queue.md` (create from the format below if absent; commit + push to main).
- Local-only businesses (zaro-family, zaro-holdings, mobile-detailing): `~/Knowledge-Base/<business>/queue.md`.

Format — one line per item, newest first under **## Open**; move to **## Done** with the close date when finished:

```
- [ ] YYYY-MM-DD · **<what>** — <where/how to pick it up> (<source: project / PR / issue>) [owner: claude|michael] [due: YYYY-MM-DD if dated]
```

Rules: one item per line; the line must be enough to act on cold; never duplicate a roadmap `>>>` task (link to the roadmap instead); parked ideas go to memory or the roadmap's Open Questions, not the queue.

## 5. Report

One short list in the session: finished, asked, queued (with the queue file path). Then continue to the handoff.

## Pick-up

`/project start` and any session's opening glance should read the business's `queue.md` **## Open** section (it is short by design). A future triage agent will prioritize queued items across businesses.
