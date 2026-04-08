---
name: spec
description: >
  Q&A about product specifications. Answers questions by referencing spec document files under {{SPEC_DIR}}.
  {{TRIGGER_KEYWORDS}}
allowed-tools: Read, Grep, Glob, AskUserQuestion
---

# Spec Document Q&A

## Overview

A skill that references spec document files under `{{SPEC_DIR}}` to answer any questions about the product specification.

### Operating Modes

- **`/spec <question>`**: Determines the topic and reads the relevant spec document to answer
- **`/spec` (no arguments)**: Uses AskUserQuestion to ask the user what they want to know

## Spec Map

Based on the question topic, read the corresponding file/section from the mapping table below. **If the question spans multiple topics, read all related files.**

{{SPEC_MAP}}

<!-- Generation notes:
  - For each spec document file, analyze the heading structure (H2/H3/H4)
    and create a topic-to-section mapping table
  - Express topic names using keywords that users would naturally use when asking questions
  - Table format: | Topic | Section |
-->

## Response Guidelines

1. **Cite your sources**: Always indicate the source file name and section number in your answer
2. **Quote spec documents accurately**: Base answers on what is written in the spec documents, not on speculation
3. **Be explicit about missing information**: If the question is not covered by the spec documents, state "This is not documented in the spec documents" and suggest checking the code
4. **Be concise**: Focus on the scope of the question. Extract information that directly answers the question rather than reading out entire related sections
5. **Be precise with numbers and thresholds**: Quote numerical values from spec documents exactly
6. **Use tables when helpful**: Use table format when it makes the answer clearer

## Workflow

### With arguments (`/spec <question>`)

1. Determine the topic from the question
2. Based on the "Spec Map" above, Read the relevant section(s) from the corresponding file(s)
3. If multiple files are involved, read them in parallel
4. Answer based on the spec document content (following the guidelines)

### Without arguments (`/spec`)

Use AskUserQuestion to ask the user what they want to know:

```
Question: What would you like to know about the spec documents?
Options:
{{ASK_OPTIONS}}
- (Free text input)
```

## Spec Document File Paths

{{SPEC_FILES_TABLE}}

<!-- Generation notes:
  Table format:
  | File | Path |
  |------|------|
  | Overview | `docs/specification/01_overview.md` |
  ...
-->
