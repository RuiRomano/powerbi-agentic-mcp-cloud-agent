"""
Deployment script for publishing PBIP artifacts to Microsoft Fabric.

Workspace resolution logic (in precedence order)
===============================================

1) Explicit CLI override (highest priority)
    - If `--workspace_name` is provided, that value is always used.

2) `.env` file in current working directory
    - If `--workspace_name` is not provided, the script reads `.env` from CWD
      and resolves `PBI_WORKSPACE_<ENV>`.

3) `deploy.config` file alongside this script
    - If CWD `.env` does not provide a value, the script reads
      `scripts/deploy.config` (same format as `.env`) and resolves
      `PBI_WORKSPACE_<ENV>`.

4) Fail due to missing configuration
    - If no value is found in any source, execution fails with a clear error.
"""

import argparse
import sys
from pathlib import Path
from azure.identity import InteractiveBrowserCredential, AzureCliCredential
from dotenv import dotenv_values
from fabric_cicd import FabricWorkspace, publish_all_items


def _read_env_file(file_path: Path) -> dict[str, str]:
    if not file_path.exists():
        return {}

    parsed_values = dotenv_values(file_path)
    return {
        key: value.strip()
        for key, value in parsed_values.items()
        if key and value and value.strip()
    }


def resolve_workspace_name(explicit_workspace_name: str | None, environment_name: str) -> str:
        normalized_workspace_name = (explicit_workspace_name or "").strip()
        if normalized_workspace_name:
                return normalized_workspace_name

        if not environment_name:
            print(
                "Unable to resolve workspace because environment is missing. "
                "Provide --environment or set a default in argument parsing.",
                file=sys.stderr,
            )
            sys.exit(1)

        env_var_name = f"PBI_WORKSPACE_{environment_name}"

        deploy_config_path = Path(__file__).resolve().with_name("deploy.config")
        deploy_config_values = _read_env_file(deploy_config_path)
        workspace_name = deploy_config_values.get(env_var_name)
        if workspace_name:
            return workspace_name

        print(
            f"Unable to resolve workspace for environment '{environment_name}'. "
            f"Provide --workspace_name, or define {env_var_name} in "
            f"{deploy_config_path}.",
            file=sys.stderr,
        )
        sys.exit(1)


parser = argparse.ArgumentParser(description="Deploy PBIP to Fabric")
parser.add_argument("--workspace_name", type=str, required=False, help="Target workspace name")
parser.add_argument("--environment", type=str, default="DEV", help="Environment name (default: DEV)")
parser.add_argument("--spn-auth", type=bool, default=False, help="Use SPN authentication")
args = parser.parse_args()

resolved_environment = ((args.environment or "").strip().upper() or "DEV")
resolved_workspace_name = resolve_workspace_name(args.workspace_name, resolved_environment)

# Authentication (SPN or Interactive)

if (not args.spn_auth):
    credential = InteractiveBrowserCredential()
else:
    # Check current login: az account show
    credential = AzureCliCredential()

workspace_params = {
    "workspace_name": resolved_workspace_name,
    "environment": resolved_environment,
    "repository_directory": "./src",
    "item_type_in_scope": ["SemanticModel", "Report"],
    "token_credential": credential,
}

print(f"Deployment environment: {resolved_environment}", flush=True)
print(f"Target workspace: {resolved_workspace_name}", flush=True)

target_workspace = FabricWorkspace(**workspace_params)

publish_all_items(target_workspace)