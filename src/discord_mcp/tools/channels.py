from __future__ import annotations

from typing import Any, List

import discord
from mcp.types import TextContent, Tool

from discord_mcp.client import discord_client, format_dt

TOOL_DEFINITIONS: List[Tool] = [
    Tool(
        name="inspect_channel",
        description="Get detailed information about a channel, including permission overwrites",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server (guild) ID"},
                "channel_id": {"type": "string", "description": "Discord channel ID"},
            },
            "required": ["server_id", "channel_id"],
        },
    ),
    Tool(
        name="get_audit_log",
        description="Get recent audit log entries from the server",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server (guild) ID"},
                "limit": {"type": "number", "description": "Number of entries to fetch (max 100)", "minimum": 1, "maximum": 100},
                "action_type": {"type": "string", "description": "Optional filter for action type (e.g. 'member_update', 'message_delete')"},
            },
            "required": ["server_id"],
        },
    ),
    Tool(
        name="create_category",
        description="Create a new category channel",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server ID"},
                "name": {"type": "string", "description": "Category name"},
            },
            "required": ["server_id", "name"],
        },
    ),
    Tool(
        name="create_text_channel",
        description="Create a new text channel",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server ID"},
                "name": {"type": "string", "description": "Channel name"},
                "category_id": {"type": "string", "description": "Optional category ID to place channel in"},
                "topic": {"type": "string", "description": "Optional channel topic"},
            },
            "required": ["server_id", "name"],
        },
    ),
    Tool(
        name="create_voice_channel",
        description="Create a new voice channel",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server ID"},
                "name": {"type": "string", "description": "Channel name"},
                "category_id": {"type": "string", "description": "Optional category ID to place channel in"},
                "user_limit": {"type": "number", "description": "Optional user limit (0 = unlimited)"},
            },
            "required": ["server_id", "name"],
        },
    ),
    Tool(
        name="delete_channel",
        description="Delete a channel",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "ID of channel to delete"},
                "reason": {"type": "string", "description": "Reason for deletion"},
            },
            "required": ["channel_id"],
        },
    ),
]


async def handle(name: str, arguments: Any) -> List[TextContent] | None:
    if name == "inspect_channel":
        try:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            channel = await guild.fetch_channel(int(arguments["channel_id"]))
            overwrites = []
            for target, overwrite in channel.overwrites.items():
                target_type = "Role" if isinstance(target, discord.Role) else "Member"
                allow = [perm[0] for perm in overwrite if perm[1] is True]
                deny = [perm[0] for perm in overwrite if perm[1] is False]
                if allow or deny:
                    overwrites.append(
                        f"\n  {target_type} '{target.name}':\n"
                        f"    Allowed: {', '.join(allow) or 'None'}\n"
                        f"    Denied: {', '.join(deny) or 'None'}"
                    )
            info = {
                "name": channel.name,
                "id": str(channel.id),
                "type": str(channel.type),
                "category": channel.category.name if channel.category else "None",
                "position": channel.position,
                "created_at": format_dt(channel.created_at),
            }
            if isinstance(channel, discord.TextChannel):
                info["topic"] = channel.topic or "None"
                info["nsfw"] = channel.nsfw
                info["slowmode_delay"] = f"{channel.slowmode_delay}s"
            elif isinstance(channel, discord.VoiceChannel):
                info["bitrate"] = f"{channel.bitrate / 1000}kbps"
                info["user_limit"] = channel.user_limit or "Unlimited"
                info["connected_members"] = ", ".join(f"{m.name} ({m.display_name})" for m in channel.members) or "None"
            return [TextContent(
                type="text",
                text=f"Channel Information for '#{channel.name}':\n" +
                     "\n".join(f"{k}: {v}" for k, v in info.items()) +
                     f"\n\nPermission Overwrites:{''.join(overwrites) if overwrites else ' None'}",
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error inspecting channel: {e}")]

    if name == "get_audit_log":
        try:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            limit = min(int(arguments.get("limit", 20)), 100)
            action_type = arguments.get("action_type")
            entries = []
            async for entry in guild.audit_logs(limit=limit):
                if action_type and action_type.lower() not in str(entry.action).lower():
                    continue
                entries.append(
                    f"[{format_dt(entry.created_at)}] {entry.user.name}: "
                    f"{str(entry.action).replace('AuditLogAction.', '')} -> {entry.target}"
                )
            return [TextContent(type="text", text=f"Audit Log (Last {len(entries)} entries):\n" + "\n".join(entries))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching audit log: {e}")]

    if name == "create_category":
        guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        category = await guild.create_category(
            name=arguments["name"],
            reason="Category created via MCP",
        )
        return [TextContent(type="text", text=f"Created category '{category.name}' (ID: {category.id})")]

    if name == "create_text_channel":
        guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        category = None
        if "category_id" in arguments:
            category = guild.get_channel(int(arguments["category_id"]))
        channel = await guild.create_text_channel(
            name=arguments["name"],
            category=category,
            topic=arguments.get("topic"),
            reason="Channel created via MCP",
        )
        return [TextContent(type="text", text=f"Created text channel #{channel.name} (ID: {channel.id})")]

    if name == "create_voice_channel":
        guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        category = None
        if "category_id" in arguments:
            category = guild.get_channel(int(arguments["category_id"]))
        channel = await guild.create_voice_channel(
            name=arguments["name"],
            category=category,
            user_limit=int(arguments.get("user_limit", 0)),
            reason="Voice channel created via MCP",
        )
        return [TextContent(type="text", text=f"Created voice channel #{channel.name} (ID: {channel.id})")]

    if name == "delete_channel":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        await channel.delete(reason=arguments.get("reason", "Channel deleted via MCP"))
        return [TextContent(type="text", text="Deleted channel successfully")]

    return None
