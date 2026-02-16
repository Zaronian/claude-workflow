# /implement - Full Feature Implementation Workflow

Implement the requested feature following proper software engineering practices.

## Input
$ARGUMENTS - Description of the feature to implement

## Workflow

Follow these steps in order:

### Step 1: Plan
- Read relevant existing code to understand the codebase
- Identify all files that need to be created or modified
- Consider edge cases and error handling
- If the change is non-trivial, document the approach before coding

### Step 2: Implement
- Write clean, focused code that accomplishes the goal
- Follow existing patterns and conventions in the project
- Don't over-engineer - make minimal changes needed

### Step 3: Write Tests
- Create tests for the new functionality
- Tests should cover:
  - Happy path (feature works with valid input)
  - Edge cases (empty data, boundary values)
  - Error handling (invalid input, not found)
- Add tests to the project's existing test file or create one if needed

### Step 4: Run Tests
- Execute the full test suite
- Check the project's CLAUDE.local.md for the correct test command
- Common commands: `pytest tests/ -v`, `npm test`, `cargo test`
- Ensure all tests pass before proceeding

### Step 5: Report Results
After completing:
- Summarize what was implemented
- List files created/modified
- Report test results (passed/failed)
- Note any deployment steps needed (check CLAUDE.local.md)

## Example Usage

User: `/implement Add a logout button to the navbar`

Claude will:
1. Read navbar component to understand structure
2. Add logout button with appropriate handler
3. Write test that verifies logout button renders and works
4. Run test suite
5. Report: "Added logout button to navbar.html, created test in test_auth.py, all 15 tests passing"

## Important Notes

- Always check for CLAUDE.local.md for project-specific instructions
- Don't deploy automatically - just report that tests pass
- If tests fail, fix the issues before reporting completion
