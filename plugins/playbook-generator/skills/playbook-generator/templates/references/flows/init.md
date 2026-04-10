# Flow: `/playbook init [URL]` — UI Map generation

Crawl the target product's UI and generate `data/ui-map.md`. Invoked from the main `playbook` SKILL.md via sub-command routing. This flow also owns first-time browser setup (login), since the dedicated Chrome for Testing profile starts empty and needs authentication before any Playbook can use it.

**Prerequisite**: `references/preflight.md` checks must have already passed before the first `agent-browser` call here. Consult `references/agent-browser-cheatsheet.md` when translating step intents into `agent-browser ...` commands.

**MANDATORY cleanup rule**: whenever this flow ends — successful completion, user abort, error, or "keep existing UI Map" exit — you MUST run `agent-browser close` before returning control to the user. Each STOP point below restates this; do not skip it. The dedicated Chrome for Testing process must not be left running between sessions.

## Step 0: Login setup (browser authentication for the skill)

Before crawling can start, verify the dedicated Chrome for Testing profile is logged in to the target product. This is a single code path that works for both first-time setup and subsequent init runs.

1. **Open the target landing page.** The `AGENT_BROWSER_PROFILE` and `AGENT_BROWSER_HEADED` environment variables handle profile selection and visibility:

   ```bash
   agent-browser open <TARGET_URL>
   ```

   - On the very first invocation ever, the profile directory is auto-created with an empty Chrome profile.
   - On subsequent invocations, the existing profile (cookies and all) is reused.

2. **Classify the landing URL.** Give the application a moment to complete any client-side auth redirect, then read where we actually landed:

   ```bash
   agent-browser wait 2000
   agent-browser get url
   ```

   Interpret the result:

   - URL matches the expected application page (no login/auth redirect) → **logged in, skip to Step 1**.
   - URL contains `/login`, `/sign-in`, an SSO/OAuth hostname, or any other auth page → **manual login required, continue to step 3 below**.

3. **Walk the user through manual login.** Use `AskUserQuestion` to pause until the user has completed authentication in the visible Chrome for Testing window:

   - **Question**: `"A Chrome for Testing window is open at the login page. Please complete the login in that window, then choose 'Done' to continue. If you cannot complete the login, choose 'Abort' to stop."`
   - **Options**: `["Done", "Abort"]`

   After the user responds:

   - **Abort** → run `agent-browser close`, then STOP and tell the user to investigate, then re-run `/playbook init`.
   - **Done** → re-check the URL:

     ```bash
     agent-browser wait 1000
     agent-browser get url
     ```

     - If the URL now matches the expected application page → login successful, proceed to Step 0.5.
     - If the URL still shows an auth page → the login did not take. Ask again with the same options. After **3 consecutive failed attempts**, run `agent-browser close` and STOP with: `"Manual login did not succeed after 3 attempts. Please delete the profile directory and re-run /playbook init for a clean slate, or investigate the authentication flow."`

## Step 0.5: Existing UI Map check

Once Step 0 confirms the profile is logged in, but BEFORE any crawling begins, check whether a previous UI Map already exists:

```bash
test -f <skill-root>/data/ui-map.md && echo exists || echo missing
```

- **missing** → continue to Step 1.
- **exists** → ask the user with `AskUserQuestion`:
  - **Question**: `"data/ui-map.md already exists. Do you want to keep it as is and exit, or regenerate it from scratch (this will overwrite the existing file)?"`
  - **Options**: `["Keep existing (exit)", "Regenerate (overwrite)"]`
  - On **Keep existing (exit)** → run `agent-browser close`, then STOP. Tell the user: `"Kept the existing data/ui-map.md untouched. Re-run /playbook init any time to regenerate, or use /playbook resync to refresh a specific screen."`
  - On **Regenerate (overwrite)** → continue to Step 1. Step 4 will overwrite the existing file with the fresh crawl.

## Step 1: Confirm the URL

- Read the URL from `$ARGUMENTS`.
- If there is no URL, ask: "What URL should I target? If login is required, please sign in first."

## Step 2: Present the screen list

1. Run `agent-browser open <URL>` then `agent-browser snapshot -i` to read the accessibility tree.
2. From navigation elements (sidebar, header menu, tabs, etc.), list the main reachable screens.
3. Ask: "I found these screens. Should I cover all of them, or only specific ones?"

## Step 3: Crawl & capture

Visit each target screen one by one. For each screen:

1. `agent-browser open <screen URL>` (or use `batch` to chain open + wait + snapshot in one call).
2. `agent-browser snapshot -i` — accessibility tree with refs (iframes auto-inlined).
3. `agent-browser screenshot --full` — visual reference snapshot.
4. Record: screen name, URL, key UI elements (role, name, text label), and section layout.

Crawling rules:

- After finishing each screen, report "Recorded [screen name]. Moving on."
- For long pages, `agent-browser snapshot -i` already returns the full tree in one shot — no need to split top/middle/bottom. If the tree is huge, scope with `-s "<css selector>"` to a container.
- Also record the open state of modals and dropdowns (click to open first, then `snapshot -i` again).
- Report any errors or unexpected screens to the user.

## Step 4: Generate `ui-map.md`

Create the `data/` directory (`mkdir -p <skill-root>/data`) and generate `data/ui-map.md` with this structure. Set both `Created` and `Last synced` to **today's date** (get it with `date +%Y-%m-%d`):

```markdown
# [Product Name] UI Map
Created: YYYY-MM-DD
Last synced: YYYY-MM-DD

## Playbook index
(Initially empty. A new row is added every time `create` adds a Playbook.)
| Keyword | File | Summary |
|---------|------|---------|

## Screens
| # | Screen | URL | Summary |
|---|--------|-----|---------|
| 1 | ... | ... | ... |

## Navigation map
- Dashboard
  - → Click "XXX" → XXX screen
  - → Click "YYY" → YYY screen

## Shared UI elements
(Headers, sidebars, navigation shared across all screens.)

## Screen details

### 1. [Screen name]
**URL:** /path

#### Layout
- Header: [content]
- Sidebar: [content]
- Main area: [content]

#### UI elements
| Element | Type | Text / Label | Action |
|---------|------|--------------|--------|
| ... | button | "Save" | Click to save data |

#### Notes
- [Screen-specific caveats]
```

## Step 5: Confirmation

1. Any screens I missed?
2. Anything to correct or add in the screen descriptions?
3. Do you want to continue and author a Playbook now? (`/playbook create`)

## Step 6: Cleanup (mandatory)

Regardless of the user's answer in Step 5, run `agent-browser close` before finishing this flow. This terminates the dedicated Chrome for Testing process tree and cleans daemon state so the next Playbook command starts from a clean slate. Report `"Closed agent-browser session."` after the command returns.

## Element recording principles

- Prefer text labels ("Save", "Cancel", ...). Avoid pointing at elements by color or position.
- Record accessibility tree `role`, `name`, and `description` verbatim.
- This UI Map will later drive browser automation, so prioritize information that uniquely identifies each element.
