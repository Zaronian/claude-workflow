# /pr-review — Fresh-context merge gate

Review $ARGUMENTS (a PR number or a branch) with eyes that did not write it. This is the merge condition for every code repo: **full test suite green + PASS here → merge, deploy, verify, tell the user.** The user does not review PRs by hand.

**Models:** reviewer and finders run on **Opus** (`model: "opus"` on the Agent call); verifiers run on **Sonnet** (`model: "sonnet"`). Never let a review agent inherit the session model — the top-tier session-model pool is the binding usage limit and review work does not need it. Do **not** run the built-in `/code-review` or `/simplify` inside the gate: they fan out 15–20 agents on the session model, cap at ten recall-biased findings, and most of those are cleanup, which is not a merge condition.

## Steps

1. **Gather the reviewer's context** — then hand it over; the reviewer must NOT inherit this conversation:
   - the PR diff (`gh pr diff <n>` or `git diff origin/main...<branch>`) and the PR body
   - the roadmap task text this PR implements (the `>>>` line or the task bullet)
   - the rows of the project's ADR `index.md` whose area the diff touches
   - `CLAUDE.local.md` test/deploy notes if present
   - the changed-line count — it decides step 3: `gh pr diff <n> | grep -cE '^[+-][^+-]'` for a PR, `git diff origin/main...<branch> | grep -cE '^[+-][^+-]'` for a branch (the pattern excludes the `+++`/`---` file headers)
2. **Run the reviewer as a fresh subagent** (general-purpose, `model: "opus"`, no conversation context, read-only). It reads every hunk **and the enclosing function** of each hunk, then reports only findings that matter, in this order, each with `file:line`, what fails, and how to see it fail:
   - **Correctness** — wrong behaviour, unhandled failure, data loss, race, silent fallback. Three required passes: (a) line-by-line: for each changed line, what input, state, timing, or platform makes it wrong; (b) removed behaviour: for every deleted or replaced line, name the invariant it enforced and find where the new code re-establishes it; (c) callers: for each changed function, Grep its call sites and check for a new precondition, changed return shape, new exception, or ordering dependency.
   - **Authorization / security** — an endpoint or write reachable outside the project's authz model (the project's authz ADRs, if any); secrets in the diff; injection.
   - **Tests** — untested paths for the new behaviour; tests that would pass without the change.
   - **ADR compliance** — contradicts an accepted ADR without a superseding one; a design commitment made without an ADR.
   - **Scope** — changes not needed for the task.
   Style, reuse, simplification, and efficiency findings are out of scope. The reviewer ends with `VERDICT: PASS` or `VERDICT: CHANGES` (PASS = no correctness / authz / ADR findings).
3. **Large diffs only (more than ~300 changed lines):** launch two more Opus finders in parallel with the reviewer, same context, correctness only, up to six candidates each — one dedicated to the removed-behaviour audit (b), one to the caller trace (c). Skip this step for smaller diffs; the reviewer's own passes cover them.
4. **Verify, once, only what you would fix.** For each correctness or authz finding (from any agent) that would change code, run one Sonnet verifier in parallel with the others: give it the diff, the cited file(s), and the finding; it returns exactly one of CONFIRMED / PLAUSIBLE / REFUTED with one line of evidence. Keep CONFIRMED and PLAUSIBLE; drop REFUTED. A confirmed finding is never re-verified, and the main session does not run its own finder or verifier fan-out on top of this. **Then recompute the gate verdict:** PASS iff no correctness, authz, or ADR finding remains from *any* agent — where a verified finding remains if CONFIRMED or PLAUSIBLE, and a finding that was not sent to a verifier (every ADR finding; any correctness or authz finding you chose not to verify) stands as reported and blocks PASS. A finder's confirmed finding flips a reviewer PASS to CHANGES; a reviewer CHANGES whose findings were all REFUTED becomes PASS. Only this post-verification verdict counts as the gate's verdict below.
5. **Fix real findings**, re-run the full suite, then re-review **the delta only** (the fix commits, plus the original findings list) with one Opus reviewer. **Two post-verification CHANGES verdicts → stop and ask the user** with the findings; do not merge.
6. **Report to the user in one paragraph**: verdict, what was fixed, test counts (actual output), merge/deploy status. Then proceed per the Git rules in `~/CLAUDE.md`.

## Notes

- The gate's reviewer, finders, and verifiers are foreground agents the session waits on; per `~/CLAUDE.md` § Orchestration they do not count against the two-background-agent cap.
- Every review agent is read-only: it reports, the main session fixes.
- Cleanup review (reuse, simplification, efficiency, dead code) is worth doing, just not per PR: run `/simplify` deliberately on a branch when a module has accumulated debt, and let it produce its own PR.
- If the harness prompts on `gh pr merge`, that is a one-click approval for the user, not a reason to skip the gate.
