# Flow: `/playbook create` — Playbook authoring

Interview the user about an operation they want to automate, research the target product's constraints, and write a new `data/[name].md` Playbook file. Invoked from the main `playbook` SKILL.md via sub-command routing.

**Prerequisite**: `data/ui-map.md` must already exist (run `/playbook init` first if not). If a browser scan becomes necessary during Phase 2, `references/preflight.md` checks must pass before the first `agent-browser` call. Consult `references/agent-browser-cheatsheet.md` for command syntax.

## Phase 1: Intake
1. Ask: "What operation should this Playbook cover?"

## Phase 2: Research (done in parallel)

### (a) Read the UI Map + targeted re-crawl
- Read `data/ui-map.md` to understand the screen structure.
- Only if a required screen is missing from the UI Map, re-crawl the relevant screens inline via `agent-browser` to fill the gap. Do NOT dispatch another subagent — you are already running inside the subagent that was spawned for `/playbook create`.

### (b) Domain knowledge interview (the main work)
Use `AskUserQuestion` to drill into the business scenario. Grouping multiple choice-style questions works well:
- "Which screen do you start from?"
- "When you search, what do you type?" (not written in the UI)
- "After seeing the result, what do you do next?"
- "Which value tells you whether it succeeded or failed?" (not written in the UI)

### (c) Constraint and limitation research
Fetch the target product's **official documentation** via `WebFetch` / `WebSearch` and investigate:
- **What is possible**: partial-match search, filtering by specific fields, etc.
- **What is not possible**: numeric comparisons, regular expressions, range queries, etc.
- **Data retention**: automatic deletion rules, etc.

## Phase 3: Generate the Playbook file
Create `data/[name].md` using this format:

```markdown
# [Playbook name]

## Prerequisites
- [Login state, starting screen, and other preconditions]

## Pre-execution decision rules
- Official docs: [URL]
- If the request is infeasible, do NOT start operating — present an alternative instead.
- NEVER brute-force with full pagination scans.

## Constraints and limitations
- **What [feature] can do**: [specifics]
- **What [feature] cannot do**: [specifics, with the reason why]
- **Data retention**: [auto-deletion rules, etc.]
- **Workarounds**: [what to do when a constraint applies]

## Domain knowledge
- [Business knowledge that cannot be inferred from the UI alone]

## Procedure

### Step 1: [Operation overview]
- **Action**: [concrete operation]
- **Target element**: role=[role], name="[text label]"
- **Completion check**: [how to confirm success]
- **On failure**: [what to do on error]

## Output
[Report format after completion]
```

## Phase 4: Update the Playbook index & confirm
1. Add a row to the "Playbook index" table in `data/ui-map.md`.
2. Show the generated content to the user for confirmation.
3. Report: "You can now run it with `/playbook [operation]`."

## Authoring rules
- **Target element** MUST include a text label and a role. Color, position, and CSS selectors are forbidden.
- NEVER omit **Completion check**.
- **On failure** MUST contain at least "retry" or "report to user".
- For repeated operations, state the loop's start and end conditions explicitly.
- For branching logic, use `#### When [condition]` to make the branch explicit.

See also: the "Quality checklist" and "Anti-patterns" sections at the bottom of the main SKILL.md — any Playbook you generate here must satisfy them.
