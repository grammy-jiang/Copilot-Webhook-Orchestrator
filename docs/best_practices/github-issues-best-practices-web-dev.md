# Best Practices for GitHub Issues in Website Development

GitHub lets you **configure issue templates** to standardize task tracking and
reporting. In your repository’s Settings under Issues, click **“Set up
templates”** to launch the template manager. You can use the template builder or
edit YAML files in `.github/ISSUE_TEMPLATE`. Templates allow you to pre-fill
issue content and defaults (title prefixes, labels, assignees, etc.) so
contributors give all needed details. For example, you might create separate
templates for *Bug Report*, *Feature Request*, *Content Update*, or *UI
Improvement*. Each template can include a default title (like “\[Bug\]: ”),
labels (e.g. `bug`, `help wanted`), and assignees. This ensures issues start
with a clear purpose and consistent metadata.

When creating new templates, use GitHub’s UI or add files to
`.github/ISSUE_TEMPLATE`. The **“Add template”** dropdown lets you pick a
standard type (bug, feature, etc.) or define a custom template. In the template
editor you set the **title, labels, assignees** and more – either via form
fields or YAML frontmatter. For instance, the YAML frontmatter can include keys
like `title:`, `labels:`, `assignees:`, and `type:` to auto-assign each new
issue. This saves repetitive work (e.g. always tagging new UI issues with
`frontend` or assigning a QA lead). After saving, contributors see your
templates when they click **“New issue”**, guiding them to the right format.

When a user clicks **“New issue”**, they see a **template chooser** showing each
issue template’s name and description. The chooser prompts the reporter to
select the most appropriate template. Templates provide guidance for opening
issues and issue *forms* ensure contributors give specific, structured
information. In practice, this means having tailored templates for website work:
e.g. a “Feature Request” form might ask for a user story, mockups, and
acceptance criteria, whereas a “Bug Report” form might ask for steps to
reproduce and environment details. By steering users to the right template, you
make sure each issue contains the relevant fields for its task.

GitHub supports **issue forms** written in YAML, which let you define rich input
fields. A form file must include top-level keys `name`, `description`, and
`body`. For example, a **Bug Report** form in YAML might look like this:

```yaml
name: Bug Report
description: File a bug report.
title: "[Bug]: "
labels: ["bug","needs-triage"]
projects: ["org/Website-1"]
assignees: [octocat]
type: bug
body:
  - type: markdown
    attributes:
      value: |
        **Describe what happened:** Please provide as much detail as you can.
  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: List the exact steps to reproduce the bug.
      placeholder: |
        1. Go to homepage
        2. Click login
        3. Submit form
    validations:
      required: true
  - type: input
    id: environment
    attributes:
      label: Environment
      description: Browser, OS, or device (e.g. “Chrome on Windows 10”)
      placeholder: e.g. macOS Big Sur, Firefox
    validations:
      required: true
```

This YAML defines the template name/description and form fields. Notice it
includes **default fields** like `title`, `labels`, and `assignees` at the top.
The `body` section lists form elements: here a markdown note and two fields (a
required textarea and input). GitHub’s form schema supports elements like
`input`, `textarea`, `dropdown`, `checkboxes`, and `markdown`. This lets you
require structured details (e.g. steps, environment, screenshots) before an
issue is submitted.

The result is a **rendered issue form** with labeled fields. Contributors fill
them in, and their answers are automatically formatted into the issue body as
Markdown upon submission. Using such forms ensures that every bug report or
feature request contains consistent information (e.g. reproducible steps,
environment, expected vs actual) without maintainers having to chase down
missing details. By defining clear prompts and validations, you encourage
complete, actionable issues from the start.

______________________________________________________________________

## Writing Clear and Complete Issue Content

- **Use a descriptive title.** Preface it with a category (e.g. “[Bug]” or
  “[Feature]”). A good title quickly tells the team what and where: for example,
  “[Bug] Login page crashes on submit”. Avoid vague titles like “Help needed” or
  “Feature”.

- **Explain the problem or request.** In the issue body, clearly describe *what*
  is happening (or what is needed) and *why* it matters. For bugs, state what
  you expected to happen and what actually happened. For features, outline the
  user story or goal. Issue templates often include headings like “Current
  behavior” and “Expected behavior” to guide this. If relevant, describe your
  environment (browser, OS, device) and setup.

- **List steps or acceptance criteria.** If reporting a bug, enumerate how to
  reproduce the issue. If requesting a feature, list key acceptance criteria or
  sub-tasks. Using a checklist (`- [ ]`) in Markdown can help break down
  multi-step tasks (e.g. front-end UI changes, backend API updates, testing).
  This makes it easy to track progress.

- **Include context and assets.** For website projects, attach screenshots,
  sketches or links to design specs when relevant. E.g. a bug report about
  layout should include a screenshot of the error. A content-update issue might
  include the draft text or a link to the style guide. Always link to related
  docs or issue/PR numbers (e.g. “Related to #123”).

- **Apply labels and assign ownership.** Use labels to categorize the issue by
  type (`bug`, `feature`, `documentation`, `SEO`, etc.), priority
  (`high-priority`), component (`frontend`, `backend`), or status (`needs-info`,
  `good-first-issue`). Labels help anyone filter and triage issues quickly.
  Assign the issue to a specific developer or team lead so it’s clear who’s
  responsible. Add the issue to any relevant Project board or milestone: a
  milestone can represent a release or sprint, showing overall progress.

- **Link commits and pull requests.** When a fix or feature is implemented,
  reference the issue in your commit or PR message (e.g. “Fixes #45”). GitHub
  will automatically **link and close** the issue when the PR is merged into the
  default branch. In PR descriptions, use closing keywords (`fixes`, `closes`)
  followed by the issue number. After merging, the issue will be closed and
  noted as resolved.

- **Keep issues focused.** Ideally one issue = one task. If a feature is large,
  break it into smaller issues or use “epic” labels. This makes progress
  trackable and avoids confusion. Use issue dependencies or projects to show
  relations if needed.

______________________________________________________________________

## Organizing Tasks with Dashboards

Beyond issues themselves, use GitHub’s project boards to create **dashboards**
for your website development work. A GitHub Project can display issues and pull
requests in a Kanban board, table or roadmap view. For example, you might have
columns like “To Do”, “In Progress”, “Review”, and “Done”. Dragging issues
across columns visualizes status at a glance. You can customize fields (e.g.
priority, effort estimates) and create charts for burn-down or velocity. This
acts as a live dashboard of your backlog and sprints. Because projects stay
synced with GitHub data, as issues get updated or closed, the board and any
roadmap charts update automatically. This is especially useful when you have
many concurrent website tasks (UI design, content work, SEO fixes) and want a
centralized view.

______________________________________________________________________

## Summary

The **best practice** is to leverage GitHub’s templates and tools to make issue
reporting and tracking as **clear, consistent, and structured** as possible.
Write templates that ask for the specific details your team needs (rather than
leaving it free-form). Use labels, milestones and projects to categorize and
visualize work. Encourage linking issues to code changes for automatic closure.
By following GitHub’s official guidance on issue templates and forms, your
website development tasks will be well-documented and easily manageable.
