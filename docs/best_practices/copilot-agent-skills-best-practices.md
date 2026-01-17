# Best Practices for Developing GitHub Copilot Agent Skills

## Introduction

GitHub Copilot **Agent Skills** are a way to teach Copilot new capabilities by
packaging instructions and code for specific tasks. An Agent Skill is
essentially a folder (in your repo or user directory) containing a special
`SKILL.md` file plus any helper scripts or resources. Copilot will
**automatically load the skill when it detects a relevant prompt**, and follow
the provided guidance【7†L31-L39】【3†L394-L403】. This works across Copilot’s
various interfaces – the VS Code extension (Chat/Agent mode), the Copilot CLI,
and even automated **coding agents** – thanks to a common open
standard【7†L33-L39】【3†L394-L403】. In short, skills let you “write it once” and
reuse knowledge everywhere, instead of retyping the same instructions in every
prompt【30†L72-L80】.

## Setting Up an Agent Skill (Official Guidelines)

To create a skill, follow the official folder and file conventions:

- **Skill Location:** Add a `skills/` directory either in your repository (for
  project-specific skills) or in your user profile (for personal, reusable
  skills). For example, a repo skill lives under
  `.github/skills/your-skill-name/`, whereas a personal skill can go in
  `~/.copilot/skills/your-skill-name/`【1†L408-L416】【3†L452-L460】. (Support for
  organization-wide skills is planned, but not yet available【1†L410-L418】.)

- **`SKILL.md` File:** In the skill folder, create a file named exactly
  `SKILL.md`. This Markdown file begins with a **YAML frontmatter** section,
  followed by the skill’s instructions. The frontmatter must include at least: a
  `name` (unique, lowercase with hyphens) and a `description` (what the skill
  does **and** when Copilot should use it)【32†L445-L453】. You can also specify a
  `license` if you plan to share the skill publicly【32†L445-L453】. For example:

  ```yaml
  ---
  name: webapp-testing
  description: Guide for testing web applications using Playwright. Use this when asked to create or run browser-based tests.
  license: MIT
  ---
  ```

  The Markdown body of `SKILL.md` will contain the actual **instructions,
  examples, and guidelines** that Copilot should follow for this
  skill【32†L445-L453】.

- **Additional Resources:** You may include supporting files in the same skill
  directory – e.g. scripts, data, templates, reference docs. Copilot will treat
  these as part of the skill package【32†L452-L458】. For instance, a skill for
  image conversion might include a Python script to convert SVG to
  PNG【32†L452-L458】. The skill’s instructions can then reference these files
  (more on that below).

Once the skill is in place, Copilot will recognize it. In VS Code Insiders,
ensure the `chat.useAgentSkills` setting is enabled to activate
skills【3†L413-L418】. When a user prompt matches your skill’s **description**,
Copilot’s agent will inject the `SKILL.md` content into its context, making
those instructions active【32†L509-L517】. Any scripts or example files in the
folder can be accessed by Copilot as needed. This on-demand loading means you
can add plenty of guidance without polluting every prompt – Copilot only loads
the skill when it’s relevant【5†L615-L624】【5†L627-L635】.

## Best Practices for Skill Content and Structure

Designing the contents of `SKILL.md` effectively is crucial. Here are best
practices to ensure your skill is clear, efficient, and effective:

- **Keep it Focused and Concise:** *Less is more* when it comes to prompt
  instructions. Only include information that the AI truly needs for the task at
  hand. Remember, the skill content competes for space in the model’s context
  window along with the chat history and other active
  skills【23†L243-L252】【23†L273-L281】. Avoid lengthy theoretical explanations or
  generic background – assume Copilot (backed by a large model) already knows
  common programming knowledge. For example, you don’t need to explain what a
  PDF is or how to install a library in excessive detail; just tell it to use a
  specific tool or approach【23†L273-L281】【23†L279-L283】. Every sentence in your
  skill should justify its token cost. Aim for a succinct how-to, not an essay.
- **Write a Specific, Triggering Description:** In the YAML frontmatter, the
  `description` field guides Copilot on when to apply the skill. Make it
  **specific** and include keywords or phrases a user might use when they need
  this skill【26†L1455-L1463】【26†L1505-L1513】. Mention both *what* the skill does
  and *when/where* to use it. For example: “Cleans up HTML text by fixing
  quotes, dashes, and spaces – use this when asked to format or clean an
  article.” Such a description contains actionable terms (clean, format HTML
  text) that will match user queries. A well-written description helps Copilot
  **pick the right skill at the right time**【26†L1505-L1513】. It also reduces
  overlap (and confusion) between skills.
