# /implement - Feature Implementation Workflow

Implement the requested feature end to end: $ARGUMENTS

## Workflow

1. **Understand** — Read the relevant code and any `CLAUDE.local.md` (test command, deploy notes). If the project has a decision log, grep its index for the area. Plan only as much as the change needs; if the diff could be described in one sentence, just make it.
2. **Implement** — Minimal, focused changes that follow the project's existing patterns. No refactors, abstractions, or features beyond the task.
3. **Test** — Add or update tests for the new behavior (happy path, edge cases, error handling) in the project's existing test layout. Run the full suite with the project's test command. Fix failures before continuing.
4. **Fresh-context review** — Launch a subagent that sees only the diff and the task description. Ask it to report gaps that affect correctness or the stated requirements (missing cases, untested paths, out-of-scope changes) — not style. Fix real findings; re-run tests.
5. **Report** — Lead with the outcome. Then: files changed, test results with the actual output, and any deployment steps from `CLAUDE.local.md`. Open the PR; merging additionally requires `/pr-review` PASS (Git rule in `~/CLAUDE.md`).
