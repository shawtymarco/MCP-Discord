from __future__ import annotations

from typing import Any, List

from mcp.types import TextContent, Tool

from discord_mcp.client import discord_client

TOOL_DEFINITIONS: List[Tool] = [
    Tool(
        name="add_reaction",
        description="Add a reaction to a message",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "Channel containing the message"},
                "message_id": {"type": "string", "description": "Message to react to"},
                "emoji": {"type": "string", "description": "Emoji to react with (Unicode or custom emoji ID)"},
            },
            "required": ["channel_id", "message_id", "emoji"],
        },
    ),
    Tool(
        name="remove_reaction",
        description="Remove a reaction from a message",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "Channel containing the message"},
                "message_id": {"type": "string", "description": "Message to remove reaction from"},
                "emoji": {"type": "string", "description": "Emoji to remove"},
            },
            "required": ["channel_id", "message_id", "emoji"],
        },
    ),
]


async def handle(name: str, arguments: Any) -> List[TextContent] | None:
    if name == "add_reaction":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        message = await channel.fetch_message(int(arguments["message_id"]))
        await message.add_reaction(arguments["emoji"])
        return [TextContent(type="text", text=f"Added reaction {arguments['emoji']} to message")]

    if name == "remove_reaction":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        message = await channel.fetch_message(int(arguments["message_id"]))
        await message.remove_reaction(arguments["emoji"], discord_client.user)
        return [TextContent(type="text", text=f"Removed reaction {arguments['emoji']} from message")]

    return None