- **Avoid Overlap Between Skills:** Each skill should have a clear, distinct
  purpose. If you create multiple skills, ensure their descriptions don’t
  unintentionally cover the same triggers or domain. Overlapping skills can
  confuse the agent (it may load the wrong one or even try to use both). For
  instance, having two skills both claim “use for debugging errors” is not a
  good idea if one is specifically about debugging **GitHub Actions** failures
  and another about debugging general code. Merge skills or refine their scopes
  to eliminate ambiguity. A community user noted that having “many overlapping
  skills... tends to confuse Claude and make it not consistently use the
  skills”【28†L727-L735】, and the same principle applies to Copilot. In short:
  one skill, one specialty.
- **Use Progressive Disclosure for Large Topics:** If your skill covers a broad
  or complex domain, don’t cram everything into the `SKILL.md` body. The Agent
  Skills format lets you include additional Markdown files (or other resources)
  in subfolders and only load them when needed. **Keep `SKILL.md` relatively
  short** (the Claude team suggests under 500 lines as a
  guideline【26†L1490-L1498】【26†L1507-L1515】) focusing on the most important
  instructions or a high-level workflow. For detailed reference material,
  include it as separate files (e.g. a `reference/` subdirectory with multiple
  `.md` files, each on a subtopic). In your `SKILL.md`, you can provide an
  outline or Table of Contents and links to those files. Copilot will pull in a
  reference file only if the conversation reaches a point where that detailed
  info is required【5†L621-L629】【25†L1398-L1406】. This “just-in-time” approach
  keeps the context lightweight. It also makes maintenance easier – you can
  update a reference file independently when things change.
- **Step-by-Step Instructions:** Agents excel when given clear, procedural
  guidance. If the task can be broken into steps, do it! Numbered lists or
  bullet points for each major step in a workflow are highly
  recommended【2†L475-L483】【11†L178-L186】. For example, a testing skill might
  say: “1. Build the project. 2. Start the test server. 3. Run the test suite.
  4\. Report any failures.” This provides a structured game plan for the AI. In
  practice, Copilot will often internally reason through these steps and even
  show the outcome, such as presenting diffs or results after executing the
  steps【11†L197-L204】. The example from Visual Studio Magazine’s walkthrough
  shows the benefit: the skill’s steps for cleaning an article (replace curly
  quotes, replace long dashes, etc.) led Copilot to perform all replacements and
  then present a **diff** of changes for the user to review【11†L197-L204】. When
  writing steps, use imperative verbs and be specific (“Replace X with Y”,
  “Fetch data from Z”, “If condition A, do B”). This reduces ambiguity and
  ensures reproducibility.
- **Include Concrete Examples:** Where appropriate, pepper your skill
  instructions with examples – small code snippets, command examples, or format
  samples. Examples act as **calibration data** for the AI, showing it the style
  of solution you expect. For instance, if you have a skill to enforce API call
  patterns, you might include a snippet of a correctly formatted API call. Or if
  your skill is a “code reviewer,” include an example of a good review comment.
  Make sure examples are **realistic and relevant** (don’t show a trivial
  hello-world if the skill is about complex refactoring). The documentation
  advises that examples should be *concrete, not abstract*【26†L1507-L1515】 –
  e.g. show actual function names or data that the AI might encounter, so it can
  pattern-match effectively. Also, clearly delineate example content (use
  Markdown fences for code) and perhaps label it in a comment, so the AI knows
  how to use it.
- **Use Consistent Terminology and Tone:** Treat your skill content like you
  would documentation – consistency is key. Use the same terms for the same
  concept throughout the skill. If your skill alternates between calling
  something “module” vs “package” or “bug” vs “issue”, you might confuse the
  model. Consistent terminology helps the AI map your instructions to the user’s
  request reliably【26†L1509-L1513】. Additionally, maintain a steady tone: if
  your skill is giving step-by-step commands, keep them all in either imperative
  form or a consistent narrative style. This consistency makes it easier for the
  agent to follow the instructions without slipping into confusion or blending
  styles.
- **Avoid Time-Sensitive or Volatile Info:** Don’t include information that will
  go out-of-date quickly (or if you must, isolate it in a clearly marked
  section). For example, writing “*Use library XYZ version 1.2 (released last
  week)*” is risky – in a few months, that may be obsolete. Skills might live in
  codebases or personal folders for a long time. If you need to refer to
  version-specific or date-specific guidance, consider noting the date and
  marking it as potentially stale (or put such guidance in an “Appendix”
  section). In general, focus on timeless process over transient details. The
  Anthropic best-practice guide explicitly says to avoid time-sensitive
  information unless you handle it carefully【24†L133-L141】. In the context of
  Copilot, this ensures your skill stays useful over time and doesn’t mislead
  the model as things change.

