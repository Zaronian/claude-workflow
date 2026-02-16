# Snowline Team Development Standards

These standards apply to all projects managed through Snowline Consulting's portfolio (Burn App, V School, Smash Creative, Volley, and all other client work).

---

## Project Organization

Everything lives under `~/Knowledge-Base/` (single root directory):

```
~/Knowledge-Base/                     # Single root for all KB content
├── _system/                          # Templates, hooks, system tools (local only)
├── daily-reviews/                    # Daily HTML reports (local only)
├── burn-app/                         # Git repo - burn-app/kb
├── v-school/                         # Git repo - VSchool/kb
├── smash-creative/                   # Git repo - Smash-Creative/kb
├── snowline/                         # Git repo - snowline-consulting/kb
├── volley/                           # Git repo - Zaronian/volley-kb
├── .claude/                          # Project settings & slash commands
└── CLAUDE.md                         # Project-level instructions
```

### Rules:
1. **New projects go in the appropriate business folder** under `projects/`
2. **Ask which business** if unclear before creating files
3. **Never create project folders at root level** of the Knowledge Base directory
4. **Each business has its own CLAUDE.md** with specific context - read it when working on that business
5. **Credentials stay in LastPass** - only reference them in KB folders, never store raw API keys

### Code vs Documentation:
- **Actual codebases** → `~/Code/[project-name]/` (git-controlled, cloned from GitHub)
- **Documentation, strategy, plans** → `~/Knowledge-Base/[org-name]/`
- **Local-only folders** (`_system/`, `daily-reviews/`) are not git repos
- Never mix code repos into the Knowledge Base folders

### Starting Work on a Business:
When beginning work on a specific business, read its CLAUDE.md first:
- `~/Knowledge-Base/burn-app/CLAUDE.md`
- `~/Knowledge-Base/v-school/CLAUDE.md`
- `~/Knowledge-Base/smash-creative/CLAUDE.md`
- `~/Knowledge-Base/snowline/CLAUDE.md`
- `~/Knowledge-Base/volley/CLAUDE.md`

---

## Knowledge Base Change Workflow

**Work logs and case studies push directly to main** — these are append-only records that don't benefit from review gates.

```bash
cd ~/Knowledge-Base/[org]
git checkout main && git pull
# make changes
git add [specific files]
git commit -m "Description of change"
git push origin main
```

### Key rules:
- **Push to main after each session** — don't let work sit uncommitted (protects against data loss)
- **Keep commits focused** — one logical change per commit, clear messages
- **Batch related changes** — if making multiple edits to the same repo, commit them together
- **Never commit secrets** — no API keys, passwords, .env files (pre-commit hook will block these)
- **Shared documentation edits** — when multiple people are editing the same docs, use branches + PRs to avoid conflicts

---

## Working Style: Push Forward Autonomously

**Default mode: Do as much as possible without stopping.**

### Complete Features End-to-End
- When implementing features that require data population or migration, **run them automatically** as part of the implementation
- Don't create admin buttons, intermediate pages, or manual steps that require user action
- If something can't be done automatically (needs credentials, external access), immediately state what's needed and offer to do what's possible
- **Never leave next steps unmentioned** - when finishing work, verify the feature is fully functional
- If deployment requires post-deploy actions (data imports, env vars), explicitly state this and handle it if possible

### Only pause when:
1. **Security-sensitive** - pushing to production, deleting data, operations that can't be undone
2. **Design decisions** - multiple valid approaches where user preference matters
3. **Explicitly asked** - "slow down," "keep me in the loop on X"
4. **Ambiguous requirements** - genuinely unclear what's wanted
5. **Settings & permissions changes** - ALWAYS get explicit confirmation before:
   - Modifying `~/.claude/settings.json`
   - Changing any permissions configuration
   - Altering CLAUDE.md workflow rules
   - Present the proposed change, explain the impact, and wait for approval

### Gather Credentials & Dependencies Upfront
Before starting execution on any task that involves third-party services, APIs, or external dependencies:
1. **Audit the full task** for every credential, API key, environment variable, npm package, or external service access needed
2. **Present the complete list** at the start — not piecemeal as you discover them
3. **Ask for everything at once** so credentials can be gathered while you work on parts that don't need them
4. **Include where to find each credential** (e.g., "Firebase Console → Service Accounts → Generate key")
5. **Don't start execution until dependencies are confirmed** — planning and research are fine, but don't write code that will immediately fail due to missing credentials

