---
name: spec-skills-generator
description: >
  A meta-skill that auto-generates three-layer specification documents (01_overview / 02_business_spec / 03_technical_spec)
  for any project, and builds /spec (spec Q&A) and /spec-maintenance (spec maintenance) skills.
  Analyzes the codebase to generate specs, leveraging existing specs or documents as input when available.
  Triggered by keywords like "generate specs", "spec-skills-generator", "setup specification management",
  "create spec skills", "build spec documents".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Task
---

# Automatic Specification Skill Generation

Generates three-layer specification documents for any project and auto-generates `/spec` and `/spec-maintenance` skills.

## Prerequisites

- Analyzes the codebase to generate three-layer specs (01_overview / 02_business_spec / 03_technical_spec), then builds /spec and /spec-maintenance skills based on them
- Leverages existing specs or documents as input when available

## Output Language Rule

Generate spec documents in the language detected from the project's CLAUDE.md `<language>` tag. If no language is configured, default to English.

## Workflow

Execute the following Phases 1 through 8 in order.

---

### Phase 1: Project Discovery (Automatic)

1. Use Glob to locate `**/spec-skills-generator/**/discover_project.py`, then run:

```bash
python {found_path} "$(pwd)"
```

2. Review the following from the output JSON:
   - `spec_files`: List of spec document candidates and their heading structure
   - `source_code`: Source code structure (primary languages, entry points, shared modules)
   - `tests`: Test directories, test file counts, test configuration
   - `iac`: Infrastructure-as-Code files
   - `build_system`: Build system
   - `claude_config`: Presence of CLAUDE.md, language settings, existing skills

3. If spec/document files are detected, Read them to leverage as existing knowledge (parallel reads recommended)

---

### Phase 2: Information Gathering (Interactive)

Use AskUserQuestion to confirm the following:

**Question 1: Confirm spec output path**
- "Please confirm the output directory for specs."
- Options: "`docs/specification/` (default)" / "Specify a custom path"
- Default: `docs/specification/`

**Question 2: Confirm use of existing documents** (only if files detected in `spec_files`)
- Present the list of detected existing document files
- "Would you like to use these existing documents as reference for spec generation?"
- Options: "Yes, use as reference" / "No, generate from code only"

**Question 3: Confirm overwrite of existing skills** (only if existing `/spec` or `/spec-maintenance` skills are found)
- "Existing /spec and /spec-maintenance skills were found. Overwrite them?"
- Options: "Overwrite" / "Skip"

**Language setting**: Use `claude_config.detected_language` if available. Otherwise, default to English.

---

### Phase 3: Spec Generation (Core Feature)

Use Glob to locate `**/spec-skills-generator/**/references/spec-document-templates.md`, then Read it to understand the template structure.

**Project name**: Use `project_name` from discover_project.py (directory name) as the spec title. If it seems unnatural (e.g., directory name is `src` or `app`), confirm with the user via AskUserQuestion.

**Section application rules** (the goal is NOT to fill every template section; only document information that exists in the project):
- No API endpoints: 03_technical_spec §1 API Spec → Reinterpret as "Command Interface" etc., or omit the section entirely
- No external integrations: 03_technical_spec §2 External Integrations → Omit
- No IaC: 03_technical_spec §5 Infrastructure → Omit or document deployment steps only
- No tests: 03_technical_spec §6 Cross-Reference Matrix → Source file list only
- If sections are omitted, renumber remaining sections sequentially

#### Step 1: Deep Codebase Analysis

In addition to discover_project.py results, Read the following for deep understanding:

- **Entry points**: Read each file in `source_code.entry_points` → Extract API specs and processing flows
- **Shared modules**: Read each file in `source_code.shared_modules` → Understand business logic and domain models
- **Data models**: Read ORM definitions, schema files, type definitions → Identify data structures
- **IaC files**: Read `iac.files` → Understand infrastructure configuration (skip if none)
- **Test files**: Leverage `tests` results from discover_project.py → Understand test directory structure, test counts, and supplement feature lists
- **Existing documents**: If "use as reference" was selected in Phase 2, leverage detected documents as knowledge

**Context management guidelines** (to prevent context exhaustion in large projects):
- Entry points: Read all (typically 10-20 files)
- Shared modules: Up to 15 major ones (prioritized by file size)
- IaC files: Up to 5 main definition files
- Read approximately the first 200 lines of each file. The goal is to grasp the overall picture, not to read every line
- For projects with many files, using Task(Explore) agents is recommended

#### Step 2: Generate 01_overview.md

Generate according to template §1-§6:

1. **§1 Project Overview**: Business context, related systems, role of this system, related repositories
2. **§2 System Architecture**: Architecture diagram (**Mermaid diagram required**), data flow overview, processing flow diagrams
3. **§3 Component List**: Tables categorized by function. **Auto-count from code and record accurate counts**
4. **§4 Glossary**: Extract domain terms and abbreviations from the code
5. **§5 Environment Configuration**: Environment list, runtime settings, parameters (values redacted)
6. **§6 Document Structure**: Structure and management of this spec document set

Output to: `{spec_dir}/01_overview.md`

#### Step 3: Generate 02_business_spec.md

Read and document business logic source code:

1. **§1 Domain Model**: Key entities, category definitions, state transitions
2. **§2-N Business Specs by Feature**: Identify use cases per entry point and describe:
   - Processing flow (numbered list + conditional branches)
   - Business rules (**express decision logic in pseudocode**)
   - Data examples (**in JSON format**)
   - Error cases and handling
3. **§X Time-Limited Rules**: Document if TODO/FIXME/time-limited logic exists in code (omit if none)