## Best Practices for Including Scripts and Code

One powerful feature of Agent Skills is the ability to include **executable
code** (scripts) or other files that the AI can leverage. This can dramatically
improve reliability and efficiency. Here’s how to make the most of scripts in
your skills, especially using Python or JavaScript/TypeScript, while keeping
things safe:

- **Leverage Utility Scripts for Complex Logic:** Even though Copilot *could*
  write code on the fly, it’s often better to provide a ready-made script. Many
  community-contributed skills bundle Python or Node.js scripts to handle heavy
  lifting, as these runtimes are commonly available on developers’
  machines【13†L1-L4】. Pre-writing a script has several benefits: it ensures
  correct, tested behavior (no risk of the AI writing buggy code), it saves
  tokens/context (the AI doesn’t need to “imagine” the implementation – it just
  runs it), and it can be re-used across multiple invocations【25†L1255-L1263】.
  In short, if your skill requires parsing a file, querying an API, crunching
  data, or any deterministic operation – consider shipping that as a script in
  the skill. For example, if you have a skill to analyze PDFs, include a
  `parse_pdf.py` that does the parsing. Your instructions can then say “Run the
  `parse_pdf.py` script to extract text from the PDF” instead of expecting the
  model to do it from scratch. This yields more reliable
  outcomes【25†L1255-L1263】.
- **Explicitly State When to Execute vs. Reference Code:** When you include
  scripts, clarify how Copilot should use them. In some cases, you want the AI
  to **run** the script and use its output. In other cases, you might include a
  file just as reference (for example, a library of helper functions that the AI
  might draw from or a template it should follow). Make this distinction clear
  in your `SKILL.md` text【25†L1270-L1278】. Phrasing like “**Run**
  `analyze_form.py` to extract the fields” tells Copilot to execute the script,
  whereas “**See** `analyze_form.py` for the algorithm” implies it should
  open/read the file for information. Most of the time, **execution is
  preferred** because it’s more efficient and less error-prone (the AI doesn’t
  have to reinterpret the code)【25†L1271-L1278】. So, use imperative language for
  running scripts. If you do provide reference code (say, a large example or
  documentation in a file), use careful wording so the agent knows it shouldn’t
  just regurgitate it blindly – maybe instruct it to summarize or apply the
  concept rather than dumping the file contents.
- **Cross-Platform Script Design:** Keep in mind that Copilot’s agent might run
  in different environments (developers on Windows, macOS, Linux, etc., or in CI
  containers for coding agents). To maximize compatibility, write scripts in
  cross-platform languages (Python is a great choice, as is Node.js for
  JavaScript/TypeScript) and avoid OS-specific shell commands if possible. For
  instance, instead of a Bash `.sh` script that uses `grep` or `sed` (which
  might not work on Windows without a POSIX shell), you could use a Python
  script to achieve the same ends. If you do use shell commands, stick to ones
  that exist in PowerShell or document that a Unix-like environment is needed. A
  simple but important convention: **use forward slashes in paths** and relative
  paths for your files【25†L1398-L1406】. For example, prefer
  `./scripts/my-tool.js` over backslashed Windows-style paths【26†L1523-L1528】 –
  the latter might not be understood by the agent or could fail on non-Windows
  systems. Also, if using Node/TypeScript, remember that the skill will likely
  execute via Node.js. That means if you include a `.ts` file, you either need
  to ensure `ts-node` is available or provide a precompiled `.js`. A safer route
  is often to include the transpiled JavaScript (or use plain JS) unless you
  know the user’s environment has a TypeScript runner. In summary, aim for
  **maximum portability** in any code you include.
- **Declare Dependencies and Setup:** If your skill’s script relies on external
  libraries or tools, let the user (and Copilot) know! In your instructions,
  include installation steps or checks for dependencies. For example: “This
  skill requires the **Playwright** test framework. Ensure it’s installed
  (`npm install playwright`) before running tests.” or “Uses the Python
  **pypdf** library – run `pip install pypdf` if not already installed.” Being
  explicit prevents frustration and wasted cycles. The Claude documentation
  specifically advises against assuming a package is available without telling
  the agent/user to install it【26†L1455-L1463】. Copilot CLI’s execution
  environment can potentially install PyPI or npm packages (with user
  permission)【25†L1366-L1374】, but only if instructed. So list out any
  `pip`/`npm` commands needed, ideally at the top of your skill or right before
  the first use of that tool. This way, Copilot will attempt to satisfy
  dependencies rather than failing.
