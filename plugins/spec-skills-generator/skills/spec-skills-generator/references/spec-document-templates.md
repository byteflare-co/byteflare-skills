# Specification Document Templates — 3-Layer Structure Guide

This template serves as a guide for Claude to analyze a project's codebase and generate specification documents.
It defines the section structure and "what to write." Specific content is extracted from the project's actual code.

---

## Common Metadata

Include the following at the beginning and end of each file.

**Header:**
```markdown
# {project_name} Specification — {subtitle}

> Last updated: YYYY-MM-DD
> Related: [01_overview.md](./01_overview.md) | [02_business_spec.md](./02_business_spec.md) | [03_technical_spec.md](./03_technical_spec.md)
```

- `Last updated`: The date when the spec document content was last modified

**Footer:**
```markdown
---

## Change History

| Date | Description | Commit |
|------|-------------|--------|
| YYYY-MM-DD | Initial creation | — |

> Last verified: YYYY-MM-DD
```

- `Last verified`: The date when consistency between the spec document and code was last confirmed (check_spec_drift.py uses this date for the 30-day check)
- On initial generation, set both `Last updated` and `Last verified` to the generation date

---

## 01_overview.md — Overview

Subtitle: `Overview`

### §1 Project Overview

| Subsection | Content | Format |
|------------|---------|--------|
| 1.1 Business Context | Business problem the project solves, stakeholders | Text |
| 1.2 Related Systems | List of external systems/services and their roles | Table |
| 1.3 Role of This System | Bullet list of key capabilities (4–6 items) | Bullet list |
| 1.4 Related Repositories | For multi-repo setups: role, technology, and path of each repo | Table + detailed description |

**What to write in §1:**
- Description of the business domain (who the system serves and what it does)
- Related systems and the data flows between them
- Clear definition of this repository's responsibilities

### §2 System Architecture

| Subsection | Content | Format |
|------------|---------|--------|
| 2.1 Overall Architecture Diagram | System components and their connections | **Mermaid diagram** |
| 2.2 Data Flow Overview | Major data flows (direction, frequency, trigger) | Table or bullet list |
| 2.3 Process Flow Diagrams | Sequences for representative use cases | **Mermaid sequence diagram** |

**What to write in §2:**
- Component architecture diagram (Mermaid `graph` or `flowchart`)
- Data flow direction, frequency, and trigger conditions
- Sequence diagrams for 1–3 key use cases

### §3 Component Inventory

| Subsection | Content | Format |
|------------|---------|--------|
| 3.1–3.N By functional category | Component name, description, source path | Table (category heading + count) |

**What to write in §3:**
- List components by functional category in tables (e.g., API functions, shared modules, data models, IaC, etc.)
- Include the count in each category heading (e.g., `### 3.1 Lambda Functions (10)`)
- Auto-count from code and record the exact number

**Classification guidelines** (derived from discover_project.py detection results):
- `entry_points` → API endpoints / batch jobs / CLI commands, etc. (classified by directory structure)
- `shared_modules` → Shared modules / libraries
- IaC → Infrastructure resources (DB/storage/compute, etc.)
- Use exact counts derived from code for each category

### §4 Glossary

| Subsection | Content | Format |
|------------|---------|--------|
| 4.1 Domain Terms | Terms specific to the business domain | Table (term, description) |
| 4.2 Technical Terms & Abbreviations | Technical abbreviations and project-specific naming | Table (term, full name, description) |

**What to write in §4:**
- Extract all domain-specific terms used in the code
- Full names for abbreviations and acronyms

### §5 Environment Configuration

| Subsection | Content | Format |
|------------|---------|--------|
| 5.1 Environment List | dev/staging/production, etc. | Table |
| 5.2 Runtime Settings | Language versions, frameworks | Table |
| 5.3 Parameters & Secrets | Environment variables, SSM parameters, secrets | Table (values redacted) |

### §6 Documentation Structure

| Subsection | Content | Format |
|------------|---------|--------|
| 6.1 Spec Document Files | Structure of this spec document set and target audience | Table |
| 6.2 Maintenance Process | Update rules, consistency check procedures | Text + command examples |

---

## 02_business_spec.md — Business Specification

Subtitle: `Business Specification`

### §1 Domain Model

| Subsection | Content | Format |
|------------|---------|--------|
| 1.1 Core Entities | Central domain concepts and classifications | Table (classification, criteria, behavior) |
| 1.2 State Transitions | Entity lifecycle | Text or **Mermaid state diagram** |
| 1.3 Flow Overview | Overview of major business flows | Numbered list + conditional branches |

**What to write in §1:**
- Core domain entities and their classifications (categories, types, etc.)
- Criteria and behavioral differences for each classification
- State transitions if applicable

### §2–N Feature-Specific Business Specifications

Allocate one section per feature. Use the following structure as a baseline:

| Subsection | Content | Format |
|------------|---------|--------|
| N.1 Overview & Types | Purpose of the feature, data classifications | Table |
| N.2 Process Flow | Trigger → processing steps → result | Numbered list + conditional branches |
| N.3 Business Rules | Decision criteria, thresholds, edge cases | Table or **pseudocode** |
| N.4 Data Examples | Concrete input/output examples | **JSON code block** |

