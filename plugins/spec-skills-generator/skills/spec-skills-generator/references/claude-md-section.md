# CLAUDE.md Additional Section Template

Add the following template to your project's CLAUDE.md.
Replace `{{...}}` placeholders with project-specific values.

---

## Spec Document Maintenance

When changing code, update the affected spec document sections at the same time.

### Code → Spec Impact Mapping

{{IMPACT_MAPPING_TABLE}}

<!-- Generation notes:
  Table format:
  | Changed file | Affected spec | Section |
  |---------|--------------|-----------|
  | `src/...` | overview.md | §X Section name |
  ...
  Use the same content as the spec-maintenance skill mapping
-->

### Update Rules

1. **When adding or changing features**: Follow the mapping above to update the relevant sections
2. **When deleting**: Remove the corresponding description from the spec and update cross-reference matrices
3. **Commit messages**: Include a `docs:` prefix when spec documents are updated
4. **When unsure**: Run `{{DOCS_CHECK_COMMAND}}` to check for drift