- **Error Handling and Robustness in Scripts:** Write the scripts as if they’ll
  be run by a somewhat naive user (because effectively, an AI is running them on
  behalf of a user). That means including **helpful error messages and usage
  info** in your code. For instance, if a script expects a file path input,
  check for it and print “Usage: xyz <input-file>” if not provided, instead of
  just throwing a stack trace. If an error is likely (network call fails, file
  not found, etc.), catch it and output a clear message. Why? Because whatever
  your script prints will become part of the AI’s context/output. Clear errors
  help the AI (and user) diagnose what went wrong and possibly recover. In the
  checklist for good skills, it’s noted that error handling in scripts should be
  explicit and informative (no silent failures)【26†L1521-L1528】. Also avoid
  “voodoo constants” or unexplained behaviors in code – if your script has a
  timeout of 47 seconds for no obvious reason, either remove it or document it,
  since the AI might otherwise be puzzled by such
  choices【25†L1246-L1254】【26†L1521-L1528】. Write scripts in a clean,
  straightforward style with comments for any non-obvious logic. This not only
  aids maintainers, it also means if Copilot ever has to read the script
  (instead of running it) to answer a question, it can more easily interpret
  what’s going on.
- **Secure Script Execution:** Always remember that when your skill triggers a
  script, that code is running on the user’s machine (or CI environment). Be
  extremely cautious with any operation that can modify user data or
  environment. As a best practice, **avoid destructive actions** (deleting
  files, modifying system settings, etc.) in auto-run scripts. If your skill
  must perform something potentially dangerous (say clean up build artifacts),
  consider adding a confirmation step in the instructions or leveraging
  Copilot’s built-in safety. GitHub has implemented controls in VS Code’s
  *terminal tool* where certain commands require user approval or pre-approval
  via allow-lists【5†L648-L657】. For example, the user can configure Copilot to
  auto-allow running certain scripts or commands. Design your skills to work
  with these safety nets: use predictable command names and locations (so they
  can be allow-listed easily), and don’t try to obfuscate what you’re running.
  It’s wise to mention in your skill’s README or comments if something will run
  automatically and might need permission. As an analogy, treat skills like VS
  Code extensions or GitHub Actions – be transparent about their behavior so
  users can trust them.
- **Organize and Reference Scripts Cleanly:** Place any scripts or files within
  your skill directory, and refer to them with **relative paths** in your
  instructions. For instance, if you have a `test-template.js` file as part of
  your skill, you can reference it in `SKILL.md` like:
  `[test script](./test-template.js)`【4†L73-L80】. This signals to Copilot where
  to find the file. Using `./` relative links is important; it tells the agent
  to look in the current skill folder. Also, use descriptive file and folder
  names to keep things tidy. Instead of naming something `script1.py`, call it
  `update_database_schema.py` (for example) – this is easier for developers to
  understand and for the AI to recall. The agent skills architecture treats your
  skill folder like a mini filesystem it can navigate【25†L1398-L1406】, so
  logical structure helps. A good pattern is to group by function: e.g. a
  `scripts/` subfolder for .py/.js scripts, a `reference/` subfolder for extra
  docs or data, etc. Remember that large files don’t count against context
  limits until read, so you can include things like an extensive README or even
  a changelog if it helps your skill – just keep them separate from the main
  instructions to avoid bloat【25†L1399-L1407】【25†L1408-L1416】. In summary,
  package your skill like a mini project, with a clear layout. Copilot will find
  the pieces when it needs them.

## User Experience and Workflow Considerations

A well-crafted skill not only makes Copilot *smarter* – it should also make life
easier for the user. Consider the UX implications of how your skill operates:

- **Seamless, Contextual Activation:** The ideal skill kicks in when the user
  naturally asks for that kind of help, without requiring special incantations.
  To achieve this, use wording in your skill’s description and instructions that
  matches how users speak. The earlier example “straighten-quotes” skill was
  activated by the user typing “clean this article” in chat【11†L195-L203】. This
  worked because the skill’s description and prompt text mentioned phrases like
  “fixing quotes” and “when I ask you to ‘clean this article’”【11†L170-L179】.
  Anticipating user phrasing is part art, part science – you might gather common
  words from how people describe the task. For a testing skill, maybe words like
  “run tests” or “browser test” are triggers. For a database migration skill,
  “migrate schema” or “update DB”. Including these key terms increases the
  chance Copilot will recognize the relevance【26†L1505-L1513】. Also, ensure the
  description isn’t so narrow that a reasonable request misses it. If your
  description says “Use this when asked to tidy HTML typography” and the user
  says “clean up this HTML file format,” Copilot should still make the
  connection (thanks to “clean” and “HTML”). In short, align skill triggers with
  user vocabulary.
