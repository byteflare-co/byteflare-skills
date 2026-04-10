---
name: playbook
description: Integrated skill for managing and executing browser operation playbooks. Use "/playbook init [URL]" to generate a UI Map, "/playbook create" to author a new playbook, "/playbook list" to list registered playbooks, "/playbook resync [screen]" to rescan the UI, "/playbook [operation]" to run one, and "/playbook update" to update an existing one. Trigger on keywords like "playbook", "runbook", "browser operation", "UI map", or "screen map".
argument-hint: "init [URL] | create | list | resync [screen] | update | [operation-name]"
---

# Playbook

Integrated skill for managing and executing browser operation runbooks ("Playbooks").

Browser automation is driven by the [`agent-browser`](https://github.com/anthropics/agent-browser) CLI invoked via the `Bash` tool. This skill is a dispatcher: it routes sub-commands to flow files under `references/flows/`. `init` runs **inline in the main session** so the user can watch the browser scan and log output live; the other browser flows (`create`, `resync`, `execute`) are dispatched to a Sonnet subagent via the `Agent` tool. User-generated Playbook data (UI Map + individual Playbooks) lives under `data/`.

## File layout

```
<skill-root>/            ← directory containing this SKILL.md
  SKILL.md               ← this dispatcher
  references/
    preflight.md         ← environment checks before browser calls
    agent-browser-cheatsheet.md  ← CLI command reference
    flows/
      init.md            ← UI Map generation flow
      create.md          ← Playbook authoring flow
      list.md            ← Playbook listing flow
      resync.md          ← UI Map rescan flow
      update.md          ← manual edit flow
      execute.md         ← Playbook execution flow
  data/                  ← user-generated (created by /playbook init)
    ui-map.md            ← UI Map + Playbook index
    [name].md            ← individual Playbooks
```

All paths in this document and in the flow files are **relative to the skill root**. When constructing dispatch prompts for subagents, resolve them to absolute project paths. For example, if this skill is installed at `.claude/skills/playbook/`, then `data/ui-map.md` becomes `.claude/skills/playbook/data/ui-map.md`.

## User-facing language rule

Every `AskUserQuestion` call and freeform user prompt — question body AND every `options` entry — MUST be rendered in the user's active Claude Code session language. The English strings in `references/flows/*.md` are semantic templates only; translate them before calling the tool. Subagent dispatchers must forward this rule (see Subagent flows → item 7).

## Sub-command routing

Branch on the content of `$ARGUMENTS`:

| Input | Flow file | Runtime |
|-------|-----------|---------|
| `init [URL]` | `references/flows/init.md` | **Inline** (browser via `Bash` + `agent-browser`) |
| `create` | `references/flows/create.md` | Sonnet subagent (browser + user interview) |
| `list` | `references/flows/list.md` | **Inline** (file read only) |
| `resync [screen]` | `references/flows/resync.md` | Sonnet subagent (browser) |
| `update` | `references/flows/update.md` | **Inline** (file edit only) |
| anything else / empty | `references/flows/execute.md` | Sonnet subagent (browser) |

**Difference between `resync` and `update`**:
- `resync` rescans the actual UI, auto-detects diffs, and updates `data/ui-map.md`.
- `update` manually edits existing Playbooks or `ui-map.md` to add domain knowledge that cannot be obtained by a browser scan.

**Existence check**: for every sub-command except `init`, first verify that `data/ui-map.md` exists (resolve to absolute path). If it is missing, reply "Please run `/playbook init [URL]` first to create the UI Map." and stop.

## Dispatch contract

### Inline flows (`init`, `list`, `update`)

These flows run **directly in the main session** so the user can watch every tool call and log line as it happens. `list` and `update` only read or edit markdown files under `data/`; `init` additionally drives `agent-browser` via the `Bash` tool to scan the target URLs and generate `data/ui-map.md`.

General steps:

1. Read the flow body from `references/flows/<name>.md` and follow its steps in order.
2. Use `Read` / `Edit` / `Write` / `AskUserQuestion` as needed.

Extra steps for `init` (because it drives the browser):

3. **Preflight (mandatory before the first `agent-browser` call).** Read `references/preflight.md` and run all checks via `Bash`. If any check fails, STOP and print the user-facing block verbatim — do not try to self-heal.
4. **Cheatsheet.** Consult `references/agent-browser-cheatsheet.md` when translating step intents into concrete `agent-browser ...` shell commands.
5. **Report.** At the end, print any reporting templates specified in `references/flows/init.md`.

**Why `init` runs inline and not via a subagent**: historical subagent runs were opaque — the user could not see what the browser was doing, and dispatch prompt debugging was painful. Running inline keeps the tool-call stream visible in the conversation. `init` is a one-shot generation (not the long ref-chasing loop that `execute` / `create` / `resync` do), so the extra reasoning cost is negligible.

### Subagent flows (`create`, `resync`, `execute`)

These flows drive `agent-browser` and MUST run on **Sonnet** for browser reasoning quality. Dispatch via the `Agent` tool:

```
Agent(
  description: "Playbook <sub-command> — <short summary>",
  subagent_type: "general-purpose",
  model: "sonnet",
  prompt: <self-contained brief, see below>
)
```

The dispatch prompt MUST be self-contained because the subagent starts with no memory of this conversation. Include, in this order:

1. **Goal + the user's `$ARGUMENTS`** — one sentence of what to do.
2. **Flow reference** — an explicit instruction to `Read` the flow file at `<absolute-skill-root>/references/flows/<name>.md` and follow its steps in order.
3. **Preflight requirement** — before the first `agent-browser` call, `Read` `<absolute-skill-root>/references/preflight.md` and run all checks via `Bash`. If any check fails, STOP and print the user-facing block verbatim.
4. **Cheatsheet pointer** — consult `<absolute-skill-root>/references/agent-browser-cheatsheet.md` when translating Playbook step intents into `agent-browser ...` commands.
5. **Data paths** — `<absolute-skill-root>/data/ui-map.md` is the Playbook index; individual Playbooks live at `<absolute-skill-root>/data/[name].md`.
6. **Report contract** — return the Execution log + Playbook Output sections exactly as specified in the flow file.
7. **User-facing language rule** — render every `AskUserQuestion` (question + all `options`) and any user-visible prompt in the user's active session language. The English in the flow docs is a template.

**Why Sonnet, not general-purpose default**: browser operation requires fine-grained reasoning about a11y tree snapshots, ref invalidation, and Completion check heuristics. Haiku tends to misinterpret snapshots; Opus is overkill for the mechanical steps. Pin Sonnet explicitly — do NOT rely on the caller's default.

**Why `general-purpose` subagent type**: this is the portable subagent that every Claude-compatible runtime exposes, and the Claude Code `Agent` tool does not allow per-invocation `tools` / `mcpServers` restriction. Inline everything the subagent needs via the dispatch prompt. Do NOT create custom `.claude/agents/*.md` subagent definitions — they break skill portability to Codex and other runtimes.

**Relay the subagent's report verbatim**: after the subagent returns, forward its Execution log and Playbook Output to the user without summarization. These sections are the contract the user reads to judge success.

## Quality checklist (for `create` / `update`)

- [ ] Every step has all four elements (Action, Target, Completion check, On failure).
- [ ] Every target element is specified by role + text label.
- [ ] Prerequisites are documented.
- [ ] "Pre-execution decision rules" section is present (official docs URL required).
- [ ] "Constraints and limitations" section is present.
- [ ] "Domain knowledge" section is present.
- [ ] The Playbook index (`data/ui-map.md`) is up to date.

## Anti-patterns

- Procedures that check every entry via pagination.
- Procedures that try to implement numeric comparisons via text search.
- Procedures that "just try it" without checking the tool's constraints.
- Loops of "if not found, go to the next page".
