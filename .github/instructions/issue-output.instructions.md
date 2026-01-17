---
applyTo: "**/*issue*,**/*story*,**/*feature*,**/*bug*,**/*adr*,**/*incident*"
---

# Issue Output Format Instructions

These instructions apply when generating content for GitHub Issues.

## Output Structure

When generating issue content, structure your output to match the corresponding
Issue Template in `.github/ISSUE_TEMPLATE/`.

### For User Stories (`02-user-story.yml`)

Output must include these sections in order:

```markdown
## User Story Statement
As a [persona], I want [capability], so that [benefit].

## Business Value
[Why this matters]

## Acceptance Criteria: Happy Path
**Scenario 1: [Name]**
- Given [context]
- When [action]
- Then [outcome]

## Acceptance Criteria: Edge Cases & Negative Scenarios
**Edge Case: Empty State**
- Given [context]
- When [action]
- Then [outcome]

**Edge Case: Permission Denied**
- Given [context]
- When [action]
- Then [outcome]

**Edge Case: Validation Failure**
- Given [context]
- When [action]
- Then [outcome]

## Out of Scope
- [What is NOT included]

## Dependencies
- [Other stories, APIs, designs]

## Open Questions
- [ ] [Question 1]
- [ ] [Question 2]

## Definition of Ready Checklist
- [ ] User value is clearly stated
- [ ] Success metric is defined
- [ ] Acceptance criteria are complete (happy + edge)
- [ ] Dependencies are identified
- [ ] Out of scope is listed
```

### For Feature Requests (`01-feature-request.yml`)

Output must include:

```markdown
## Problem Statement
[What problem, who is affected, current workaround]

## Proposed Solution
[Desired outcome]

## Success Metrics
[How we measure success]

## Constraints & Dependencies
[Time, compliance, platform, dependencies]

## Alternatives Considered
[Other options evaluated]
```

### For Bug Reports (`03-bug-report.yml`)

Output must include:

```markdown
## Current Behavior
[What actually happens]

## Expected Behavior
[What should happen]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Environment
- OS: [e.g., macOS 14.0]
- Browser: [e.g., Chrome 120]
- Version: [e.g., v1.2.3]

## Severity
[Critical/High/Medium/Low]
```

### For Architecture Decisions (`04-architecture-decision.yml`)

Output must include:

```markdown
## Context
[Situation requiring decision, forces at play]

## Decision Drivers
[Criteria for decision]

## Options Considered

### Option 1: [Name]
**Pros:** [List]
**Cons:** [List]

### Option 2: [Name]
**Pros:** [List]
**Cons:** [List]

## Decision
[Chosen option and rationale]

## Consequences
**Positive:** [List]
**Negative:** [List]
**Risks:** [List with mitigations]
```

### For Incident Reports (`08-incident-report.yml`)

Output must include:

```markdown
## Incident Summary
[Brief factual summary]

## Impact Assessment
[Users affected, business impact, systems affected]

## Timeline
| Time (UTC) | Event |
|------------|-------|
| HH:MM | [Event] |

## Root Cause Analysis
[5 Whys or equivalent]

## Resolution
[How it was fixed]

## Action Items
| Action | Owner | Priority | Due Date |
|--------|-------|----------|----------|
| [Action] | @person | High/Med/Low | YYYY-MM-DD |
```

## Validation Rules

Before finalizing issue content:

1. ✅ All required fields from the template are present
1. ✅ Acceptance criteria include at least 1 happy path + 2 edge cases
1. ✅ Out of scope is explicit (not empty)
1. ✅ Given/When/Then format is used for all scenarios
1. ✅ No invented fields that don't exist in the template
