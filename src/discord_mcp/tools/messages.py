from __future__ import annotations

from typing import Any, List

import discord
from mcp.types import TextContent, Tool

from discord_mcp.client import discord_client, format_dt

TOOL_DEFINITIONS: List[Tool] = [
    Tool(
        name="send_message",
        description="Send a message to a specific channel",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "Discord channel ID"},
                "content": {"type": "string", "description": "Message content"},
            },
            "required": ["channel_id", "content"],
        },
    ),
    Tool(
        name="read_messages",
        description="Read recent messages from a channel",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "Discord channel ID"},
                "limit": {"type": "number", "description": "Number of messages to fetch (max 1000)", "default": 50},
            },
            "required": ["channel_id"],
        },
    ),
    Tool(
        name="read_thread_messages",
        description="Read recent messages from a thread attached to a message",
        inputSchema={
            "type": "object",
            "properties": {
                "thread_id": {"type": "string", "description": "Discord thread ID (same as the message ID that started the thread)"},
                "limit": {"type": "number", "description": "Number of messages to fetch (max 1000)", "default": 50},
            },
            "required": ["thread_id"],
        },
    ),
]


def _format_reactions(reactions: list) -> str:
    parts = []
    for r in reactions:
        if r.get("is_custom"):
            parts.append(f":{r['emoji_name']}: (ID: {r['emoji_id']}, Count: {r['count']})")
        else:
            parts.append(f"{r['emoji']} ({r['count']})")
    return ", ".join(parts)


def _collect_reactions(message: discord.Message) -> list:
    reactions = []
    for reaction in message.reactions:
        emoji_data: dict = {"emoji": str(reaction.emoji), "count": reaction.count, "me": reaction.me}
        if isinstance(reaction.emoji, (discord.PartialEmoji, discord.Emoji)):
            emoji_data["is_custom"] = True
            emoji_data["emoji_id"] = str(reaction.emoji.id) if reaction.emoji.id else None
            emoji_data["emoji_name"] = reaction.emoji.name
            emoji_data["animated"] = getattr(reaction.emoji, "animated", False)
        else:
            emoji_data["is_custom"] = False
        reactions.append(emoji_data)
    return reactions


async def _fetch_messages(channel, limit: int) -> list:
    messages = []
    batch_size = 100
    last_message_id = None
    remaining = limit

    while remaining > 0:
        fetch_count = min(remaining, batch_size)
        kwargs: dict = {"limit": fetch_count}
        if last_message_id:
            kwargs["before"] = discord.Object(id=last_message_id)

        batch = [msg async for msg in channel.history(**kwargs)]
        if not batch:
            break

        last_message_id = batch[-1].id
        remaining -= len(batch)
        messages.extend(batch)

    return messages


async def handle(name: str, arguments: Any) -> List[TextContent] | None:
    if name == "send_message":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        message = await channel.send(arguments["content"])
        return [TextContent(type="text", text=f"Message sent successfully. Message ID: {message.id}")]

    if name == "read_messages":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        limit = min(int(arguments.get("limit", 50)), 1000)
        raw_messages = await _fetch_messages(channel, limit)

        output = [f"Retrieved {len(raw_messages)} messages:"]
        for message in raw_messages:
            reactions = _collect_reactions(message)
            thread_info = None
            if hasattr(message, "thread") and message.thread is not None:
                t = message.thread
                thread_info = {"id": str(t.id), "name": t.name, "message_count": t.message_count, "archived": t.archived}

            msg_text = f"{message.author} ({format_dt(message.created_at)}): {message.content}"
            msg_text += f"\n  ID: {message.id}"

            if reactions:
                msg_text += f"\n  Reactions: {_format_reactions(reactions)}"

            for i, embed in enumerate(message.embeds):
                msg_text += f"\n  [Embed {i + 1}]"
                if embed.title:
                    msg_text += f"\n    Title: {embed.title}"
                if embed.description:
                    msg_text += f"\n    Description: {embed.description}"
                for field in embed.fields:
                    msg_text += f"\n    Field: {field.name} = {field.value}"

            if message.attachments:
                msg_text += f"\n  Attachments: {', '.join(str(a.url) for a in message.attachments)}"

            if thread_info:
                archived = " [archived]" if thread_info["archived"] else ""
                msg_text += f"\n  Thread: {thread_info['name']} (ID: {thread_info['id']}, Messages: {thread_info['message_count']}{archived})"

            msg_text += f"\n  Type: {message.type}"
            output.append(msg_text)

        return [TextContent(type="text", text="\n\n".join(output))]

    if name == "read_thread_messages":
        thread = await discord_client.fetch_channel(int(arguments["thread_id"]))
        if not isinstance(thread, discord.Thread):
            return [TextContent(type="text", text=f"Error: Channel {arguments['thread_id']} is not a thread.")]

        limit = min(int(arguments.get("limit", 50)), 1000)
        raw_messages = await _fetch_messages(thread, limit)

        output = [f"Thread: {thread.name} (ID: {thread.id}) — Retrieved {len(raw_messages)} messages:"]
        for message in raw_messages:
            reactions = _collect_reactions(message)
            msg_text = f"{message.author} ({format_dt(message.created_at)}): {message.content}"
            msg_text += f"\n  ID: {message.id}"
            if reactions:
                msg_text += f"\n  Reactions: {_format_reactions(reactions)}"
            if message.attachments:
                msg_text += f"\n  Attachments: {', '.join(str(a.url) for a in message.attachments)}"
            output.append(msg_text)

        return [TextContent(type="text", text="\n\n".join(output))]

    return None
