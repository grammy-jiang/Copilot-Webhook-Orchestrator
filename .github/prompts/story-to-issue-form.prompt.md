---
name: story-to-issue-form
description: Convert a user story draft into GitHub Issue Form-compatible format ready for backlog entry
---

# Convert Story to Issue Form Format

You are converting a user story draft into the exact format required by the
GitHub Issue Form template at `.github/ISSUE_TEMPLATE/02-user-story.yml`.

## Input

${input:story:Paste the user story draft or feature description}

## Task

Transform the input into a structured format that can be directly copied into
the GitHub Issue Form. Ensure all required fields are populated.

## Output Format

Generate output with these exact sections:

### Title

`[Story]: <concise title>`

### Epic / Feature Reference

`#<number>` or `<Feature Name>` (if applicable, otherwise "None")

### User Story Statement

```
As a [specific persona],
I want [specific capability],
So that [specific benefit].
```

### Business Value

- User benefit: [specific benefit]
- Business benefit: [specific benefit]
- Success metric: [quantified measure]

### Acceptance Criteria: Happy Path

**Scenario 1: [Descriptive Name]**

- Given [specific initial context]
- When [specific action is performed]
- Then [specific expected outcome]

**Scenario 2: [Descriptive Name]**

- Given [specific initial context]
- When [specific action is performed]
- Then [specific expected outcome]

### Acceptance Criteria: Edge Cases & Negative Scenarios

**Edge Case: Empty State**

- Given [no data / empty condition]
- When [user performs action]
- Then [appropriate empty state handling]

**Edge Case: Permission Denied**

- Given [user lacks required permission]
- When [user attempts restricted action]
- Then [clear permission error with guidance]

**Edge Case: Validation Failure**

- Given [invalid input condition]
- When [user submits]
- Then [specific validation error messages]

**Edge Case: Network/Timeout Error**

- Given [network unavailable or slow]
- When [action requires network]
- Then [graceful degradation / retry option]

### Out of Scope

- [Explicit item 1 NOT included in this story]
- [Explicit item 2 NOT included in this story]
- [Explicit item 3 NOT included in this story]

### Dependencies

- [Dependency 1: other story, API, design, team]
- [Dependency 2]
  (or "None" if no dependencies)

### Open Questions

- [ ] [Clarification question 1]
- [ ] [Clarification question 2]
  (or "None" if all questions resolved)

### Technical Notes

- Affects: [files/modules]
- Consider: [technical considerations]
- Watch out for: [potential issues]
  (or "None" if no technical notes)

### Definition of Ready Checklist

- [x] User value is clearly stated
- [x] Success metric is defined (quantified when possible)
- [x] Acceptance criteria are complete (happy path + edge cases)
- [x] Dependencies are identified
- [x] Out of scope is explicitly listed
- [ ] Data model impact is assessed (new fields, migrations)
- [ ] Security/privacy implications are reviewed
- [ ] Telemetry/observability requirements are defined
- [ ] UX states are defined (loading, empty, error)
- [ ] Rollout strategy is considered (feature flags, canary)

## Rules

1. **Do not skip any section** — use "None" or "N/A" if not applicable
1. **Be specific** — avoid vague statements like "handle errors appropriately"
1. **Include at least 4 edge cases** — empty, permission, validation, network
1. **Quantify success metrics** — use numbers, percentages, or measurable outcomes
1. **Mark DoR items honestly** — check only what is actually addressed