- **Keep the AI’s Output User-Friendly:** When Copilot uses a skill, the end
  goal is to assist the user, not just parrot the skill text. Write your
  instructions in a way that the *results* will be helpful and neatly presented.
  For instance, if the skill is supposed to fix code style issues, the agent’s
  output might be a diff or a list of changes. Ensure the instructions guide it
  to present that in a digestible way (the VS Code agent does a good job of
  showing diffs by default【11†L197-L204】). If your skill involves multiple steps
  or lengthy output, consider having the agent summarize intermediate steps to
  avoid flooding the user. Always think: “If I were the user, what would I want
  to see?” A concise answer, a patch, a table of results, etc., rather than
  pages of raw logs or entire file dumps. You can instruct Copilot in the skill
  to e.g. “summarize the findings in a table” or “present the modifications as a
  unified diff” – it will try to follow that format. By shaping the output
  format in your skill, you improve UX.
- **Safeguard Potentially Destructive Actions:** If a skill can perform write or
  delete operations (code modifications, file operations, etc.), it’s best
  practice to *not* have the AI do it blindly without user review. Copilot’s
  agent in VS Code typically will show a preview (like a diff or a suggested
  code change) and wait for the user to accept it【11†L197-L204】. This is great
  for safety. Make sure your skill’s instructions align with that flow: e.g.,
  “propose the changes and await confirmation” rather than “automatically apply
  the changes”. In CLI scenarios, where a diff UI might not exist, the skill
  could instruct the agent to output the changed file content or list of
  changes, and maybe suggest a follow-up command to apply them (with user
  consent). Always err on the side of **user control**. The user should be able
  to see what Copilot is going to do and approve it, especially for anything
  beyond read-only operations. Skills should act as a copilot, not an
  auto-pilot.
- **Utilize Copilot’s Toolset for Better Results:** Copilot’s agents come with
  integration points (the so-called *MCP servers* and tools) that can enhance
  what a skill can do. For example, GitHub’s own skills can use a **GitHub
  Actions tool** to list workflow runs or fetch logs【32†L475-L484】. If you’re
  writing a skill that interacts with an ecosystem (GitHub, a cloud provider,
  etc.), see if there are built-in tools you can invoke via instructions, rather
  than relying purely on the AI’s language reasoning. In your skill steps, you
  might say “Use the `GitHub:list_issues` tool to retrieve open issues” or “Run
  the database client CLI to export schema”. By doing so, you offload work to
  reliable external tools and simply have the AI orchestrate them. The result is
  typically more accurate and less context-heavy (for instance, calling an API
  to get data is better than having the AI guess what the data might be). The
  key is to reference tools by their proper names so the agent finds them.
  Anthropic’s guide notes to always fully qualify tool names (e.g.,
  `GitHub:create_issue` rather than just `create_issue`) to avoid ambiguity when
  multiple tool sources exist【26†L1433-L1442】【26†L1445-L1453】. While end-users
  of your skill don’t need to know this detail, as a skill author it’s a good
  practice if you’re leveraging any agent tools.
- **Minimize Interruption and Clarify Queries:** Skills should streamline
  workflows, not create extra hassle. Try to design your skill such that once
  invoked, it provides value immediately. If possible, avoid requiring a lot of
  follow-up questions to the user. Sometimes a skill may need more info (e.g., a
  code generation skill might ask which module to place code in). When that
  happens, the agent will naturally ask the user. That’s fine, but try to limit
  it to what’s necessary. One trick is to have reasonable defaults: for example,
  the skill could assume a default file name or configuration if the user
  doesn’t specify, and proceed, mentioning what default was used. This way, the
  user isn’t blocked by endless queries. Also, if your skill has multiple modes
  or options, you might consider breaking them into separate skills or at least
  separate commands, so the user can directly invoke what they want (for
  instance, a “database backup” skill vs a “database restore” skill, rather than
  one skill that asks “backup or restore?” every time). The smoother the
  interaction, the more likely users will appreciate and continue using the
  skill.
