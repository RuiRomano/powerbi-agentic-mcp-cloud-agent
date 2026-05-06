---
name: semantic-model-authoring
description: >
  Develops and manages Power BI semantic models across Desktop, PBIP projects,
  and Fabric Service. Handles (1) creating new models (Import, DirectQuery,
  Direct Lake), (2) editing measures, tables, columns, and relationships,
  (3) deploying models to Fabric workspaces, (4) working with PBIP project
  files, (5) refreshing semantic models, (6) configuring data sources and
  permissions, (7) DAX performance optimization. Supports both Power BI
  Desktop and Fabric Service development workflows.
  Does NOT handle report layout/visual authoring or workspace administration.
  Triggers: "create semantic model", "edit/develop semantic model", "add measure",
  "PBIP", "refresh semantic model", "semantic model authoring",
  "Direct Lake", "DAX optimization", "semantic model permissions".
---

# Power BI Semantic Model Authoring

## Workflow Selector

Use this decision tree to route to the correct workflow based on user intent:

| User wants to...                                           | Workflow                                                                             |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| Create a semantic model from scratch                       | [Build & Deploy a New Model](#workflow-build--deploy-a-new-model)                    |
| Add/edit measures, tables, columns, relationships          | [Modify an Existing Model](#workflow-modify-an-existing-model)                       |
| Write or refactor DAX code, create UDFs                    | [Modify an Existing Model](#workflow-modify-an-existing-model)                       |
| Improve DAX query or measure performance                              | [Optimize DAX Performance](#workflow-optimize-dax-performance)                       |
| Analyze semantic model against best practices              | [Analyze Best Practices](#workflow-analyze-best-practices)                           |
| Deploy a model to a Fabric workspace                       | [Deploy to Fabric](#workflow-deploy-to-fabric)                                       |
| Refresh a semantic model                                   | [Refresh Semantic Model](#workflow-refresh-semantic-model)                            |
| Configure data sources, parameters, or permissions         | [Manage Semantic Model in Fabric](#workflow-manage-semantic-model-in-fabric)          |

## Reference Index

Load these references on demand when a workflow step requires them. Do not load all at once.

| Topic                      | Reference                                                                             | When to load                                   |
| -------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------- |
| Modeling Best Practices    | [modeling-guidelines.md](./references/modeling-guidelines.md)                         | Before creating or editing any model            |
| Naming Conventions         | [naming-conventions.md](./references/naming-conventions.md)                           | When naming or renaming tables, columns, measures |
| Direct Lake Modeling       | [direct-lake-guidelines.md](./references/direct-lake-guidelines.md)                   | When model connects to OneLake                  |
| TMDL Editing               | [tmdl-guidelines.md](./references/tmdl-guidelines.md)                                 | Before generating or editing any TMDL file           |
| PBIP Projects              | [pbip.md](./references/pbip.md)                                                       | When working with PBIP folders                  |
| DAX Language               | [dax-guidelines.md](./references/dax-guidelines.md)                                   | When writing or reviewing any DAX code          |
| DAX Performance            | [dax-performance-optimization.md](./references/dax-performance-optimization.md)       | When optimizing DAX                             |
| Semantic Model REST API    | [semantic-model-rest-api.md](./references/semantic-model-rest-api.md)                 | When using `az rest` for TMDL CRUD, refresh, parameters, permissions, or property retrieval |
| Finding Workspaces/Items   | [COMMON-CLI.md](../../common/COMMON-CLI.md#finding-workspaces-and-items-in-fabric)    | When resolving workspace/item IDs               |
| Fabric Control-Plane API   | [COMMON-CLI.md](../../common/COMMON-CLI.md#fabric-control-plane-api-via-az-rest)      | When using `az rest` patterns, LRO, pagination  |
| Authentication             | [COMMON-CLI.md](../../common/COMMON-CLI.md#authentication-recipes)                    | When authenticating with `az login`             |
| Definition Envelope        | [ITEM-DEFINITIONS-CORE.md](../../common/ITEM-DEFINITIONS-CORE.md#semanticmodel)       | When building TMDL definition payloads          |

---

## Tool Selection Priority

> **All workflows below are tool-agnostic.** Workflow steps describe the *intent* (connect, create, edit, save, deploy, refresh). The tool used to perform each step is determined here. Always select the highest-priority tool available for the current environment; do not mix tools when a higher-priority option works.

> **What "MCP available" means:** MCP is "available" when the `powerbi-modeling-mcp` server is **registered and callable** in the current session — i.e., its tools appear in the tool list. It is **NOT** a function of whether there are pre-existing live connections. An empty `list_connections` result does **not** mean MCP is unavailable; it just means no model is connected yet. In that case, use MCP to **open** the PBIP folder, Desktop instance, or Fabric workspace model — do not fall back to Tier 2/3.
>
> Only fall back to Tier 2/3/4 when MCP itself is **not registered, errors on every call, or the user explicitly opts out**.

Priority order (highest first):

1. **Tier 1 — `powerbi-modeling-mcp` MCP is registered** -> Use MCP for all operations (create, edit, query) against any source: live Desktop instance, Fabric workspace model, **or local PBIP folder** (open it via MCP's connect/open-folder operation). If no model is currently connected, MCP's role is to **establish** that connection — not to be skipped. Unless the user specifically requests working directly with TMDL files.
2. **Tier 2 — MCP not registered + PBIP folder exists** -> Edit TMDL files directly. Load [tmdl-guidelines.md](./references/tmdl-guidelines.md) and [pbip.md](./references/pbip.md).
3. **Tier 3 — MCP not registered + Fabric workspace** -> Use `az rest` (load [semantic-model-rest-api.md](./references/semantic-model-rest-api.md)): getDefinition -> edit TMDL -> updateDefinition.
4. **Tier 4 — MCP not registered + Power BI Desktop** -> Guide user to save as PBIP or enable MCP server.

> **Workflow-specific overrides:** Some workflows OVERRIDE this default priority. In particular, [Deploy to Fabric](#workflow-deploy-to-fabric) requires the Fabric REST API (not MCP) when the source is PBIP/TMDL files on disk, even if MCP is available. Always check the workflow's own tool-selection rules before defaulting to Tier 1.

### Connecting to a Semantic Model

A semantic model can live in three locations. Resolve the connection per [Tool Selection Priority](#tool-selection-priority):

- **Power BI Desktop**: Locate the running Desktop instance and connect to its local model.
- **Fabric workspace**: First, find the workspace and semantic model using the [Finding Workspaces and Items](../../common/COMMON-CLI.md#finding-workspaces-and-items-in-fabric) pattern: list workspaces to resolve the workspace ID by name, then list items of type `SemanticModel` in that workspace to resolve the model ID by name. Then connect to the model (live) or export its TMDL definition for local editing.
- **PBIP project**: Connect to the `[Name].SemanticModel/definition` folder. Load [pbip.md](./references/pbip.md) to understand the PBIP folder structure - only load the `[Name].SemanticModel/definition` folder that includes the TMDL code.

### Saving Changes to a Semantic Model

How changes are persisted depends on where the model lives and which tool tier (per [Tool Selection Priority](#tool-selection-priority)) is in use:

**Live connection (Tier 1 - MCP against Desktop or Fabric workspace):**

- Changes are applied immediately as each operation executes against the live model. No explicit save step is needed.
- **PBIP project (live via MCP)**: Serialize the model back to the `[Name].SemanticModel/definition` folder at the end of the session. If the PBIP folder does not exist yet, follow [Export to PBIP](#workflow-export-to-pbip) to create the full structure first.

**Local TMDL editing (Tiers 2 & 3 - direct file edits or `az rest` round-trip):**

- **PBIP project**: Changes are already written to the TMDL files during editing. No additional save step is needed.
- **Fabric workspace**: Changes were made to local TMDL files exported from the service. Re-deploy the model (load [semantic-model-rest-api.md](./references/semantic-model-rest-api.md) for the `updateDefinition` flow) to push changes back to the workspace.

---

## Workflow: Build & Deploy a New Model

**When this applies:** User asks to create a new semantic model from scratch.

### Phase 1 - Requirements & Design

1. **Gather requirements** - interview the user until both reach a shared understanding of: purpose of the model, data source information and schemas, and key business entities/facts.
2. **Analyze source schema** - inspect the source tables, columns, and data types. It's critical to understand the data before designing the model. **If data source information is not available (e.g., no connection details, no schema, no tables identified), STOP and ask the user to provide it before proceeding.** Do not guess or fabricate data source details. 
3. **Determine storage mode:**
   - Data source is Fabric OneLake -> **Direct Lake** (follow the [Direct Lake path](#direct-lake-path) below)
   - Otherwise -> **Import or DirectQuery mode** (follow the [Import or DirectQuery path](#import-or-directquery-path) below)
4. **Design star schema** - identify fact and dimension tables, define relationship keys. 

### Phase 2 - Build

#### Import or DirectQuery path

Load [modeling-guidelines.md](./references/modeling-guidelines.md) before starting.

1. **Create database** - create a new empty semantic model database with compatibility level 1702 or higher.
2. **Create data source parameters** - create semantic model M parameters for the data sources (`Server`, `Database`, etc.), and use them in the partition M code.
3. **Create tables** - add partitions with correct source type, create columns with proper data types and `sourceColumn` mapping.
4. **Create relationships** - define relationships between fact and dimension tables before creating measures.
5. **Create measures** - add explicit measures for aggregatable columns. 

#### Direct Lake path

Load [modeling-guidelines.md](./references/modeling-guidelines.md) and [direct-lake-guidelines.md](./references/direct-lake-guidelines.md) before starting.

1. **Create database** - create a new empty semantic model database with compatibility level 1702 or higher.
2. **Create the named expression** - create a shared named expression for the Direct Lake connection using `AzureStorage.DataLake` connector.
3. **Create tables** - using the schema from the lakehouse, add semantic model tables using `EntityPartitionSource` with `directLake` mode. Map columns to the OneLake table columns.
4. **Create relationships and measures** - follow [modeling-guidelines.md](./references/modeling-guidelines.md).

### Phase 3 - Deploy & Validate

1. **Deploy or save** - determine the target:
   - **Fabric workspace available** -> follow [Deploy to Fabric](#workflow-deploy-to-fabric).
   - **No workspace available / user wants local files** -> follow [Export to PBIP](#workflow-export-to-pbip) to save the model as a PBIP project.
   - See [Saving Changes to a Semantic Model](#saving-changes-to-a-semantic-model) for how persistence works in each context.
2. **Validate** - run [Validation Checklist](#validation-checklist).

---

## Workflow: Modify an Existing Model

**When this applies:** User asks to add/edit/remove measures, tables, columns, relationships, write DAX code, refactor with UDFs, or edit TMDL directly.

### Phase 1 - Connect & Discover

1. **Connect to the model** - determine the source (PBIP folder, Desktop, Fabric workspace) and connect per [Connecting to a Semantic Model](#connecting-to-a-semantic-model).
2. **Discover the current state** - before any changes, always gather context:
   - List all tables
   - List existing relationships to map the current star schema
   - List existing measures to avoid duplicates and understand calculation patterns   
   - Identify model storage mode - this dictates which guidelines apply
3. **Determine applicable guidelines:**
   - Any model -> load [modeling-guidelines.md](./references/modeling-guidelines.md)
   - Direct Lake model -> load [direct-lake-guidelines.md](./references/direct-lake-guidelines.md)   
   - TMDL editing needed -> load [tmdl-guidelines.md](./references/tmdl-guidelines.md)
   - DAX code needed -> load [dax-guidelines.md](./references/dax-guidelines.md)
   - Refactoring with UDFs -> load [dax-guidelines.md](./references/dax-guidelines.md) and review the *DAX User-Defined Functions* section. Create the UDF, then refactor existing measures to call it.

### Phase 2 - Plan & Execute

1. **Plan changes** - based on the user request, identify exactly what needs to be added, modified, or removed. Check for naming conflicts and duplicates.
2. **Execute changes** - apply modifications following the correct ordering:
   - **Adding tables:** create partitions first, then columns, then relationships, then measures.
   - **Adding measures:** verify referenced columns/tables exist, test with a simple DAX query.
   - **Adding relationships:** ensure key columns exist on both sides with matching data types.
   
### Phase 3 - Validate & Save

1. **Validate** - run [Validation Checklist](#validation-checklist).
2. **Save** - follow [Saving Changes to a Semantic Model](#saving-changes-to-a-semantic-model) based on the current working context.

---

## Workflow: Optimize DAX Performance

**When this applies:** User asks to improve DAX query performance, diagnose slow measures, or optimize calculations.

> **Hard requirement:** This workflow requires Tier 1 (MCP Server connected to the target semantic model) because trace diagnostics are only available through MCP. Other tiers cannot satisfy this workflow.

Load [dax-performance-optimization.md](./references/dax-performance-optimization.md) and follow the complete framework defined there. The framework includes:

1. Tier model for categorizing optimization effort
2. Trace diagnostics to identify bottlenecks
3. Pattern catalog with proven optimization techniques

---

## Workflow: Analyze Best Practices

**When this applies:** User asks to review, audit, or analyze a semantic model against best practices.

### Phase 1 - Connect & Inventory

1. **Connect to the model** - follow [Connecting to a Semantic Model](#connecting-to-a-semantic-model) to locate and connect.
2. **Inventory the model** - List all tables, columns, relationships, measures, and storage modes. Build a complete picture of the current state.

### Phase 2 - Analyze Against Best Practices

1. **Load modeling guidelines** - read [modeling-guidelines.md](./references/modeling-guidelines.md) in full.
2. **Load storage-specific guidelines** - if the model uses Direct Lake, also load [direct-lake-guidelines.md](./references/direct-lake-guidelines.md).
3. **Evaluate the model** - compare the current implementation against the guidelines, checking:
   - Star schema design (fact vs dimension tables, relationship keys)
   - Consistent Naming conventions (tables, columns, measures)
   - Relationship cardinality and cross-filter direction
   - Measure patterns (explicit measures, `formatString`, no implicit measures)
   - Column data types and `sourceColumn` mappings
   - Hidden columns used only in relationships
   - Appropriate use of calculated columns vs measures
   - Direct Lake constraints (if applicable)

### Phase 3 - Propose & Apply Changes

1. **Present findings** - summarize issues found, grouped by severity (critical, recommended, optional). Include the best-practice rule being violated and the proposed fix for each.
2. **Wait for user approval** - do not apply changes until the user confirms which fixes to apply.
3. **Execute approved changes** - apply fixes following the [Modify an Existing Model](#workflow-modify-an-existing-model) workflow.
4. **Save** - follow [Saving Changes to a Semantic Model](#saving-changes-to-a-semantic-model) based on the current working context.
5. **Validate** - run [Validation Checklist](#validation-checklist).

---

## Workflow: Export to PBIP

**When this applies:** User asks to export or save a semantic model to a PBIP project folder, or there is no Fabric workspace available to deploy to (e.g., after building a model in-memory).

> **Key fact:** Exporting a model only produces the TMDL definition files. It does NOT create the surrounding PBIP folder structure. The agent must ensure the full PBIP structure exists before exporting.

Load [pbip.md](./references/pbip.md) before starting.

### Step 1 - Determine the target PBIP folder

1. Ask the user for the target folder path and the semantic model name (e.g., `Sales`).
2. If the user provides only a folder, use the model's database name as the semantic model folder name.

### Step 2 - Ensure the PBIP folder structure exists

A PBIP cannot be opened in Power BI Desktop with only a semantic model folder - it requires a Report folder with a `byPath` reference to the model. Before exporting any TMDL, verify (and create if missing) the full PBIP scaffolding:

```text
<TargetFolder>/
├── <Name>.SemanticModel/
|   ├── definition/          # <- TMDL export target
|   └── definition.pbism     # <- Must be created by the agent
├── <Name>.Report/
|   ├── definition/          # <- Empty folder for report definition
|   └── definition.pbir      # <- Must be created with byPath reference to the semantic model
└── <Name>.pbip              # <- Must be created as the Desktop entry point
```

1. **Create the `<Name>.SemanticModel/` folder** if it does not exist.
2. **Create the `<Name>.SemanticModel/definition/` folder** if it does not exist.
3. **Create `<Name>.SemanticModel/definition.pbism`** with the standard content.
4. **Create the `<Name>.Report/` folder** if it does not exist.
5. **Create the `<Name>.Report/definition/` folder** if it does not exist.
6. **Create `<Name>.Report/definition.pbir`** with a `byPath` reference pointing to the semantic model folder.

### Step 3 - Export TMDL to the definition folder

Serialize the model's TMDL files into the `<Name>.SemanticModel/definition/` folder. Per [Tool Selection Priority](#tool-selection-priority):

- **Tier 1 (MCP)**: Use the MCP export/save operation against the live model.
- **Tier 3 (Fabric workspace, no MCP)**: Call `getDefinition` (load [semantic-model-rest-api.md](./references/semantic-model-rest-api.md)) and write the returned TMDL parts to the `definition/` folder.
- **Local TMDL files already on disk**: Copy or move them into the `definition/` folder.

### Step 4 - Validate

1. Verify the `definition/` folder contains the expected TMDL files (at minimum: `model.tmdl` and one or more table `.tmdl` files).
2. Verify `definition.pbism` exists with correct content.
3. Verify `<Name>.Report/definition.pbir` exists with the correct `byPath` reference to `../<Name>.SemanticModel`.
4. Verify `<Name>.pbip` exists and points to `<Name>.Report`.

---

## Workflow: Deploy to Fabric

**When this applies:** User asks to deploy or publish a semantic model to a Fabric workspace.

> **Hard rule — this workflow OVERRIDES the default [Tool Selection Priority](#tool-selection-priority).** Do not default to MCP just because it is available. The deployment path is determined by the **source of the model**, not by which tools are connected. If the source is PBIP/TMDL files on disk, you **MUST** use the Fabric REST API even when an MCP session is active.

Decision tree (pick exactly one — top-down, first match wins):

1. **Are there PBIP / TMDL files on disk that need to be deployed?**
   -> **YES — use Fabric REST API.** Call `az rest` with `createItemWithDefinition` (new model) or `updateDefinition` (existing model). Load [semantic-model-rest-api.md](./references/semantic-model-rest-api.md).
   - Rationale: deploying TMDL files directly via the Fabric API is more reliable, faster, and avoids unnecessarily loading the model into MCP only to push it back out.
   - **Do NOT** open the PBIP in MCP first and then deploy via MCP. That is an explicit anti-pattern for this workflow.
2. **Is the model already loaded in a live `powerbi-modeling-mcp` session** (e.g., just built in-memory, or currently being edited via MCP) **with no PBIP/TMDL files involved?**
   -> Use MCP `database_operations` Deploy with the target workspace and semantic model name.
3. **Is the model live in Power BI Desktop with no PBIP saved?**
   -> Use MCP Deploy if MCP is connected to Desktop. If MCP is not available, instruct the user to save as PBIP first, then restart this workflow at step 1.

Verify deployment succeeded by listing workspace items of type `SemanticModel`.

---

## Workflow: Refresh Semantic Model

**When this applies:** User asks to refresh data in a semantic model.

Refresh is only possible when working against a live model in Desktop or Fabric Service. If working with local TMDL files, deploy the model first.

Trigger a refresh per [Tool Selection Priority](#tool-selection-priority):

- **Power BI Desktop**: Tier 1 (MCP) only — use the MCP Refresh operation.
- **Fabric Service**: Tier 1 (MCP Refresh operation) or fallback to the Power BI Enhanced Refresh API (load [semantic-model-rest-api.md](./references/semantic-model-rest-api.md)).

If the refresh fails with a credential error, **stop immediately** and instruct the user to configure the data source connections manually in Power BI Service. Do not attempt to retry or work around credential errors programmatically.

---

## Workflow: Manage Semantic Model in Fabric

**When this applies:** User asks to configure data sources, update parameters, or manage permissions for a semantic model in Fabric Service.

### Data Sources & Parameters

Get/update data sources and parameters via Power BI REST API. Load [semantic-model-rest-api.md](./references/semantic-model-rest-api.md#4-data-sources--parameters-power-bi-datasets-api).

### Permissions

List/grant/update dataset user permissions via Power BI REST API. Load [semantic-model-rest-api.md](./references/semantic-model-rest-api.md#5-permissions-power-bi-datasets-api).

---

## Validation Checklist

Run after any model creation or modification:

**Always (works with PBIP, Desktop, and Fabric Service):**

1. **Check the PBIP structure** - if the model is sourced from a PBIP folder, ensure the folder structure and files are correct (see [pbip.md](./references/pbip.md)).
2. **Verify relationships** - for new relationships, confirm cardinality, cross-filter direction, and that key columns have matching data types.
3. **Verify table columns** - for new tables, confirm all columns have correct `sourceColumn` mapping and `dataType`.
4. **Check for duplicates** - ensure no duplicate measures (same DAX expression) or orphan objects were introduced.

**Only when connected to an Analysis Services database (Power BI Desktop or Fabric Service):**

5. **Test new measures** - for each new measure, run a simple DAX query to validate it returns expected results (e.g., `EVALUATE { [Measure Name] }`). Skip this step when working with local TMDL/PBIP files only.
6. **Test table refresh** - when new tables were created, trigger a refresh to verify that partitions, data source expressions, and column mappings are correct. A failed refresh typically indicates mismatched `sourceColumn` names, invalid M expressions, or incorrect Direct Lake entity references. Skip this step when working with local TMDL/PBIP files only.

If any check fails, fix the issue and re-run validation.

---

## Must/Prefer/Avoid

### MUST

- **Understand the data source schema before starting** - analyze source tables, columns, and data types before designing or modifying the model.
- **Follow modeling guidelines** - load [modeling-guidelines.md](./references/modeling-guidelines.md) before creating or editing any model; apply star schema design, naming conventions, and column/measure rules
- **Follow [Tool Selection Priority](#tool-selection-priority)** - always pick the highest-priority tool tier available for the current environment; do not mix tiers when a higher-priority option works
  
### PREFER

- **Star schema over snowflake or flat tables** - denormalized dimensions with single-column relationship keys
- **Consistency with existing model patterns** - when editing an existing model, match its naming conventions and structure rather than imposing new ones
- **TMDL format over TMSL** - text-based, diff-friendly, preferred for Fabric

### AVOID

- **Hardcoded workspace/item IDs** - resolve dynamically via API

---

## TROUBLESHOOTING

| Symptom                              | Fix                                                                                                                   |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| MCP connection failure               | Fall back to TMDL editing (see Tool Selection Priority). Inform the user about the fallback.                          |
| TMDL validation errors               | Read error details, fix syntax, re-validate. Load [tmdl-guidelines.md](./references/tmdl-guidelines.md).              |
| `403 Forbidden` / `identity None`    | User needs Contributor+ role - stop immediately. Do not retry.                                                        |
| `401 Unauthorized`                   | Wrong `--resource` audience or missing permissions to the item. Check [semantic-model-rest-api.md](./references/semantic-model-rest-api.md). |
| `202 Accepted` but no result         | Poll LRO to completion.                                                                                               |
| Parts missing after updateDefinition | Must include ALL parts - modified + unmodified.                                                                       |
| Refresh credential error             | Direct user to configure in Service portal. Do not retry.                                                             |
| DAX errors in measures               | Check column/table name references (case-sensitive). Verify referenced objects exist.                                 |
| Deployment failure                   | Check workspace permissions, model compatibility level, and Direct Lake expression source references.                 |
| Missing data source                  | Verify M parameters or named expressions are correctly defined.                                                       |
