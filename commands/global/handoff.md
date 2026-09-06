# /handoff — Re-surface what a session last copied for the user

Arguments: `$ARGUMENTS` — optional: a session id, an `business/project`, or `index`.

Every session writes whatever it `pbcopy`s for the user (handoff prompts, "Need from you" blocks, shell commands) through `~/Knowledge-Base/_system/scripts/handoff.sh`, which stores it under `~/.claude/handoffs/`. Voice-to-text and other sessions overwrite the clipboard constantly; this command gets the item back for the cost of one small file read.

## Steps

1. Pick the file:
   - no argument → `~/.claude/handoffs/latest.md`
   - `index` → print `~/.claude/handoffs/index.md` (one line per session: id · project · kind · written) and stop
   - a session id → `~/.claude/handoffs/sessions/<id>.md`
   - an `business/project` → the newest `sessions/*.md` whose `project:` header matches
2. Print the file's body verbatim (after the header block), then re-copy the body to the clipboard:
   `tail -n +7 <file> | pbcopy` (the header is exactly six lines: `session`, `project`, `cwd`, `written`, `kind`, blank).
3. Say "It's on your clipboard." and, in one line, which session and when it was written.

Do not re-derive or rewrite the content; this is a retrieval command.
