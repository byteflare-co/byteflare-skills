# Environment preflight — `agent-browser` readiness checks

This skill drives browser automation through the **`agent-browser` CLI**. Run these checks, in order, via `Bash` **immediately before the first `agent-browser` call** in any flow that touches the browser. Skip entirely for sub-commands that only read / write markdown files.

The checks are cheap — run them every time, right before the first browser call, not behind a marker file.

## Check 1 — `agent-browser` is installed and on PATH

`agent-browser` can be installed via npm (`npm install -g agent-browser`), pinned in a project's toolchain manager (e.g. mise, asdf), or built from source. As long as it is on PATH, the skill can use it.

```bash
command -v agent-browser >/dev/null 2>&1 && agent-browser --version
```

If the command is not found, STOP and show the user this block verbatim:

> **`agent-browser` is not on PATH.**
>
> This Playbook skill uses the `agent-browser` CLI for browser automation. Install it with one of these methods:
>
> ```bash
> # npm (global)
> npm install -g agent-browser
>
> # mise (project-pinned, recommended for teams)
> # Add to .mise.toml: [tools] "npm:agent-browser" = "^0.25"
> mise install
> ```
>
> After installation, verify with `agent-browser --version`, then re-run the Playbook command.

## Check 2 — stale `agent-browser` daemon state is clean or recoverable

**Known footgun:** `agent-browser` keeps a background CDP daemon alive between invocations. If a previous Playbook run, test session, or crashed daemon left state files at `~/.agent-browser/default.{pid,sock,stream,engine,log}` pointing at a process that no longer exists — or worse, a process that is running but wedged into an unresponsive state — the next `agent-browser` call will either silently reuse stale state or hang with `Resource temporarily unavailable (os error 35)`.

A simple `agent-browser close` is insufficient because close itself can hang against a wedged daemon. The robust procedure is to inspect `~/.agent-browser/default.pid` directly, verify the process is alive, and force-clean the state files when it is not.

```bash
if [ -f ~/.agent-browser/default.pid ]; then
  pid=$(cat ~/.agent-browser/default.pid)
  if ! kill -0 "$pid" 2>/dev/null; then
    # dead PID — daemon process is gone but state files linger
    rm -f ~/.agent-browser/default.pid ~/.agent-browser/default.sock \
          ~/.agent-browser/default.stream ~/.agent-browser/default.engine \
          ~/.agent-browser/default.log
  else
    # live PID — try graceful close with a portable 5-second timeout
    # (GNU `timeout` is not available on stock macOS; fall back to
    #  `gtimeout` from Homebrew coreutils, then to perl's alarm())
    _ab_timeout() { command -v timeout >/dev/null 2>&1 && timeout "$@" || command -v gtimeout >/dev/null 2>&1 && gtimeout "$@" || perl -e 'alarm shift; exec @ARGV' -- "$@"; }
    if ! _ab_timeout 5 agent-browser close >/dev/null 2>&1; then
      # Guard against PID reuse: only SIGKILL if the process actually
      # belongs to agent-browser or Chrome, not an unrelated process
      # that recycled the stale PID.
      if ps -p "$pid" -o command= 2>/dev/null | grep -q 'agent-browser\|chrome'; then
        kill -9 "$pid" 2>/dev/null
      fi
      rm -f ~/.agent-browser/default.pid ~/.agent-browser/default.sock \
            ~/.agent-browser/default.stream ~/.agent-browser/default.engine \
            ~/.agent-browser/default.log
    fi
  fi
fi
```

No completion check needed — the snippet is idempotent, safe to re-run, and leaves the tree in a known-good state. `agent-browser close` is only allowed here (pre-run stale-daemon reset) and in the end-of-run cleanup of flow files. Calling it **mid-flight**, between the first operational `agent-browser` call and the end-of-run cleanup, would destroy the refs the Playbook captured (see `references/flows/execute.md` → "Forbidden during execution").

## Check 3 — `AGENT_BROWSER_PROFILE` points at a dedicated profile

`agent-browser` supports a dedicated browser profile via the `AGENT_BROWSER_PROFILE` environment variable, which isolates session cookies, local storage, and login state from your everyday Chrome browsing. Each project should use its own dedicated profile under `~/.agent-browser/profiles/`.

```bash
[[ -n "$AGENT_BROWSER_PROFILE" && "$AGENT_BROWSER_PROFILE" == */.agent-browser/profiles/* ]]
```

If the check fails, STOP and show this block verbatim:

> **`AGENT_BROWSER_PROFILE` is not configured.**
>
> This Playbook skill requires a dedicated browser profile to isolate login sessions. Set the `AGENT_BROWSER_PROFILE` environment variable to a path under `~/.agent-browser/profiles/`.
>
> Common setup methods:
>
> ```bash
> # Option 1: mise .mise.toml (recommended for teams — auto-activates per-repo)
> # [env]
> # AGENT_BROWSER_PROFILE = "{{env.HOME}}/.agent-browser/profiles/myproject"
> # AGENT_BROWSER_HEADED = "1"
>
> # Option 2: direnv .envrc
> # export AGENT_BROWSER_PROFILE="$HOME/.agent-browser/profiles/myproject"
> # export AGENT_BROWSER_HEADED=1
>
> # Option 3: manual export (current shell only)
> export AGENT_BROWSER_PROFILE="$HOME/.agent-browser/profiles/myproject"
> export AGENT_BROWSER_HEADED=1
> ```
>
> Replace `myproject` with a name that identifies this project. After setting, re-run the Playbook command.

## Check 4 — viewport is set to a usable size

`agent-browser` in headed mode opens Chrome for Testing at the OS-default window size, which may be too narrow for the target application. Set the viewport explicitly — the call is idempotent and persists for the daemon session lifetime.

```bash
agent-browser set viewport 1440 900
```

Run this **after** Checks 1–3 pass but **before** any other `agent-browser` call. It is typically the call that spawns Chrome for Testing, so everything downstream inherits the viewport.

If you need a different size for a specific Playbook (e.g. mobile emulation), override it later in the flow with another `set viewport` call.

## Invocation convention (post-preflight)

After all checks pass, **every** browser command in this skill and its Playbooks MUST be invoked via `Bash` as `agent-browser <command> ...` — no `--profile` flag, no `--auto-connect` flag. The `AGENT_BROWSER_PROFILE` env var (from Check 3) handles profile selection automatically.

```bash
agent-browser open http://example.com
agent-browser snapshot -i
agent-browser click @e3
```

Chrome for Testing spawns automatically on the first call, reuses the dedicated user-data-dir, and is shared across all subsequent calls in the same run via `agent-browser`'s internal daemon. Close at the end of the run with `agent-browser close`.
