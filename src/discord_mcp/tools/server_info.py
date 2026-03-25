from __future__ import annotations

from typing import Any, List

import discord
from mcp.types import TextContent, Tool

from discord_mcp.client import discord_client, format_dt

TOOL_DEFINITIONS: List[Tool] = [
    Tool(
        name="list_servers",
        description="Get a list of all Discord servers the bot has access to",
        inputSchema={"type": "object", "properties": {}},
    ),
    Tool(
        name="get_server_info",
        description="Get information about a Discord server",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server (guild) ID"}
            },
            "required": ["server_id"],
        },
    ),
    Tool(
        name="get_channels",
        description="Get a list of all channels in a Discord server",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server (guild) ID"}
            },
            "required": ["server_id"],
        },
    ),
    Tool(
        name="get_user_info",
        description="Get information about a Discord user",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Discord user ID"}
            },
            "required": ["user_id"],
        },
    ),
    Tool(
        name="create_role",
        description="Create a new role in a Discord server",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server ID"},
                "name": {"type": "string", "description": "Role name"},
                "color": {"type": "string", "description": "Hex color code e.g. #FF5733 (optional)"},
                "hoist": {"type": "boolean", "description": "Whether to display role separately in member list"},
                "mentionable": {"type": "boolean", "description": "Whether the role is mentionable"},
            },
            "required": ["server_id", "name"],
        },
    ),
    Tool(
        name="delete_role",
        description="Delete a role from a Discord server",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server ID"},
                "role_id": {"type": "string", "description": "Role ID to delete"},
                "reason": {"type": "string", "description": "Reason for deletion"},
            },
            "required": ["server_id", "role_id"],
        },
    ),
    Tool(
        name="rename_channel",
        description="Rename an existing channel",
        inputSchema={
            "type": "object",
            "properties": {
                "channel_id": {"type": "string", "description": "Channel ID to rename"},
                "name": {"type": "string", "description": "New channel name"},
            },
            "required": ["channel_id", "name"],
        },
    ),
]


async def handle(name: str, arguments: Any) -> List[TextContent]:
    if name == "list_servers":
        servers = [
            f"{g.name} (ID: {g.id}) - Members: {g.member_count}"
            for g in discord_client.guilds
        ]
        return [TextContent(type="text", text="Connected Servers:\n" + "\n".join(servers))]

    if name == "get_server_info":
        guild = discord_client.get_guild(int(arguments["server_id"]))
        if not guild:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        info = [
            f"Server Name: {guild.name}",
            f"ID: {guild.id}",
            f"Owner: {guild.owner}",
            f"Created At: {format_dt(guild.created_at)}",
            f"Member Count: {guild.member_count}",
            f"Verification Level: {guild.verification_level}",
            f"Roles: {len(guild.roles)}",
            f"Channels: {len(guild.channels)}",
        ]
        return [TextContent(type="text", text="\n".join(info))]

    if name == "get_channels":
        try:
            guild = discord_client.get_guild(int(arguments["server_id"]))
            if not guild:
                guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            channel_list = [
                f"#{c.name} (ID: {c.id}) - {c.type}" for c in guild.channels
            ]
            return [TextContent(
                type="text",
                text=f"Channels in {guild.name}:\n" + "\n".join(channel_list),
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {e}")]

    if name == "get_user_info":
        user_id = int(arguments["user_id"])
        user = discord_client.get_user(user_id)
        if not user:
            try:
                user = await discord_client.fetch_user(user_id)
            except discord.NotFound:
                return [TextContent(type="text", text="User not found")]
        info = [
            f"Username: {user.name}",
            f"Display Name: {user.display_name}",
            f"ID: {user.id}",
            f"Bot: {user.bot}",
            f"Created At: {format_dt(user.created_at)}",
        ]
        return [TextContent(type="text", text="\n".join(info))]

    if name == "create_role":
        guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        color = discord.Color.default()
        if "color" in arguments:
            hex_val = arguments["color"].lstrip("#")
            color = discord.Color(int(hex_val, 16))
        role = await guild.create_role(
            name=arguments["name"],
            color=color,
            hoist=arguments.get("hoist", False),
            mentionable=arguments.get("mentionable", False),
            reason="Role created via MCP",
        )
        return [TextContent(type="text", text=f"Created role '{role.name}' (ID: {role.id})")]

    if name == "delete_role":
        guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        role = guild.get_role(int(arguments["role_id"]))
        if not role:
            return [TextContent(type="text", text="Role not found")]
        await role.delete(reason=arguments.get("reason", "Deleted via MCP"))
        return [TextContent(type="text", text=f"Deleted role '{role.name}'")]

    if name == "rename_channel":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        await channel.edit(name=arguments["name"])
        return [TextContent(type="text", text=f"Renamed channel to '{arguments['name']}' (ID: {channel.id})")]

    return None