**What to write in each feature section:**
- Use cases (who, when, what triggers it, what happens)
- Detailed processing steps (including branch conditions)
- Business rules (express decision logic as pseudocode)
- Concrete data examples (JSON format)
- Error cases and handling

**Example feature sections (varies by project):**
- Point synchronization, member rank determination, birthday point grants, guaranteed rank exceptions, legacy EC site payment amounts, monthly batch processing, etc.

### §X Time-Bound Rules List (only if applicable)

```markdown
| # | Rule | Removal Date | Action | Related Files |
|---|------|-------------|--------|---------------|
```

**What to write in §X:**
- Temporary business rules or processes with migration deadlines
- Removal date and required actions upon removal
- Omit this section entirely if not applicable

---

## 03_technical_spec.md — Technical Specification

Subtitle: `Technical Specification`

**Section applicability conditions** (omit sections that don't meet the criteria, and renumber remaining sections sequentially):

| Section | Applicability |
|---------|--------------|
| §1 API Specification | When API endpoints exist (for CLI tools, can be reframed as "Command Interface", etc.) |
| §2 External Integrations | When external service integrations exist |
| §3 Data Model | Applicable to virtually all projects |
| §4 Implementation Modules | Applicable to virtually all projects |
| §5 Infrastructure Configuration | When IaC files exist |
| §6 Cross-Reference Matrix | Applicable to virtually all projects |

### §1 API Specification

| Subsection | Content | Format |
|------------|---------|--------|
| 1.1 Common Specifications | Protocol, authentication method, response format | Table + JSON code example |
| 1.2–1.N Per Endpoint | Path, method, parameters, response, process flow, errors | Table + numbered list |

**What to write in §1:**
- Common specifications (protocol, authentication, response structure, CORS, etc.)
- Authentication methods table
- For each endpoint:
  - Source file path
  - Request parameters (table: field/type/required/description)
  - Process flow (numbered list)
  - Response (status code/condition/payload)
  - Error codes

### §2 External Integration Interfaces

| Subsection | Content | Format |
|------------|---------|--------|
| 2.1–2.N Per Client | Authentication method, API list, error codes, retry strategy | Table + code examples |

**What to write in §2:**
- One subsection per external API client
- Authentication method details (token generation, encryption method, etc.)
- List of key methods (method name/SCODE/description/parameters)
- Error code list
- Retry and timeout strategy

### §3 Data Model

| Subsection | Content | Format |
|------------|---------|--------|
| 3.1 DB Schema | Table definitions (PK/SK/attributes/GSI/TTL) | Table |
| 3.2 Repository Methods | List of CRUD operations | Table (method name/operation/target table) |
| 3.3 Type & Model Definitions | Pydantic/TypeScript type definitions, etc. | Table or code block |

**What to write in §3:**
- Definitions for all tables/collections/schemas
- Index definitions (GSI/LSI, etc.) and their purposes
- TTL settings
- Repository pattern method list
- Application-layer type definitions

### §4 Implementation Module Details

| Subsection | Content | Format |
|------------|---------|--------|
| 4.1 Business Logic Layer | Use cases, service classes | Table (module/class/responsibility/dependencies) |
| 4.2 Infrastructure Layer | DB/API/external integration clients | Table |

**What to write in §4:**
- List separately for business logic layer and infrastructure layer
- Responsibilities and dependencies for each module

### §5 Infrastructure Configuration

| Subsection | Content | Format |
|------------|---------|--------|
| 5.1 Compute Resources | Lambda/ECS/EC2 settings, etc. | Table (resource name/runtime/memory/timeout) |
| 5.2 API Gateway | Routing, authentication settings | Table |
| 5.3 DB/Storage | Tables/buckets/caches | Table |
| 5.4 Other | Step Functions/EventBridge/SQS, etc. | Table |
| 5.5 CI/CD | Deployment pipeline | Text or table |

**What to write in §5:**
- Extract from IaC files (Terraform/CDK/CloudFormation, etc.)
- If no IaC exists, infer from configuration files or README
- Omit subsections that don't apply

### §6 Cross-Reference Matrix

| Subsection | Content | Format |
|------------|---------|--------|
| 6.1 Feature ↔ Source Files | Mapping between feature names and source files | Table |
| 6.2 Source Files ↔ Test Files | Mapping between implementation and test files | Table |

**What to write in §6:**
- Mapping of features (business spec sections) ↔ source files
- Mapping of source files ↔ test files
- Overview of test coverage

---

## Notes for Generation

1. **Extract from code**: The template structure is a guide; all actual content must be extracted from the codebase
2. **Omit inapplicable sections**: Not all sections are required. Do not create sections that don't apply to the project
3. **Use sequential section numbers**: Do not skip numbers even when sections are omitted
4. **Always include Mermaid diagrams**: Include at least one architecture diagram in §2
5. **Use tables extensively**: Markdown tables should be the primary format for spec documents
6. **Use concrete paths and values**: Write actual file paths and configuration values, not placeholders
7. **Component counts must be accurate**: Counts in §3 must be exact numbers auto-counted from code