- **Test the User Flow in Different Environments:** Don’t assume the experience
  is identical in VS Code vs the CLI. Try out your skill in VS Code’s
  chat/coding assistant – see how it presents results. Then, try using it
  through Copilot CLI if you have access. The CLI might involve typing something
  like `copilot run "describe this image"` (if that triggers a skill) and then
  reading the terminal output. You want to ensure the output is formatted in a
  readable way for a text terminal (maybe avoid super long lines or color codes
  that only work in certain shells, etc.). If your skill outputs markdown (like
  a table or code block), in VS Code that will render nicely in the chat panel;
  in a raw terminal, it will just print the markdown text. That’s okay, just be
  aware and see if it’s still legible. By testing, you might discover, for
  example, that a progress indicator your skill prints (like a spinning bar)
  doesn’t show well, or that you need an extra newline for clarity. These little
  UX tweaks can make a big difference in how professional and helpful the skill
  feels. In sum, **dogfood your skill** as a user would, in multiple contexts.

## Security Considerations

Agent Skills blur the line between AI prompts and code execution – making them
powerful but also raising security questions. Whether you’re creating your own
skills or using community ones, keep these practices in mind:

- **Review and Vet Skills Before Use:** Treat a skill like you would any code
  dependency. If it’s a third-party/community skill, read through the `SKILL.md`
  and any scripts to ensure there’s nothing malicious or unsafe. The official
  docs and community guides strongly encourage reviewing shared skills for
  security and suitability【5†L648-L657】【20†L483-L492】. Copilot will execute
  scripts and commands from skills with your privileges, so a malicious skill
  could potentially do harm. Don’t blindly install a skill just because it’s on
  an “awesome” list – give it a quick audit. Conversely, if you’re authoring a
  skill intended for others, assume they will (or at least *should*) read
  through it. Be transparent and write clear, simple code/instructions that pass
  a security sniff test. A GitHub disclaimer notes that community agents
  (skills, etc.) aren’t vetted by GitHub, so it’s on users to check what a skill
  might do【20†L483-L492】. As a skill developer, make that job easy by avoiding
  any suspicious patterns in your code.
- **Apply Principle of Least Privilege:** Only request or perform the actions
  that are necessary for the task. For example, if your skill needs to read some
  files in the repository, have it do so for specific paths or via provided
  tools – don’t instruct it to do a blanket search of the entire filesystem. If
  a skill is meant to clean up build artifacts, limit it to the project
  directory, not `/tmp` or other locations. By keeping the skill’s scope tight,
  you reduce the chance of collateral damage or abuse. Also, design scripts to
  default to safe behaviors (e.g., a script could refuse to run if an output
  file already exists, to avoid overwriting something unintentionally, unless a
  `--force` flag is provided). These are the same kind of practices as writing
  any automation tool, just applied in the context of AI-driven usage.
- **User Confirmation and Auto-Approval Settings:** As mentioned, Copilot
  provides some control for running commands. Users can pre-approve certain
  commands or get prompted each time. As a skill author, you should not rely on
  auto-approval being on; assume the user will be prompted for dangerous
  actions. It’s good to design the skill such that most actions are either
  read-only or clearly safe. For those that do require running a command (say,
  deploying to a cloud, deleting a branch, etc.), consider adding a note in the
  skill instructions like “(This action will require confirmation before
  executing)”. This at least signals to the user what to expect. If you know
  your target audience might enable auto-approve for convenience, **strongly
  suggest** in your documentation that they only do so for non-destructive
  commands and provide an allow-list example. For instance, you might suggest
  they allow only your specific script or a certain CLI invocation. On the VS
  Code side, the terminal tool’s security docs discuss how users can configure
  allow-lists and other safeguards【5†L648-L657】 – be aware of these and maybe
  even refer to them in your skill’s README. The goal is to never surprise the
  user with a destructive outcome.
- **Never Include Secrets or Sensitive Info:** This should go without saying,
  but do not hard-code API keys, passwords, or proprietary sensitive logic in a
  shared skill. If your skill needs to use an API, use environment variables or
  instruct the user to configure a secret outside of the skill. Remember, your
  repository might be public (if you open source the skill) or at least visible
  to others in your org. From a privacy standpoint, also avoid embedding large
  chunks of proprietary content (like dumping your company’s internal
  documentation verbatim). Instead, summarize or reference a link if possible.
  The skill’s purpose is to equip the AI to help with tasks, not to serve as a
  data vault. Moreover, if a skill becomes very large because it’s storing lots
  of info, that’s against the earlier advice of keeping things concise and
  on-demand.
