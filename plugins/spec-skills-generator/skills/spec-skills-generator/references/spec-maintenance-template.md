---
name: spec-maintenance
description: >
  Maintaining consistency between spec documents ({{SPEC_DIR}}) and code. Spec document update support.
  Code change impact analysis, spec section identification, {{DOCS_CHECK_COMMAND}} result interpretation and fixes.
  {{TRIGGER_KEYWORDS}}
---

# Spec Document Maintenance

## Overview

A skill for maintaining consistency between spec document files under `{{SPEC_DIR}}` and the codebase. Performs code change impact analysis → identifies affected spec document sections → presents update proposals → validates with `{{DOCS_CHECK_COMMAND}}`.

## Spec Document Structure

{{SPEC_STRUCTURE_TABLE}}

<!-- Generation notes:
  Table format:
  | File | Content | Key Sections |
  |------|---------|-------------|
  | `01_overview.md` | Overview | §1 ..., §2 ... |
  ...
  Auto-generated from heading structure analysis results
-->

## Code → Spec Impact Mapping

{{IMPACT_MAPPING_TABLE}}

<!-- Generation notes:
  Table format:
  | Change Target | Affected Spec Document | Section |
  |--------------|----------------------|---------|
  Analyze the source code directory structure and files,
  and map each source file/directory to the spec document sections it affects.
  If the mapping is unclear, map at the directory level as a rough approximation.
-->

## Workflow

### 1. Impact Analysis

When a code change is received, identify the affected spec document sections using the mapping above.

### 2. Divergence Detection

```bash
{{DOCS_CHECK_COMMAND}}
```

Interpret the output and target `[WARN]` items for correction.

### 3. Spec Document Update Checklist

- [ ] Numerical consistency: Do component counts match across spec document files?
- [ ] Terminology consistency: Are project-specific terms used correctly?
- [ ] Cross-reference integrity: Are references up to date?
- [ ] Change history: Has a line been added to the spec document's change history (if one exists)?
- [ ] Last verified date: Has the "last verified date" been updated to today's date in the updated spec document (if applicable)?

### 4. Update Pattern Guide

{{UPDATE_PATTERNS}}

<!-- Generation notes:
  List common update patterns based on the project structure. Examples:
  #### Adding a New Component
  1. Add to the component list in the overview file
  2. Add details to the technical spec
  3. Update cross-references

  #### Business Logic Changes
  1. Update the relevant section in the business spec
  2. If numerical values change, verify consistency across all files
-->

### 5. Interpreting `{{DOCS_CHECK_COMMAND}}` Output

| Output | Meaning | Action |
|--------|---------|--------|
| `[OK]` | Code and spec document match | No action needed |
| `[WARN]` Count mismatch | Component count differs between code and spec document | Update the spec document's list table |
| `[WARN]` Undocumented file | File exists in code but not in spec document | Add to spec document |
| `[WARN]` Last verified date exceeded | Spec document not updated in over 30 days | Review content and update last verified date |
