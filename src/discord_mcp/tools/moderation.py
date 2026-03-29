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
        name="bulk_delete_messages",
        description="Delete multiple messages at once from a channel (max 100, must be under 14 days old)",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "Channel ID containing the messages"},
                "message_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of message IDs to delete",
                },
                "reason": {"type": "string", "description": "Reason for deletion"},
            },
            "required": ["channel_id", "message_ids", "reason"],
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
        await message.delete()

        if arguments.get("timeout_minutes", 0) > 0 and isinstance(message.author, discord.Member):
            await message.author.timeout(
                datetime.timedelta(minutes=arguments["timeout_minutes"]),
                reason=arguments["reason"],
            )
            return [TextContent(type="text", text=f"Message deleted and user timed out for {arguments['timeout_minutes']} minutes.")]

        return [TextContent(type="text", text="Message deleted successfully.")]

    if name == "bulk_delete_messages":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        message_ids = [int(mid) for mid in arguments["message_ids"]]
        messages = [discord.Object(id=mid) for mid in message_ids]
        await channel.delete_messages(messages, reason=arguments.get("reason", "Bulk delete"))
        return [TextContent(type="text", text=f"Deleted {len(message_ids)} messages.")]

    if name == "test_reload":
        return [TextContent(type="text", text="MCP server is running.")]

    return None
