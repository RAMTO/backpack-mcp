"""
Backpack Exchange MCP Server

A Model Context Protocol server that exposes Backpack Exchange API functionality
for order management (list, create, cancel orders).

Phase 1: Minimal MCP server with test tool
"""

from mcp.server.fastmcp import FastMCP

# Create FastMCP server instance
# json_response=True ensures responses are in JSON format
mcp = FastMCP("Backpack Exchange", json_response=True)


@mcp.tool()
def hello_world(name: str = "World") -> dict:
    """
    A simple test tool to verify the MCP server is working.
    
    This is a placeholder tool for Phase 1 testing.
    Once verified, we'll add real Backpack API tools.
    
    Args:
        name: Name to greet (default: "World")
    
    Returns:
        Dictionary with a greeting message
    """
    return {"message": f"Hello, {name}!"}


if __name__ == "__main__":
    # Run the server using stdio transport
    # This allows local communication via stdin/stdout
    # No network exposure - safe for local usage
    mcp.run(transport="stdio")
