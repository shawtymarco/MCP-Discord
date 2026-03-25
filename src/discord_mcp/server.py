from __future__ import annotations

import sys
import asyncio
import io
from typing import Any, List

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from discord_mcp.client import discord_client, DISCORD_TOKEN, require_discord_client
from discord_mcp.tools import ALL_TOOLS, route_tool


def _configure_windows_stdout_encoding():
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


_configure_windows_stdout_encoding()

app = Server("discord-mcp")


@app.list_tools()
async def list_tools() -> List[Tool]:
    return ALL_TOOLS


@app.call_tool()
@require_discord_client
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    return await route_tool(name, arguments)


async def main():
    asyncio.create_task(discord_client.start(DISCORD_TOKEN))
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
