# `agent-browser` command cheatsheet

Reference for translating Playbook step intents into `agent-browser ...` commands. This is the authoritative mapping — Playbook files in this skill are written in agent-browser vocabulary.

Every command below assumes Environment preflight (`references/preflight.md`) has already passed. Commands are invoked via `Bash` with **no flags** — `AGENT_BROWSER_PROFILE` and `AGENT_BROWSER_HEADED` are set via environment variables and propagate automatically, so every call lands on the dedicated profile without any per-call setup.

## Command mapping

| Intent | agent-browser command |
|---|---|
| List / create tabs | `agent-browser tab list` / `tab new [URL]` |
| Navigate | `agent-browser open <URL>` |
| Read accessibility tree | `agent-browser snapshot -i` (iframes auto-inlined) |
| Read a11y tree scoped to a container | `agent-browser snapshot -i -s "<css>"` |
| Get link URLs alongside refs | `agent-browser snapshot -i --urls` |
| Click an element | `agent-browser click @eN` |
| Click by text / role / label | `agent-browser find text "..." click` (also: `find role button click --name "..."`) |
| Clear + type into an input | `agent-browser fill @eN "value"` |
| Type into the currently focused element | `agent-browser keyboard type "..."` |
| Press a key | `agent-browser press Enter` (or `cmd+Enter`, `Escape`, ...) |
| Wait N ms | `agent-browser wait 2000` |
| Wait for a ref / selector / URL / text | `agent-browser wait @eN` / `wait "#id"` / `wait --url "**/dashboard"` / `wait --text "Welcome"` |
| Evaluate JS (simple) | `agent-browser eval 'document.title'` |
| Evaluate JS (complex — nested quotes, multiline) | `agent-browser eval --stdin <<'JSEOF' ... JSEOF` |
| Screenshot (viewport) | `agent-browser screenshot` |
| Screenshot (full page) | `agent-browser screenshot --full` |
| Annotated screenshot with ref labels | `agent-browser screenshot --annotate` |
| Inspect network requests | `agent-browser network requests --type xhr,fetch` |
| Filter by status (non-2xx) | `agent-browser network requests --status 400-599` |
| Set viewport size | `agent-browser set viewport 1440 900` |
| Iframe scoping (if auto-inline misses something) | `agent-browser frame @eN` then `snapshot -i`, and `frame main` to return |
| Close just the current tab | `agent-browser tab close` |
| Close / disconnect the agent-browser session | `agent-browser close` (kills the CfT process tree and cleans daemon state) |

## Chaining

Prefer `agent-browser batch "open ..." "wait 2000" "snapshot -i"` for multi-step calls that have no intermediate decision. Use a single call when you need to read the output before choosing the next step (e.g. `snapshot -i` to discover refs).

## Ref lifecycle

Refs like `@e1` are invalidated after any navigation or DOM mutation. Re-run `snapshot -i` before interacting again.

## Console reading

agent-browser has no dedicated "read console" command. If you need console error verification, inject a capture early via `eval`:

```bash
agent-browser eval 'window.__errs=[]; window.addEventListener("error",e=>window.__errs.push(String(e.message)))'
```

then later read it back with:

```bash
agent-browser eval 'JSON.stringify(window.__errs)'
```

For API-level error checks, prefer `network requests --status 400-599`.
