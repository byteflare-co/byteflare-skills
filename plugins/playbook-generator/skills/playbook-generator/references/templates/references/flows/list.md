# Flow: `/playbook list` — List registered Playbooks

Show every currently registered Playbook. Pure file-read flow — does NOT touch the browser, so no preflight is required.

**Prerequisite**: `data/ui-map.md` must already exist. If not, reply "Please run `/playbook init [URL]` first to create the UI Map." and stop.

## Step 1: Read the Playbook index
1. Read `data/ui-map.md`.
2. Extract the rows of the "Playbook index" table.

## Step 2: Print the list
Use this format:

```
Registered Playbooks (N)

| # | Keyword | File | Summary |
|---|---------|------|---------|
| 1 | ... | ... | ... |
...

Run: /playbook [keyword]
Details: see data/[file]
```

## Step 3: Edge cases
- If there are zero Playbooks, reply: "No Playbooks are registered yet. Use `/playbook create` to add one."
- If the Playbook index table is missing from `ui-map.md`, reply: "No Playbook index found in `ui-map.md`. Please rerun `/playbook init` or add the table manually."

## Step 4: UI Map freshness check (automatic rescan notification)

Read `Last synced: YYYY-MM-DD` from the top of `ui-map.md` and compute the difference from today (`date +%Y-%m-%d`).

| Elapsed days | Message |
|---|---|
| Under 30 days | Show nothing |
| 30-59 days | `ui-map.md was last synced N days ago. Run /playbook resync if the UI may have changed.` |
| 60+ days | `ui-map.md was last synced N days ago. Playbooks may no longer work. Run /playbook resync to rescan.` |

If the `Last synced` field is missing entirely (old version of `ui-map.md`):
- Report `ui-map.md has no Last synced field. Run /playbook resync to sync with the current UI state.`