Output to: `{spec_dir}/02_business_spec.md`

#### Step 4: Generate 03_technical_spec.md

Describe technical implementation details:

1. **§1 API Spec**: Extract common specs + per-endpoint specs from handler code
2. **§2 External Integration Interfaces**: Extract authentication methods, API lists, error codes from client modules
3. **§3 Data Model**: Generate DB structure, repository methods, type definitions from schema definitions
4. **§4 Implementation Module Details**: List by business logic layer and infrastructure layer
5. **§5 Infrastructure**: Extract compute resources, API Gateway, DB, storage, etc. from IaC files
6. **§6 Cross-Reference Matrix**: Build source file ↔ test file correspondence

Output to: `{spec_dir}/03_technical_spec.md`

#### Step 5: User Review

1. Report a summary of the 3 generated files:
   - Section structure and key content summary for each file
   - Explicitly note any missing information or sections filled by inference

2. Confirm via AskUserQuestion:
   - Options: "Proceed as-is" / "Modifications needed"
   - If "Modifications needed": Revise based on feedback and report the summary again (maximum 1 iteration)

3. After confirmation, proceed to Phase 4

---

### Phase 4: Generate /spec Skill

Use Glob to locate `**/spec-skills-generator/**/references/spec-skill-template.md`, then Read it as a reference template.

**The template is a structural reference, not meant for direct variable substitution.** After understanding the structure of the specs generated in Phase 3, do the following:

1. **Build a spec map**: Analyze the heading structure of each spec file and create a topic → section correspondence table
   - Express topic names as keywords users would naturally use when asking questions
   - The number and categories of spec files vary per project (not always 3 files)

2. **Set trigger keywords**: Extract project-specific keywords from the spec content

3. **AskUserQuestion options**: Set 3-4 major topics from the specs as options

4. Write to `.claude/skills/spec/SKILL.md`

---

### Phase 5: Generate /spec-maintenance Skill

Use Glob to locate `**/spec-skills-generator/**/references/spec-maintenance-template.md`, then Read it as a reference template.

1. **Spec structure table**: List the main sections of each spec file

2. **Build impact mapping table**: Create correspondence between source code structure and spec sections
   - `source_code.entry_points`: Entry points → Corresponding spec sections
   - `source_code.shared_modules`: Shared modules → Corresponding spec sections
   - `iac.files`: IaC files → Infrastructure-related spec sections
   - If correspondence is unclear, map roughly at the directory level

3. **Update patterns**: Describe common update patterns based on the project structure

4. **docs-check command**: Configure based on build system
   - If Makefile exists: `make docs-check`
   - If npm: `npm run docs-check`
   - Otherwise: `python scripts/check_spec_drift.py`

5. Write to `.claude/skills/spec-maintenance/SKILL.md`

---

### Phase 6: Generate check_spec_drift.py

Use Glob to locate `**/spec-skills-generator/**/references/check-spec-drift-example.py`, then Read it as a reference implementation.

**The reference implementation contains content specific to the addplus-proxy project.** Customize for the project structure:

1. **Path configuration**: Adjust `PROJECT_ROOT`, `SPEC_DIR`, source directory paths for the project

2. **Component count functions**: Create `_count_*()` functions matching the project structure
   - Example: Instead of Lambda functions, use API routes, React components, Go packages, etc.
   - If no IaC, omit Terraform-related checks

3. **Spec table count functions**: Adjust regex in `_count_spec_*()` to match spec headings
   - `_count_table_rows()` is generic and can be used as-is

4. **Filename coverage check**: Adjust for the project's source file structure

5. **Metadata freshness check**: Omit if specs don't have a "Last verified date"

6. Write to `scripts/check_spec_drift.py`

---

### Phase 7: Build System & CLAUDE.md Integration

Use Glob to locate `**/spec-skills-generator/**/references/claude-md-section.md`, then Read it as a reference template.

1. **Build system integration**:
   - If Makefile exists: Add a `docs-check` target
     ```makefile
     docs-check:  ## Check spec-code consistency
     	python scripts/check_spec_drift.py
     ```
   - If package.json exists: Add `"docs-check"` to `scripts`
   - If neither exists: Skip (run `python scripts/check_spec_drift.py` directly)

2. **CLAUDE.md update**:
   - If CLAUDE.md exists: Append a "Spec Maintenance" section
   - If CLAUDE.md does not exist: Ask via AskUserQuestion whether to create it
   - If a "Spec Maintenance" section already exists: Confirm overwrite
   - Replace template placeholders with actual values

---

### Phase 8: Verification

1. Dry-run `check_spec_drift.py`:
   ```bash
   python scripts/check_spec_drift.py
   ```

2. Review the results:
   - Success if completed without errors
   - Fix any Python errors that occur

3. Report generated results to the user:
   - List of generated files
   - How to use `/spec` and `/spec-maintenance`
   - Summary of `check_spec_drift.py` execution results

---

## Important Notes

- **Templates are structural references**: Do not simply substitute variables in templates under `references/`. Understand the project's characteristics and adjust content accordingly
- **Archetype-agnostic**: Do not assume specific frameworks like Lambda, Next.js, Django, etc. Flexibly adapt based on the structure detected by discover_project.py
- **Respect existing skills**: Confirm overwrite when existing `/spec` or `/spec-maintenance` skills are found
- **Always generate specs**: Generate three-layer specs from the codebase regardless of whether specs already exist. Use existing specs as reference when available
- **Code is the source of truth**: All spec content is extracted from the codebase. Explicitly flag any sections filled by inference during user review
