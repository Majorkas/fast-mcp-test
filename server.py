from fastmcp import FastMCP

mcp = FastMCP("echo-server", version="2025-03-26")

@mcp.tool(description="Echo text back with optional casing tweaks")
def echo(text: str, upper: bool = False) -> str:
    """Return the submitted text."""
    return text.upper() if upper else text

@mcp.tool
def word_count(text: str) -> int:
    """Count characters separated by whitespace."""
    return len(text.split())

@mcp.tool
def add(a: int , b: int) -> int:
    """adds two int together"""
    return a + b

if __name__ == "__main__":
    mcp.run()  # Use stdio transport for gateway integration
