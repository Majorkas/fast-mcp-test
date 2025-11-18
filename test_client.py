import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:8080/sse") as client:
        await client.ping()
        tools = await client.list_tools()
        print("Tools:", [tool.name for tool in tools])

        result = await client.call_tool("echo", {"text": "pie", "upper": True})
        print(result.content[0].text) #type: ignore


asyncio.run(main())