### Do NOT pause for:
- Running dev servers, tests, builds
- Routine code changes
- Standard git operations (commit, push)
- Any step that's clearly "the next logical thing to do"
- **Internet searches** - search any domain needed to complete tasks without asking permission
- **Bash commands** - run commands needed to complete tasks

---

## Project Lifecycle & Autonomous Execution

**Multi-session projects use roadmaps for tracking and autonomous execution.**

### Project Sizing

Before starting work, assess the project size:

| Size | Duration | Sessions | Required Artifacts |
|------|----------|----------|-------------------|
| **Small** | < 1 day | 1 | Nothing — just build it |
| **Medium** | 1-5 days | 2-5 | Project brief + lightweight roadmap |
| **Large** | 1-4 weeks | 5-15 | Brief + PRD + phased roadmap with gates |
| **Strategic** | 4+ weeks | 15+ | Brief + research + PRD + phased roadmap with gates |

### Decision Heuristics
- **Single session?** Skip the system, just work.
- **Multi-session?** Create a roadmap (`_system/Templates/roadmap-template.md`).
- **Large or strategic?** Write a PRD before execution. Add quality gates between phases.
- **Unclear size?** Start with a brief (`_system/Templates/project-brief-template.md`) to assess.

### Quality Gates

Gates are roadmap items prefixed with `GATE:` that force a pause for human review:
- **Phase boundaries** — always gate between phases on Large/Strategic projects
- **PRD approval** — before execution of any Large/Strategic phase
- **Deliverable review** — after significant outputs needing human judgment
- **Production deployments** — always gate before production changes

### Roadmap Format

Roadmaps use machine-readable HTML comments and human-readable markdown:
- `<!-- ROADMAP-META -->` — project-level metadata (entity, repo, size, status)
- `<!-- SESSION-CONTEXT -->` — cross-session state (last task, next task, blockers)
- `<!-- PHASE -->` — per-phase metadata
- `>>>` marker — current in-progress task (only one at a time)
- `GATE:` prefix — quality gate (task runner stops here)
- Standard `- [x]`/`- [ ]` checkboxes for progress tracking

### Working with Roadmaps

When a session involves a roadmapped project:
1. **Start**: Read the roadmap, find `>>>` current task, read SESSION-CONTEXT
2. **During**: Execute the current task, commit work
3. **End**: Mark task `[x]`, move `>>>` to next task, update SESSION-CONTEXT, update Progress table

### Autonomous Task Runner

`_system/scripts/run-project.py` reads the roadmap and executes tasks via Claude CLI:
- Finds the `>>>` task, generates a full-context prompt, runs `claude -p --permission-mode acceptEdits`
- Loops through tasks until hitting a GATE, completing all tasks, or reaching the session limit
- Sends macOS notifications at gates, errors, or completion
- Safety: stops if the same task isn't updated between sessions (prevents infinite loops)

### `/project` Command

Use `/project` for lifecycle management:
- `/project new` — create a project with brief + roadmap
- `/project status` — show current progress
- `/project start [entity/project]` — load context for manual session
- `/project end` — update roadmap and write work log
- `/project gate` — review and approve a pending quality gate
- `/project run [entity/project]` — kick off autonomous task runner

### Files

| File | Purpose |
|------|---------|
| `_system/Templates/roadmap-template.md` | Roadmap format with machine-readable metadata |
| `_system/Templates/project-brief-template.md` | Sizing assessment + kickoff document |
| `_system/scripts/run-project.py` | Autonomous task runner |
| `_system/scripts/open-roadmap.sh` | Open roadmap in viewer app |
| `.claude/commands/project.md` | `/project` slash command |
| `_system/active-gate.md` | Written by runner when a gate is reached |

---

## Structural Safeguards (Always-On Recovery Guarantees)

These safeguards ensure mistakes are always recoverable, eliminating the need for permission prompts.

### Before ANY potentially destructive operation:

**Git-tracked files:**
1. Run `git status` first - if there's uncommitted work, commit or stash it
2. Never `git push --force` to main/master
3. Never `git reset --hard` without first confirming uncommitted work is saved
4. Use branches for experimental changes

## Git Workflow: Branch & Pull Request

**Standard workflow for all code changes across all businesses.**

### Why Branches?
- Keeps `main` branch stable and deployable
- Changes are reviewed before merging
- Easy to abandon work that doesn't pan out
- Multiple people can work without conflicts

### Workflow Steps:

```
1. CREATE BRANCH
   git checkout -b feature/description-of-work

2. MAKE CHANGES
   Edit files, test locally

3. COMMIT CHANGES
   git add [files]
   git commit -m "Description of what changed"

4. PUSH BRANCH (run in Terminal - needs auth)
   git push -u origin feature/description-of-work

5. OPEN PULL REQUEST
   gh pr create --title "Title" --body "Description"
   (or do it in GitHub web UI)

6. GET REVIEW
   Team member reviews and approves

7. MERGE
   Reviewer merges PR into main

8. CLEAN UP
   git checkout main
   git pull
   git branch -d feature/description-of-work
```

### Branch Naming Conventions:
- `feature/short-description` - New functionality
- `fix/short-description` - Bug fixes
- `docs/short-description` - Documentation only
- `refactor/short-description` - Code cleanup

### Who Reviews?
Check each business's CLAUDE.md for specific reviewers. General rule:
- Developer reviews developer code
- Project lead reviews strategy/config changes

**Non-git files (databases, configs, data files):**
1. Before modifying: create a timestamped backup copy
2. Before deleting: confirm it's recoverable or explicitly backed up
3. Database changes: always backup first (`cp database.db database.db.backup-$(date +%Y%m%d-%H%M%S)`)

**File deletion:**
1. Never `rm -rf` on directories without first `ls` to see contents
2. For non-trivial deletions, move to trash/backup instead of permanent delete
3. If deleting git-tracked files, they're recoverable - proceed

**Production systems:**
1. ALWAYS pause before any production operation (deploys are OK, data changes are not)
2. Test locally/staging first
3. Create rollback plan before proceeding

### Recovery commands to know:
- `git reflog` - recover lost commits
- `git stash list` / `git stash pop` - recover stashed work
- `git checkout -- <file>` - restore file to last commit
- Database backups in project `backups/` directories

### Development Tools Required:
- **Homebrew** - Mac package manager (`brew install [package]`)
- **GitHub CLI** - Authenticated (`gh repo clone [org/repo]`)
- **Python 3.9+** - For hooks and scripts
- **jq** - JSON processing for statusline (`brew install jq`)
- **Git LFS** - Large file storage for binary files in KB repos

---

## Automated Safeguards (Installed)

### 1. Automatic Database Backups
Projects with import endpoints automatically create backups before any data modification:
- Location: `<project>/backups/`
- Format: `database.db.backup-YYYYMMDD-HHMMSS-<reason>`
- Retention: Last 10 backups kept automatically

### 2. Global Scratch/Backup Directory
Location: `~/.scratch/`
```
~/.scratch/
├── hooks/           # Reusable git hooks
│   └── pre-commit-secrets
└── backups/         # Temporary backups for non-project files
```

### 3. Pre-commit Secret Detection Hook
Installed in project repos to block accidental commits of:
- `.env` files
- Credentials files (*.pem, *.key, credentials.json)
- Code containing passwords, API keys, secrets
- Database connection strings with credentials

