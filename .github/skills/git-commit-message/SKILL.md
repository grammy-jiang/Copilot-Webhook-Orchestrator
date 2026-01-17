---
name: git-commit-message
description: Create a well-formatted Conventional Commits message and commit it. Trigger when the user asks to write a commit message and/or commit the changes (e.g., "write well formatted git commit message", "commit with this message", "commit these changes", "commit now", "commit staged files").
license: MIT
metadata:
  author: grammy-jiang
   version: "1.3"
---

# Git Commit + Message Skill

Create a well-structured commit message and, with user approval, run `git commit` using that message.

## When to Activate This Skill

Trigger this skill for any request to write a commit message and/or commit code, including:

- "write well formatted git commit message"
- "commit with this message" / "commit using this message"
- "commit these changes" / "commit now" / "commit the staged files"
- "create a commit message" / "generate a commit message"
- "save to git" / "check in" / "git commit" / "commit and push"
- "review my commit message" / "is this a good commit message"

## Commit Message Structure

A commit message has three parts: **header** (required), **body** (optional),
and **footer** (optional).

### Header (Subject Line)

1. Use imperative mood (e.g., "Add", "Fix", "Update", not "Added", "Fixed",
   "Updated")
1. Start with a capital letter
1. Do not end with a period
1. Limit to 50 characters maximum
1. Complete the sentence: "If applied, this commit will..."

### Body

1. Separate from header with a blank line
1. Wrap lines at 72 characters
1. Explain **what** changed and **why** (not how)
1. Include relevant context, background, or reasoning

### Footer

1. Reference issues: `Closes #123`, `Fixes #456`, `See also: #789`
1. Note breaking changes: `BREAKING CHANGE: description`
1. Add co-authors: `Co-authored-by: name <email@example.com>`

## Steps to Create and Apply a Commit

Follow this workflow when asked to write a commit message and/or commit the changes:

1. **Check staged changes**
   - Run `git diff --cached` to see staged changes.
   - If empty: tell the user nothing is staged and suggest `git add <files>`.

2. **Analyze the diff**
   - Purpose: feature, fix, docs, refactor, etc.
   - Scope: module/area touched.
   - Impact: any breaking change?
   - Issues: any referenced tickets?

3. **Pick the commit type** (Conventional Commits)
   - `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`, `perf`, `ci`, `revert`

4. **Draft the commit message**
   - **Header:** `<type>(<scope>): <description>` (≤50 chars)
   - **Body (optional):** what + why, wrapped at 72 chars
   - **Footer (optional):** issue refs, breaking change notice, co-authors

5. **Show the message** to the user for approval

6. **Commit when approved**
   - Single-line: `git commit -m "header"` (and add `-m "body" -m "footer"` if present)
   - Or open editor: `git commit`

7. **Confirm success**
   - Show latest commit: `git log -1 --pretty=format:"%h - %s"`

## Format and Examples

### Message Structure

```
<type>(<scope>): <description>

[optional body explaining what and why, not how]

[optional footer with issue refs, breaking changes, or co-authors]
```

**Key Rules:**
- **Imperative mood:** Use "Add", "Fix", "Update" (not "Added", "Fixed", "Updated")
- **Capital first letter:** Start with uppercase
- **No period:** Don't end header with a period
- **50 char header max:** Keep subject line concise
- **72 char body wrap:** Wrap body text for terminal readability
- **Blank line separation:** Separate header from body and body from footer
- **Explain why:** Focus on motivation and implications, not code mechanics
- **Be specific:** Mention the component or module affected
- **No vague messages:** Avoid "Fix stuff", "Update", "Changes" without context
- **No meta-commentary:** Don't say "this commit" or "in this PR"
- **No personal pronouns:** Avoid "I fixed" – use imperative instead
 - **Ready to apply:** Ensure the message is final before running `git commit`

### Example Commits

**Simple fix (feature or bug):**
```
fix(auth): handle null pointer in user login flow
```

**Feature with body:**
```
feat(oauth): add OAuth 2.0 authentication support

Implement OAuth 2.0 login using the external provider library.
This introduces a new callback endpoint and updates the user
model with OAuth tokens for secure authentication.

Closes #42
```

**Breaking change:**
```
refactor(api)!: standardize response format

Standardize all API endpoints to return responses in a unified
JSON structure with status, data, and error fields.

BREAKING CHANGE: API responses now use a new envelope format.
Clients must update their parsing logic.

Closes #128
```

**With co-author:**
```
perf(cache): improve user profile API caching

Reduce database queries by implementing Redis caching for
frequently accessed user profile data. This improves response
times by approximately 40%.

Co-authored-by: Jane Doe <jane@users.noreply.github.com>
```

**Documentation update:**
```
docs(readme): update installation instructions

Add steps for Docker-based setup and troubleshooting section
for common installation issues on Windows.
```

**Test addition:**
```
test(api): add integration tests for auth endpoints

Cover happy path, invalid credentials, and rate limiting
scenarios for login and registration endpoints.
```

## Quality Standards

Every commit message must follow these rules:

- **One logical change per commit** – keep commits focused and atomic
- **Describe impact, not mechanics** – explain what changed and why, not the code mechanics
- **Complete the sentence** – your header should complete: "If applied, this commit will..."
- **Include scope when possible** – `fix(module)` is clearer than just `fix`
- **Reference related issues** – use `Closes #123`, `Fixes #456`, `Related to #789`
- **Flag breaking changes** – use `!` in header or `BREAKING CHANGE:` in footer
- **Provide context** – body text should explain the *why* and *what*, not the *how*
- **Use past-tense body** – describe what was done in past tense in the body
- **No abbreviations** – spell out terms clearly for future readers
- **Keep it focused** – if the message is hard to write concisely, the change may be too broad

## Workflow and Common Scenarios

### Scenario 1: "write well formatted git commit message"
1. Check `git diff --cached`.
2. Draft the message (type/scope/description, optional body/footer).
3. Show the message for approval.
4. On approval, run `git commit -m ...` and confirm.

### Scenario 2: "commit with this message <text>"
1. Validate the provided message against the format (type(scope): description).
2. Suggest any fixes (imperative, ≤50 chars header, etc.).
3. On approval, run `git commit -m ...` and confirm.

### Scenario 3: "commit these changes" / "commit now"
1. Check staged changes. If none, ask user to stage.
2. Draft the message following the steps.
3. Show for approval, then commit and confirm.

### Scenario 4: No staged changes
1. Run `git status`.
2. Inform: "No staged changes to commit."
3. Suggest: `git add <files>` then continue.

### Scenario 5: Multiple unrelated changes
1. Note that changes span different areas.
2. Offer: split into separate commits (X, Y) with separate messages.
3. Proceed per user choice.
