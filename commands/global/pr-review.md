# /pr-review — Fresh-context merge gate

Review $ARGUMENTS (a PR number or a branch) with eyes that did not write it. This is the merge condition for every code repo: **full test suite green + PASS here → merge, deploy, verify, tell the user.** The user does not review PRs by hand.

## Steps

1. **Gather the reviewer's context** — then hand it over; the reviewer must NOT inherit this conversation:
   - the PR diff (`gh pr diff <n>` or `git diff origin/main...<branch>`) and the PR body
   - the roadmap task text this PR implements (the `>>>` line or the task bullet)
   - the rows of the project's ADR `index.md` whose area the diff touches
   - `CLAUDE.local.md` test/deploy notes if present
2. **Run the reviewer as a fresh subagent** (general-purpose, no conversation context, read-only). Ask it to report only findings that matter, in this order, each with `file:line`, what fails, and how to see it fail:
   - **Correctness** — wrong behaviour, unhandled failure, data loss, race, silent fallback.
   - **Authorization / security** — an endpoint or write reachable outside the project's authz model (the project's authz ADRs, if any); secrets in the diff; injection.
   - **Tests** — untested paths for the new behaviour; tests that would pass without the change.
   - **ADR compliance** — contradicts an accepted ADR without a superseding one; a design commitment made without an ADR.
   - **Scope** — changes not needed for the task.
   Style-only findings are out of scope. The reviewer ends with `VERDICT: PASS` or `VERDICT: CHANGES` (PASS = no correctness / authz / ADR findings).
3. **Also run the built-in `/code-review high`** on the same target and merge its findings into the list.
4. **Fix real findings**, re-run the full suite, re-review once. **Two CHANGES verdicts → stop and ask the user** with the findings; do not merge.
5. **Report to the user in one paragraph**: verdict, what was fixed, test counts (actual output), merge/deploy status. Then proceed per the Git rules in `~/CLAUDE.md`.

## Notes

- Count this subagent against the two-agent cap in `~/CLAUDE.md` § Orchestration.
- The reviewer is read-only: it reports, the main session fixes.
- If the harness prompts on `gh pr merge`, that is a one-click approval for the user, not a reason to skip the gate.
