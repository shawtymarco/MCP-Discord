from __future__ import annotations

import datetime
from typing import Any, List

import discord
from mcp.types import TextContent, Tool

from discord_mcp.client import discord_client

TOOL_DEFINITIONS: List[Tool] = [
    Tool(
        name="moderate_message",
        description="Delete a message and optionally timeout the user",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "Channel ID containing the message"},
                "message_id": {"type": "string", "description": "ID of message to moderate"},
                "reason": {"type": "string", "description": "Reason for moderation"},
                "timeout_minutes": {"type": "number", "description": "Optional timeout duration in minutes"},
            },
            "required": ["channel_id", "message_id", "reason"],
        },
    ),
    Tool(
        name="test_reload",
        description="A test tool to verify if the MCP server has reloaded.",
        inputSchema={"type": "object", "properties": {}},
    ),
]


async def handle(name: str, arguments: Any) -> List[TextContent] | None:
    if name == "moderate_message":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        message = await channel.fetch_message(int(arguments["message_id"]))
        await message.delete(reason=arguments["reason"])

        if arguments.get("timeout_minutes", 0) > 0 and isinstance(message.author, discord.Member):
            await message.author.timeout(
                datetime.timedelta(minutes=arguments["timeout_minutes"]),
                reason=arguments["reason"],
            )
            return [TextContent(type="text", text=f"Message deleted and user timed out for {arguments['timeout_minutes']} minutes.")]

        return [TextContent(type="text", text="Message deleted successfully.")]

    if name == "test_reload":
        return [TextContent(type="text", text="MCP server is running.")]

    return None
