# Flow: `/playbook [operation]` — Execute a Playbook

Run an existing Playbook end-to-end. This flow drives `agent-browser` via `Bash`, so the Environment preflight (`references/preflight.md`) MUST have already passed before the first browser call.

**MANDATORY cleanup rule**: whenever this flow ends — successful completion, early stop via an `On failure` branch, user abort, or unexpected error — you MUST run `agent-browser close` before returning the final report. Step 5 restates this; do not skip it. The dedicated Chrome for Testing process must not be left running between Playbook runs.

**Prerequisites**:
- `data/ui-map.md` exists (otherwise tell the user to run `/playbook init [URL]` first).
- Environment preflight checks (`references/preflight.md`) have passed in this run.
- The dedicated Chrome for Testing profile is logged in to whatever product the Playbook targets. If it is not, `/playbook init` walks through manual login — run it once before continuing.

## Step 1: Locate the Playbook

1. Read the "Playbook index" table in `data/ui-map.md`.
2. Match `$ARGUMENTS` against the keyword column and identify the target Playbook file (under `data/`).
3. If there is no match, show the Playbook index and ask: "Which one should I run?"

## Step 2: Load the Playbook and decide feasibility

1. Read `data/[name].md`.
2. Verify the "Prerequisites".
3. Check whether the user's request falls under "Constraints and limitations".
4. **If it does → do NOT start operating; explain the constraint and offer an alternative.**
5. If unclear, verify by fetching the "official docs" URL with `WebFetch` before deciding.

## Step 3: Run the operation

Execute the Playbook procedure directly using `agent-browser` via the `Bash` tool. Consult `references/agent-browser-cheatsheet.md` for the full command mapping.

### Execution procedure

1. For every step in the Playbook's `Procedure` section:
   - Run the `Action` via the `Bash` tool, using the commands in `references/agent-browser-cheatsheet.md`.
   - Chain decision-less calls with `agent-browser batch "open ..." "wait 2000" "snapshot -i"` to cut round trips.
   - After each step, evaluate the `Completion check`. If it fails, follow the `On failure` branch (retry / stop / report).
2. Track what you observe: steps completed, final state (last snapshot or URL), and any errors.
3. Hand the results to Step 4 for reporting.

### Forbidden during execution

- **`agent-browser close` / `agent-browser close --all` mid-execution** — tears down the CDP session / daemon while the Playbook is still running, and ruins the refs you just captured. Only close individual tabs with `agent-browser tab close`. Legitimate uses of `agent-browser close` are (a) the stale-daemon reset in Environment preflight Check 2, which happens *before* execution starts, and (b) the mandatory cleanup in Step 5, which happens *after* all Playbook steps (including the Playbook Output report) are done.
- **Passing explicit `--profile <other>` or `--auto-connect`** — would override the `AGENT_BROWSER_PROFILE` convention. The environment variable is the only sanctioned profile source.
- **Interacting with elements beyond what the Playbook instructs** — Playbooks are the contract. If you notice an element that "should" be clicked but is not in the Playbook, stop and report it instead of clicking.

## Step 4: Report the result

Return your report in this exact structure, in order. **Both sections are MANDATORY** — the Execution log is what gives the user debuggability, and the Playbook Output is what carries the pass/fail verdict.

### (a) Execution log (MANDATORY — required for debuggability)

Because this flow typically runs inside a subagent dispatched by the playbook SKILL.md, the Claude Code UI may not show the subagent's intermediate tool calls in the main session — only this final response. Without a structured per-step log here, the user has no way to audit what the subagent actually did, especially on a failing run. **Do NOT skip this section even on a clean pass.**

Format:

````markdown
## Execution log

### Preflight
- Check 1 — binary: OK agent-browser <version>
- Check 2 — stale daemon recovery: OK (cleaned stale state | no-op)
- Check 3 — AGENT_BROWSER_PROFILE: OK <profile name>
- Check 4 — viewport: OK <width>x<height> set

### Step N — <Playbook step name>
- Bash: `agent-browser <cmd>` → <1-line result or "OK">
- Bash: `agent-browser <cmd>` → <1-line result>
- Observation: <what we saw, e.g. "snapshot had heading 'Dashboard' + 5 sidebar links, no login form">
- Completion check: PASS / FAIL / WARN (<reason if not PASS>)
- Decision: proceed / retry / stop / on-failure:<which branch>

(repeat per Playbook step)

### Final state
- URL: `<last focused tab URL>`
- Tab delta: `<+N new, -N closed, net N>`
- Lingering concerns: `<none, or bullet list>`

### Cleanup
- `agent-browser close` → OK Closed agent-browser session. | WARN <error summary, report still returned>

### Errors (only if any)

<full error output with context — do not truncate error messages>
````

**Sizing rules:**
- Each step's log should be ~4-8 lines. Do NOT paste entire snapshots, full network-request dumps, or large command outputs. Summarize to the minimum signal needed to justify the Completion check verdict.
- Bash result 1-liners: reduce to what matters (e.g. "tab 3 opened at http://...", "201 POST /api/items, id abc123...", "snapshot 312 refs, heading present").
- On errors: do NOT truncate. Paste the full stderr / exception, plus the command that produced it.

### (b) Playbook Output

After the Execution log, append the Playbook's own `Output` block (from the Playbook markdown loaded in Step 2), with PASS/WARN/FAIL filled in and any required fields populated. This is the verdict the user is looking for at a glance.

## Step 5: Cleanup (mandatory)

After Step 4's report is assembled — regardless of pass / fail / early stop — run `agent-browser close` before returning the final response. This terminates the dedicated Chrome for Testing process tree and cleans daemon state so the next Playbook command starts from a clean slate. Record the outcome on the `Cleanup` line of the Execution log (already present in the template above).

- Run the cleanup **after** assembling the report but **before** returning it, so the close verdict can be included in the `Cleanup` line.
- If `agent-browser close` itself errors (e.g. the daemon is already gone because of an earlier crash), record the error on the `Cleanup` line but still return the report — do NOT retry in a loop, the next run's preflight Check 2 will force-clean any lingering state.
- Do NOT skip this step on failure paths. An early stop via an `On failure` branch is exactly when leaked daemons tend to pile up.
