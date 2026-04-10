# Flow: `/playbook resync [screen]` — UI Map rescan

Re-crawl the target product's UI, detect diffs between the state recorded in `data/ui-map.md` and the current UI, and apply them. Used to keep up with UI changes. Invoked from the main `playbook` SKILL.md via sub-command routing.

**Prerequisite**: `references/preflight.md` checks must have already passed before the first `agent-browser` call here. The dedicated Chrome for Testing profile must also be logged in to whatever product the Playbook targets; if it is not, `/playbook init` walks through manual login — run it once before continuing. Consult `references/agent-browser-cheatsheet.md` for command syntax.

## Step 1: Decide the target scope
- No argument → target every screen in the "Screens" table of `ui-map.md`.
- With argument → target screens whose name partially matches the argument.

Show the target screen list to the user and ask for confirmation:

```
resync targets (N):
  1. Dashboard (/dashboard)
  2. Members (/members)
  ...

Proceed with the rescan? [y/n]
```

## Step 2: Re-crawl & detect diffs

For each target screen:

1. `agent-browser open <screen URL>`.
2. `agent-browser wait 2000` (if the page is slow), then `agent-browser snapshot -i` to get the accessibility tree.
3. Read the "UI elements" table of that screen from `ui-map.md`.
4. Compare the current elements to the recorded ones and classify diffs:

| Kind | Criterion | Icon |
|---|---|---|
| Added | Present now, missing from ui-map | NEW |
| Removed | Present in ui-map, missing now | DEL |
| Text changed | Same role, different name (judged using neighbouring elements) | CHG |
| Role changed | Same name, different role | CHG |
| URL changed | The screen's own URL changed | URL |

**Heuristics for similarity matching** (to distinguish "text changed" from "added + removed"):
- When a pair of removed and added candidates exists, check the following in order:
  1. They are in the same section.
  2. Their neighbouring elements match.
  3. They have the same role.
- If all three hold, treat it as a text change.
- When ambiguous, defer the decision to the user in Step 3.

## Step 3: Show the diff summary and ask for approval

Show the aggregated diff for all screens:

```
UI change detection summary

[Member detail screen]
  DEL Removed: button "Save"
  NEW Added: button "Confirm"
  -> Auto-match candidate: "Save" -> "Confirm" (treat as text change? [y/n])

[Members screen]
  CHG Text changed: link "Users" -> "Members"
  CHG Text changed: button "Cancel" -> "Back"

[Dashboard]
  No changes
```

Ask the user to pick an approval mode via `AskUserQuestion`:
- [1] Apply everything
- [2] Select individually (y/n per diff)
- [3] Cancel

For any ambiguous auto-match candidates, confirm them individually.

## Step 4: Apply to `ui-map.md`

Apply the approved diffs to `ui-map.md` in place:

1. **Added element** → add a row to the "UI elements" table of the screen.
2. **Removed element** → delete the row.
3. **Text change / role change** → edit the row.
4. **URL change** → update both the "Screens" table and the `**URL:**` field of the screen.
5. Update **Last synced** to today's date.

Completion report:

```
Updated ui-map.md

Changes:
  - Member detail screen: removed 1, added 1 (applied as text change)
  - Members screen: text changed 2

Last synced: YYYY-MM-DD

Note: Existing Playbooks may still reference the changed elements.
Check manually with:
  grep -r '"[old text]"' <skill-root>/data/
```

## Step 5: Cleanup (mandatory)

Run `agent-browser close` before finishing this flow to terminate the Chrome for Testing process.

## resync caveats

- **The browser must be able to reach the target product** (e.g. already logged in).
- **Dynamic UI elements** (clocks, usernames) show up as diffs every time. Ideally they should be tagged as "dynamic" when first recorded (future extension).
- **Elements inside modals and dropdowns** cannot be detected unless the open state is reproduced. If `init` recorded them in the open state, `resync` must open them the same way.
- **Auto-updating affected Playbooks is not implemented.** This version only updates `ui-map.md`.
