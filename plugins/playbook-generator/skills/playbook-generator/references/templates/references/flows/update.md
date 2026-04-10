# Flow: `/playbook update` — Manually edit an existing Playbook or UI Map

Manually edit an existing Playbook or `data/ui-map.md` to record information that cannot be obtained by a browser scan — domain knowledge, additional constraints, clarifications, etc. Pure file-edit flow — does NOT touch the browser, so no preflight is required.

**Prerequisite**: `data/ui-map.md` must already exist.

**Difference from `resync`**:
- **`resync`** rescans the actual UI, auto-detects diffs, and updates `ui-map.md`. Use it to keep up with UI changes.
- **`update`** (this flow) manually edits existing Playbooks or `ui-map.md`. Use it to add domain knowledge, append constraints, or record information that cannot be obtained by a browser scan.

## Procedure

1. Read the "Playbook index" in `data/ui-map.md` and show the list to the user (`ui-map.md` itself is also a valid target).
2. Ask the user which one to update.
3. Read the chosen file from `data/`.
4. Ask: "What do you want to update?" (add a step, append a constraint, add domain knowledge, add a screen, etc.)
5. Apply the update with `Edit` and confirm with the user.
6. If the edit changes the Playbook's name, summary, or purpose, also update the corresponding row in the "Playbook index" table of `ui-map.md`.

## Important: `Last synced` is NOT touched

`update` is a manual-editing flow, so it **does NOT update** the `Last synced` field in `ui-map.md`. `Last synced` represents the date on which the UI was actually verified, so it is only updated by `resync` / `init` runs that actually scan the browser.
