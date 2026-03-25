from __future__ import annotations

from typing import Any, List

from mcp.types import TextContent, Tool

from discord_mcp.client import discord_client, format_dt

TOOL_DEFINITIONS: List[Tool] = [
    Tool(
        name="list_members",
        description="Get a list of members in a server",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server (guild) ID"},
                "limit": {"type": "number", "description": "Maximum number of members to fetch", "default": 100},
            },
            "required": ["server_id"],
        },
    ),
    Tool(
        name="list_roles",
        description="Get a list of all roles in a Discord server",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server (guild) ID"}
            },
            "required": ["server_id"],
        },
    ),
    Tool(
        name="inspect_role",
        description="Get detailed information about a specific role in a Discord server",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server (guild) ID"},
                "role_id": {"type": "string", "description": "Discord role ID"},
            },
            "required": ["server_id", "role_id"],
        },
    ),
    Tool(
        name="add_role",
        description="Add a role to a user",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server ID"},
                "user_id": {"type": "string", "description": "User to add role to"},
                "role_id": {"type": "string", "description": "Role ID to add"},
            },
            "required": ["server_id", "user_id", "role_id"],
        },
    ),
    Tool(
        name="remove_role",
        description="Remove a role from a user",
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {"type": "string", "description": "Discord server ID"},
                "user_id": {"type": "string", "description": "User to remove role from"},
                "role_id": {"type": "string", "description": "Role ID to remove"},
            },
            "required": ["server_id", "user_id", "role_id"],
        },
    ),
]


async def handle(name: str, arguments: Any) -> List[TextContent] | None:
    if name == "list_members":
        guild = discord_client.get_guild(int(arguments["server_id"]))
        if not guild:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        limit = arguments.get("limit", 100)
        members = []
        if not guild.members:
            async for member in guild.fetch_members(limit=limit):
                members.append(member)
        else:
            members = guild.members[:limit]
        member_list = [
            f"{m.name} (ID: {m.id}) - Roles: {', '.join(r.name for r in m.roles if r.name != '@everyone')}"
            for m in members
        ]
        return [TextContent(type="text", text=f"Members in {guild.name} (First {len(member_list)}):\n" + "\n".join(member_list))]

    if name == "list_roles":
        guild = discord_client.get_guild(int(arguments["server_id"]))
        if not guild:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        roles = sorted(
            [{"id": str(r.id), "name": r.name, "position": r.position} for r in guild.roles],
            key=lambda x: x["position"],
            reverse=True,
        )
        return [TextContent(
            type="text",
            text=f"Roles in {guild.name} ({len(roles)}):\n" +
                 "\n".join(f"{r['name']} (ID: {r['id']}, Position: {r['position']})" for r in roles),
        )]

    if name == "inspect_role":
        guild = discord_client.get_guild(int(arguments["server_id"]))
        if not guild:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        role = guild.get_role(int(arguments["role_id"]))
        if not role:
            return [TextContent(type="text", text="Role not found")]
        enabled_permissions = [perm[0] for perm in role.permissions if perm[1]]
        info = {
            "name": role.name,
            "id": str(role.id),
            "position": role.position,
            "color": str(role.color),
            "mentionable": role.mentionable,
            "hoist": role.hoist,
            "managed": role.managed,
            "permissions_value": str(role.permissions.value),
            "permissions_list": ", ".join(enabled_permissions) if enabled_permissions else "None",
            "created_at": format_dt(role.created_at),
        }
        return [TextContent(type="text", text=f"Role Information for '{role.name}':\n" + "\n".join(f"{k}: {v}" for k, v in info.items()))]

    if name == "add_role":
        guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        member = await guild.fetch_member(int(arguments["user_id"]))
        role = guild.get_role(int(arguments["role_id"]))
        await member.add_roles(role, reason="Role added via MCP")
        return [TextContent(type="text", text=f"Added role {role.name} to user {member.name}")]

    if name == "remove_role":
        guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        member = await guild.fetch_member(int(arguments["user_id"]))
        role = guild.get_role(int(arguments["role_id"]))
        await member.remove_roles(role, reason="Role removed via MCP")
        return [TextContent(type="text", text=f"Removed role {role.name} from user {member.name}")]

    return None