- **Maintain Licensing and Attribution:** If you reuse content (code snippets,
  text) from elsewhere in your skill, respect licenses. It’s a good practice to
  fill in the `license` field in frontmatter if you intend to share the
  skill【32†L445-L453】 – e.g., use MIT or Apache-2.0 for open source skills you
  create. Also, if your skill draws on a published guide or blog, consider
  crediting that in a comment or the skill’s markdown (without affecting the AI
  instructions too much). This not only is ethically right, but it also helps
  users trust that the skill is grounded in known references. GitHub’s community
  repo for Copilot customizations lists license info and encourages contributors
  to follow contributor guidelines【20†L440-L448】【20†L472-L475】. As a best
  practice, keep your skill content original or from permissively licensed
  sources to avoid any legal issues down the line – skills could eventually be
  widely shared, and you don’t want yours to raise red flags.

## Architectural and Compatibility Considerations

Thinking about the “big picture” of how skills fit into your development
workflow and toolchain will help ensure they remain effective and maintainable:

- **Modular, Composable Skills:** Agent Skills are meant to be building blocks.
  Rather than one giant skill that tries to cover a huge domain (and ends up
  slow or rarely fully relevant), prefer multiple focused skills. For example,
  if you have a suite of AI helpers for testing, you might have one skill for
  frontend/UI tests, another for API contract tests, etc., each with its own
  triggers. Copilot can load multiple skills at once if a query is relevant to
  several【3†L405-L413】【3†L431-L438】. This composition ability means you can
  tackle complex workflows by breaking them down. It also means you can reuse
  generic skills across projects and combine them with project-specific ones.
  Design skills that *could* work together: for instance, a “generate unit
  tests” skill might pair well with a “run tests and report failures” skill. If
  a user says “Generate unit tests and make sure they all pass,” the agent might
  actually invoke both. By keeping skills modular, you simplify each one’s logic
  and make it easier to troubleshoot when something goes wrong. If you notice
  two skills often get used together, you can document that synergy or even
  combine them if it makes sense – but only do so if they’re truly related.
  Generally, a skill should have a single responsibility or theme, much like a
  good function or module in code.
- **Ensuring Cross-Tool Compatibility:** As mentioned, the same skill file
  should work in VS Code, Copilot CLI, and the Copilot coding agent (which might
  be running in a cloud context or GitHub’s web UI). The underlying AI logic is
  consistent, but capabilities might differ slightly. VS Code provides a rich
  interface (panels, diff views, etc.), whereas CLI is pure text, and the coding
  agent (for example, an agent assigned to a PR) might operate
  non-interactively. To ensure your skill shines everywhere, follow the standard
  format strictly (so all agents recognize it) and avoid any instructions that
  assume a GUI. For instance, don’t instruct “click the above link” or “open the
  problems pane” – the CLI won’t have those. Instead, if needed, instruct in
  abstract terms like “open the file `errors.log`” which in VS Code will likely
  open the file, and in CLI it might just print a suggestion to open it
  manually. Also, consider that the **coding agent** (in GitHub or other
  automation) could use skills to autonomously handle tasks like merging a PR or
  writing a commit message. In those cases, there’s no human to confirm each
  step. Thus, skills used in automation should be extra careful: they should
  validate their results (maybe using the feedback loop patterns) and err on the
  side of caution. For example, a skill for an automated code cleanup might
  include a step “If more than 10 files will be changed, stop and ask for
  confirmation” – but in an automated scenario, there is no user to ask. A
  better approach might be for the skill to limit scope (clean up one module at
  a time) or produce a report for a human to review. Keep in mind the
  **context** in which your skill might run. Test if possible: assign Copilot to
  an issue or have it run a skill-driven action in a safe environment to see how
  it behaves when fully automated. This can reveal any assumptions in your
  instructions that don’t hold in headless mode.
- **Version Control and Collaboration:** Because skills are just files in a repo
  (or your home directory), they can and should be put under version control. If
  you’re using a skill in a team project, commit the `.github/skills/` folder to
  your repository. This way, everyone gets the benefit of it (assuming they have
  Copilot enabled) and you can track changes to the skill over time. Treat
  changes to a skill with similar rigor as code changes: if you update the
  skill’s logic, mention it in your commit (changelog for skills). If your
  project has multiple skills, you might even designate an “AI maintainer” to
  oversee them (especially in a large codebase). GitHub suggests enabling “AI
  managers” in enterprise contexts【1†L419-L427】 – roles responsible for curating
  AI configs, which would include skills. From a maintenance perspective,
  periodically **re-evaluate skills** as your codebase evolves. A skill might
  become less relevant or need tuning if you adopt new frameworks or
  conventions. It’s a good idea to write down somewhere (maybe in the repository
  README or a `SKILLS.md` index) what skills exist and what they cover, so new
  team members know about them. This avoids duplication and encourages proper
  use.