**To install in a new repo:**
```bash
cp ~/.scratch/hooks/pre-commit-secrets .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**To bypass (for false positives):**
```bash
git commit --no-verify
```

### When pausing, always explain WHY:
- Not just "here's what to do next"
- But "I'm stopping because [specific reason]"

---

## Documentation Maintenance

**Keep documentation current so future sessions have accurate context.**

### Proactive Updates (do automatically):
After any of these changes, update the relevant CLAUDE.md and README files:
- New tools installed (add to "Development Tools Required")
- New repos cloned
- Folder structure changes
- New credentials or API keys added
- New team members or processes documented
- Project status changes (started, completed, blocked)

### Files to consider updating:
- `~/CLAUDE.md` - Global settings, tools, workflows
- `~/Knowledge-Base/README.md` - Overall structure, active repos
- `~/Knowledge-Base/[org-name]/CLAUDE.md` - Business-specific context
- Project-specific README files

### Session End: Mandatory Work Logging

**Claude MUST write a work log entry at the end of every substantive session.** This is not optional.

**Definition of "substantive":** Any session that produces a deliverable, makes a decision, solves a problem, or advances a project. Skip only for trivial/purely conversational sessions with no deliverables.

**All work logs and case studies go to Snowline Consulting** — regardless of which entity the work was for. Snowline is the consulting practice; all entities are Snowline's clients/portfolio. This is where progress, ROI, and case studies aggregate.

**Process:**
1. Before writing the log, ask 1-2 brief questions to capture strategic context that Claude can't infer:
   - "What does getting this done unlock for the business?"
   - "How does this fit into the bigger picture?"
   - Or similar — keep it lightweight, ~30 seconds to answer
2. Write the work log entry to `~/Knowledge-Base/snowline/work-logs/YYYY-MM-DD-[slug].md`
   - Follow the template in `~/Knowledge-Base/_system/Templates/work-log-entry-template.md`
   - **Always save to snowline**, even if the work was for V School, Burn, Volley, etc.
   - Include the entity name in the log entry itself (e.g., "Entity: V School")
3. Save case studies to `~/Knowledge-Base/snowline/case-studies/`
4. Do NOT ask permission to create the log — just ask the strategic questions, then write it
5. Push work logs and case studies directly to main (no branch/PR needed)
6. Update any relevant documentation (CLAUDE.md, README files) if the session changed infrastructure

**Rate tiers for time-saved calculations:**
- **$35/hr** — Research, admin, documentation, planning, strategy
- **$75/hr** — Coding, development, technical implementation, debugging

---

## Continuous Improvement: Proactively Optimize Our Workflow

**Actively look for ways to make collaboration more efficient.**

### Watch for patterns:
- Repeated instructions or corrections → suggest adding to CLAUDE.md
- Workflows that could be automated or streamlined
- Questions asked repeatedly that could be pre-answered
- Preferences expressed in passing that should be documented

### When you notice something:
- Suggest a specific addition to CLAUDE.md or a new skill
- Explain the pattern observed and why the change would help
- Keep suggestions practical and concrete

### Research and recommend:
- If a better tool, approach, or best practice exists for what we're doing, mention it
- Don't just do things the obvious way - consider if there's a smarter way
- Share relevant techniques from software engineering, productivity, etc.

### Timing:
- Suggest improvements naturally when they're relevant (not forced)
- At natural breakpoints in work, briefly note any patterns worth capturing
- Don't interrupt flow for minor optimizations - batch them

---

## Development Workflow

When implementing features or making changes, follow this workflow:

### Discovery-to-Issue Rule

When a bug, missing auth check, architectural concern, dead code, or code inconsistency is discovered during **any** phase of work — planning, implementation, testing, or review — **file a GitHub issue immediately** in the relevant code repo. Do not just document it in a PRD, conversation summary, or work log. Those artifacts may reference the issue but are not substitutes for tracking it.

This prevents discoveries from getting lost between sessions. PRD "Discoveries" sections and conversation summaries get buried — GitHub issues show up in the backlog where they can be triaged.

### 1. Plan
- Understand the full scope before writing code
- Identify affected files and dependencies
- Consider edge cases and error scenarios
- For non-trivial changes, use `EnterPlanMode` to document approach

### 2. Implement
- Make focused, minimal changes that accomplish the goal
- Follow existing code patterns and conventions in the project
- Don't over-engineer or add unnecessary features

### 3. Test
- **Always write or update tests when adding/modifying functionality**
- Tests should verify the feature works as expected
- Tests should cover edge cases and error conditions
- Run existing tests to ensure nothing broke

### 4. Verify
- Run the full test suite before considering work complete
- Manually verify the feature works if tests alone aren't sufficient
- Check for common issues: template errors, null handling, type mismatches

### 5. Deploy
- Only deploy after tests pass
- Follow project-specific deployment instructions (check CLAUDE.local.md)
- Monitor for errors after deployment

---

## Testing Standards

### When to Write Tests
- Adding a new endpoint or route
- Adding a new feature or significant functionality
- Fixing a bug (write a test that would have caught it)
- Modifying behavior that could affect other parts of the system

### What to Test
- **Happy path**: The feature works with valid input
- **Edge cases**: Empty data, missing fields, boundary values
- **Error handling**: Invalid input, not found scenarios
- **Integration points**: Ensure components work together

### Test Structure
```python
# Example test structure for web apps
class TestFeatureName:
    def test_feature_basic(self, client):
        """Basic functionality works."""
        response = client.get("/endpoint")
        assert response.status_code == 200

    def test_feature_edge_case(self, client):
        """Edge case is handled."""
        response = client.get("/endpoint?param=edge")
        assert response.status_code == 200

    def test_feature_error(self, client):
        """Error case returns appropriate response."""
        response = client.get("/endpoint/invalid")
        assert response.status_code == 404
