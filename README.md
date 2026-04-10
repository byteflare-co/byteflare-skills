# byteflare-skills

A collection of Claude Code plugins by Byteflare.

## Installation

```
/plugin marketplace add byteflare-co/byteflare-skills
```

Then install individual plugins:

```
/plugin install spec-skills-generator@byteflare-skills
/plugin install playbook-generator@byteflare-skills
```

## Plugins

### spec-skills-generator

Auto-generate 3-layer specification documents and maintenance skills for any codebase.

**Installation:**
```
/plugin install spec-skills-generator@byteflare-skills
```

**What It Does:**

- **3-layer specification documents**: Overview (`01_overview.md`), Business Spec (`02_business_spec.md`), Technical Spec (`03_technical_spec.md`)
- **`/spec` skill**: Q&A skill for querying your specifications
- **`/spec-maintenance` skill**: Keeps specs in sync with code changes
- **`check_spec_drift.py`**: Automated drift detection script
- **CLAUDE.md integration**: Impact mapping section for your project

**Usage:**
```
/spec-skills-generator:spec-skills-generator
```

The skill will:
1. Auto-detect your project structure (languages, entry points, IaC, tests, etc.)
2. Ask configuration questions (output directory, existing docs)
3. Deep-analyze your codebase
4. Generate 3-layer spec documents
5. Create `/spec` and `/spec-maintenance` skills
6. Set up drift detection and CLAUDE.md integration

**Generated Files:**

| File | Description |
|------|-------------|
| `docs/specification/01_overview.md` | Project overview, architecture, component catalog |
| `docs/specification/02_business_spec.md` | Business rules, domain model, use cases |
| `docs/specification/03_technical_spec.md` | API specs, data models, infrastructure |
| `.claude/skills/spec/SKILL.md` | `/spec` Q&A skill |
| `.claude/skills/spec-maintenance/SKILL.md` | `/spec-maintenance` skill |
| `scripts/check_spec_drift.py` | Spec-code drift checker |

**Requirements:**
- Claude Code CLI
- Python 3.10+

---

### playbook-generator

A meta-skill that generates a browser automation playbook skill into your project. The generated skill is a multi-file setup (SKILL.md dispatcher + flow files + reference files) that can be committed to git and shared with your team.

**Installation:**
```
/plugin install playbook-generator@byteflare-skills
```

**Usage:**
```
/playbook-generator:playbook-generator
```

The generator will:
1. Detect your project structure (CLAUDE.md hints, `.agents/skills/`, `.claude/skills/`, etc.) and suggest a placement
2. Write the multi-file skill to the chosen location (e.g. `.claude/skills/playbook/`)
3. Verify git tracking and suggest `.gitignore` adjustments if needed

**Generated Skill Structure:**

```
<skill-root>/
  SKILL.md                              — Sub-command dispatcher
  references/
    preflight.md                        — Environment checks before browser calls
    agent-browser-cheatsheet.md         — agent-browser CLI command reference
    flows/
      init.md, create.md, list.md,      — Flow files for each sub-command
      resync.md, update.md, execute.md
  data/                                 — User-generated (populated by /playbook init)
    ui-map.md                           — UI Map + Playbook index
    [name].md                           — Individual Playbooks
```

**Generated Skill Features:**

| Command | Description |
|---------|-------------|
| `/playbook init [URL]` | Crawl the target product and generate a UI Map |
| `/playbook create` | Author a new Playbook via interactive interview |
| `/playbook list` | List registered Playbooks |
| `/playbook resync [screen]` | Rescan the UI and detect changes |
| `/playbook update` | Manually edit existing Playbooks or UI Map |
| `/playbook [operation]` | Execute a registered Playbook |

Browser automation is powered by the [`agent-browser`](https://github.com/anthropics/agent-browser) CLI. The skill uses a hybrid dispatch model: `init`, `list`, and `update` run inline so the user can watch live; `create`, `resync`, and `execute` are dispatched to a Sonnet subagent for cost optimization and context isolation.

**Updating:**

After updating the plugin, re-run the generator in each project to pick up the latest templates:

```
/plugin marketplace update byteflare-skills
/playbook-generator:playbook-generator
```

The generator shows a diff of changed files before overwriting and creates `.bak` backups automatically. User-generated data in `data/` is never touched.

---

## License

MIT
