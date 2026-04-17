---
name: semantic-model-documentation
version: 0.1.0
description: Uses the Power BI Modeling MCP Server to generate professional documentation for each semantic model in the repository.
---

# Generate Power BI Semantic Model Documentation

You are a documentation agent. Your task is to generate professional Markdown documentation for each Power BI Semantic Model found in this repository.

## Instructions

1. **Discover semantic models**: Use bash to find all directories matching `*.SemanticModel` in the repository root.

2. **For each semantic model found**, connect to it using the Power BI Modeling MCP Server:
   - Use the `database_operations` tool to open the semantic model from the PBIP folder. The TMDL definition folder is at `<ModelName>.SemanticModel/definition` (e.g., `SampleModel.SemanticModel/definition`).

3. **Generate documentation**: For each connected semantic model, generate a Markdown document with the following sections:

   - **Title and Overview**: The name of the semantic model and a brief summary.
   - **Table Relationships**: Use a simple mermaid erDiagram to illustrate the table relationships. Use the `relationship_operations` tool to retrieve all relationships.
   - **Measures**: Document each measure including the DAX code and a description of the business logic using business friendly names. Use the `measure_operations` tool to list and get all measures.
   - **Row-Level Security**: Document any row-level filters defined in the model. Use the `security_role_operations` tool to check for RLS rules.
   - **Data Sources**: Document the data sources by analyzing the Power Query code. Use `table_operations` and `named_expression_operations` tools to retrieve partition sources and shared expressions.

4. **Save the documentation**: Use the `edit` tool to write the generated Markdown file as `<ModelName>.md` inside the `documentation/` directory at the repository root. For example, `documentation/SampleModel.md`.

5. **Commit the documentation**:
   - Before committing, use bash to check whether any documentation files actually changed: `git diff --quiet documentation/` -- if there are no changes, stop here and report that documentation is already up to date (do NOT attempt to push).
   - If there are changes, use `create-pull-request` to create a PR with the generated documentation files. Use the title `docs: auto-generated Power BI Semantic Model documentation` and include a body noting the documentation was auto-generated.

## Output Format

The generated Markdown document should follow this structure:

```markdown
# <Model Name> – Power BI Semantic Model Documentation

> *Auto-generated documentation.*

## Table of Contents
1. [Overview](#overview)
2. [Table Relationships](#table-relationships)
3. [Tables and Columns](#tables-and-columns)
4. [Measures](#measures)
5. [Row-Level Security](#row-level-security)
6. [Data Sources](#data-sources)

## Overview
Brief description of the model with a summary table (tables, relationships, measures count).

## Table Relationships
Mermaid erDiagram showing all relationships with cardinality.

## Tables and Columns
Each table with its columns, data types.

## Measures
Each measure with:
- Business-friendly name
- Description of the business logic
- DAX code in a fenced code block

## Row-Level Security
RLS roles and their filter expressions, or a note if none are defined.

## Data Sources
Each table's data source description derived from the Power Query M code.
```
