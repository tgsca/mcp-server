# GET THE PARAMETERS
MCP_SERVER_NAME=$1

uv init $MCP_SERVER_NAME
cd $MCP_SERVER_NAME

# RESTRUCTURE THE PROJECT
echo "MCP_SERVER_NAME=$MCP_SERVER_NAME" > .env
mkdir src
mv main.py src/
touch src/__init__.py
rm -rf .git

# CREATE THE MCP SERVER
uv add ruff httpx "mcp[cli]" python-dotenv

# REPLACE SPACES IN MCP_SERVER_NAME WITH DASHES
MCP_SERVER_NAME_JSON_FRIENDLY=$(echo $MCP_SERVER_NAME | tr ' ' '-')
CURRENT_DIR=$(pwd)

# FINISH
echo """
Done! You can now start the MCP server with 'uv run mcp'

Configuration:
´´´json
{
    "mcpServers": {
        "$MCP_SERVER_NAME_JSON_FRIENDLY": {
            "command": "uv",
            "args": [
                "--directory",
                "$CURRENT_DIR/src",
                "run",
                "main.py"
            ]
        }
    }
}
´´´
"""
