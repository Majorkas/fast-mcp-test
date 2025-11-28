from fastmcp import FastMCP
from statistics import mean
import operator
from duckduckgo_search import DDGS

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
def math(a: float, b: float, op: str) -> float:
    """Perform mathematical operations. Operator can be: +, -, *, /, //, %, **"""
    ops = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '//': operator.floordiv,
        '%': operator.mod,
        '**': operator.pow
    }

    if op not in ops:
        raise ValueError(f"Invalid operator: {op}. Use: +, -, *, /, //, %, **")

    return ops[op](a, b)

@mcp.tool
def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=max_results))

    output = []
    for result in results:
        output.append(f"Title: {result['title']}\nURL: {result['href']}\nSnippet: {result['body']}\n")

    return "\n".join(output)

if __name__ == "__main__":
    mcp.run()  # Use stdio transport for gateway integration