```

### Running Tests
- Before pushing: Run the project's test suite
- After deployment: Verify critical paths still work
- Check project's CLAUDE.local.md for specific test commands

---

## Code Quality Standards

### Before Committing
- All tests pass
- No obvious security issues (SQL injection, XSS, exposed secrets)
- Error handling for user-facing code paths
- No hardcoded credentials or sensitive data

### File Organization
- Keep related code together
- Follow existing project structure
- Don't create unnecessary abstractions for one-time code

---

## Documentation Standards

### When to Create/Update README Files

Proactively create or update a README.md when:

1. **Creating automation** - Any scripts, batch processes, or multi-file systems
2. **Building workflows** - Processes with multiple steps or files that work together
3. **Cross-session work** - Anything that will need context in future conversations
4. **New directories** - When creating a new project folder with multiple files
5. **Complex changes** - After significant modifications to existing systems

### What README Should Include

- **Purpose** - What this does and why it exists
- **Current status** - What's done, what's pending
- **How to use** - Commands, examples, common operations
- **File structure** - What each file does (if multiple files)
- **Key decisions** - Why choices were made

### When NOT Needed

- Single-file scripts with obvious purpose
- Temporary/scratch work
- Files that are self-documenting (well-commented code)

### Context Maintenance for Multi-Project Work

With multiple businesses and projects:
- Each project directory should have its own README.md or CLAUDE.local.md
- Update README when significant work is completed
- Include "Current Status" section so future sessions know where things left off
- Reference README at start of new sessions on existing projects

---

## UI/UX Preferences

- **HTML files**: Automatically open in browser after creating (using `open` command on macOS)
- **Prompts for new sessions**: When providing a prompt to paste into a new terminal/Claude session, display it in the conversation for readability AND automatically copy a clean version to the clipboard (`pbcopy`). Always confirm with a note like "It's on your clipboard — just Cmd+V into the new terminal." This avoids line-break issues from terminal copy-paste.

### Session Handoffs

**Proactively recognize when to end a session and start a new one.** Don't wait to be asked — suggest it when you notice a natural breakpoint.

**Triggers:**
- **Planning → building shift** — research/planning is done, next step is writing code
- **Heavy context window** — lots of files read, long conversation, fresh session will perform better
- **Entity/project switch** — shifting from one business to another
- **Phase completion** — a milestone is done (PR merged, deploy complete, feature shipped) and the next chunk of work is distinct

**When triggering a handoff:**
1. Write the work log (per standard process)
2. Create a focused prompt for the next session with all necessary context
3. Auto-copy the prompt to clipboard via `pbcopy`
4. Suggest the handoff — don't just do it silently, but don't ask permission either. Say something like "Good breakpoint — here's a prompt for the next session" and have it ready.

---

## Project-Specific Configuration

Each project may have a `CLAUDE.local.md` file with:
- Database configuration
- Deployment instructions
- Test commands
- Project-specific notes

Always check for and reference `CLAUDE.local.md` when working on a project.

---

## Skills

### /implement
Use this skill when the user wants a complete feature implementation with proper testing.

This skill bundles the full workflow:
1. Plan the implementation
2. Write the code
3. Create/update tests
4. Run the test suite
5. Report results

Invoke with: `/implement <description of feature>`