- **Testing and Iterating on Skills:** You wouldn’t deploy code without testing;
  similarly, test your skills. There are a few levels to this: (1) **Unit test**
  the scripts if you have any (run those scripts with sample inputs to ensure
  they work as intended). (2) **Manual test** the skill by simulating relevant
  user prompts and seeing if Copilot does the right thing. (3) If possible, test
  across different AI models that might be used. Copilot’s backend can include
  models from OpenAI (like GPT-4 or GPT-3.5 Codex) or others, and their behavior
  can differ. Anthropic’s guide suggests testing skills with their Haiku,
  Sonnet, Opus models for Claude【26†L1533-L1541】; for Copilot, you might try
  with the default vs GPT-4 if you have Pro+, or even test with Claude if that’s
  an option in Copilot. This ensures your skill isn’t overfitted to one model’s
  quirks. Also, create a few **scenario tests**: e.g., if your skill is “pull
  request assistant,” simulate a PR description and ask Copilot (in a chat or
  CLI) “help me with this PR” and see if it uses the skill correctly. Refine
  based on failures: if it didn’t trigger, maybe the description needs a
  keyword. If the output was wrong, maybe the instructions need tweaking. Using
  the AI itself to improve the skill is a neat trick – you can ask
  Copilot/Claude in a chat to analyze the skill draft and suggest improvements
  (Anthropic even has a “Skill Builder” skill to audit skills【28†L681-L690】).
  Employ these meta-techniques to iterate quickly.
- **Plan for Evolution:** The field of AI coding assistance is moving fast.
  Skills are a new feature (as of late 2025), so expect improvements and
  changes. Keep an eye on updates – for example, the maximum context lengths
  might increase (making larger skills feasible), new tool integrations may
  appear (e.g., maybe Copilot will add a Slack tool or a JIRA tool, etc.), or
  the syntax of skills might expand (future YAML fields or support for org-level
  skills). Design your skills in a way that they’re easy to update. For
  instance, if a better method to accomplish a step comes along, you can swap
  out that step’s instructions or point to a new script version. If you
  anticipate changes, comment your `SKILL.md` (comments in Markdown won’t affect
  the AI) to note “TODO: update when X is available”. Also consider backwards
  compatibility if you share the skill – e.g., if using a new feature, document
  the minimum Copilot version or model needed. By treating skills as living
  artifacts and revisiting them periodically, you’ll keep them effective. A
  stale skill can be worse than none, if it leads the AI astray with outdated
  advice. So, apply good software maintenance practices here as well.

In summary, architect your skills like modular plugins for Copilot. Make them
small, purposeful, and easy to mix and match. Ensure they behave well whether in
a rich IDE or a headless terminal. And keep them under the same life-cycle
management as your code – tested, reviewed, and updated as needed.

## Conclusion

Agent Skills enable you to extend GitHub Copilot’s abilities in truly powerful
ways, but success requires careful crafting. By following the best practices
outlined above – **structuring clear and minimal prompts** that target your
use-case【23†L243-L252】【23†L279-L283】, **augmenting Copilot with reliable
scripts** instead of forcing the AI to reinvent the wheel【25†L1255-L1263】, and
always keeping an eye on **safety, user experience, and maintainability** – you
can develop skills that are both effective and trustworthy. Remember that a
great skill is one that feels natural: it triggers when needed, does its job
accurately, and integrates smoothly into the user’s workflow, whether that’s in
VS Code, a CLI session, or an automated pipeline. Copilot’s adoption of the
Agent Skills open standard means your well-built skills aren’t just one-off
hacks – they become portable AI knowledge that can benefit many contexts and
even other AI platforms. As you iterate, leverage community insights and
documentation (both GitHub’s and Anthropic’s) to refine your approach, and don’t
hesitate to have the AI itself critique your skill during development. With
iterative testing and refinement【26†L1533-L1541】【26†L1520-L1528】, you’ll end up
with a set of robust agent skills that significantly improve productivity and
consistency in your coding tasks. In effect, you’re writing the “playbook” for
your AI pair programmer – and a good playbook, once written, can be reused again
and again to great effect. Happy skill building!

**Sources:** The above recommendations are drawn from official GitHub and VS
Code documentation on Agent Skills【32†L445-L453】【5†L615-L624】, insights from the
open Agent Skills standard by Anthropic【25†L1253-L1262】【26†L1521-L1528】, and
community experiences shared via blog posts and
forums【11†L197-L204】【28†L727-L735】. These sources provide in-depth examples and
rationales for the best practices summarized here.
