# Copilot Cloud Agent Instructions

## Repository Overview

This repository contains Power BI projects (PBIP format) with semantic models and reports.

## Repository Structure

All source code lives inside the `src/` folder:

- `src/*.pbip` - Power BI project file
- `src/*.SemanticModel/` - Semantic model definition in TMDL format
- `src/*.Report/` - Report definition in PBIR format  

## MCP Server

This repository is configured to use the `@microsoft/powerbi-modeling-mcp` MCP server. Use its tools to interact with the semantic model programmatically.

To connect to a semantic model, use the `database_operations` tool with `ConnectFolder` operation pointing to the TMDL definition folder (e.g., `src/Sales.SemanticModel/definition`).

## Skills

The `.github/skills/` directory contains skill definitions that provide step-by-step workflows for common tasks. **Always read the relevant SKILL.md file before executing a task that matches a skill.**

### Available Skills

- **semantic-model-documentation** (`.github/skills/semantic-model-documentation/SKILL.md`): Generates professional Markdown documentation for Power BI semantic models. Use when asked to document a model, generate data dictionaries, or create model overviews. Outputs to `documentation/` directory.

- **standardize-naming-conventions** (`.github/skills/standardize-naming-conventions/SKILL.md`): Interactive workflow for auditing and fixing naming conventions across tables, columns, measures, and display folders. Use when asked to standardize names, fix abbreviations, clean up model names, or apply naming standards.

