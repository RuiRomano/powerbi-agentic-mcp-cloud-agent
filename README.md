# powerbi-agentic-mcp-cloud-agent

## Get started

- Click **Use this template** button, then select Create a new repository in your GitHub account
- Go to **Settings > Copilot > Cloud Agent** and configure the following JSON in **MCP configuration**
    ```json
        {
            "mcpServers": {
                "powerbi-modeling-mcp": {
                        "type": "stdio",
                        "command": "npx",
                        "args": [
                            "-y",
                            "@microsoft/powerbi-modeling-mcp",
                            "--start"                            
                        ],
                "tools": ["*"]
                }
            }
        }
    ```
- Click **Save MCP Configuration**
- 

## Acknowledgments

- [semantic-model-documentation skill](.github/skills/semantic-model-documentation/SKILL.md) was copied from [John Kerski](https://www.linkedin.com/in/john-kerski) repo [github-agentic-workflow-power-bi-mcp-example](https://github.com/clientfirsttech/github-agentic-workflow-power-bi-mcp-example/tree/main)
- [standardize-naming-conventions skill]() was copied from [Kurt Buhler](https://www.linkedin.com/in/kurtbuhler) repo [power-bi-agentic-development](https://github.com/data-goblin/power-bi-agentic-development/)