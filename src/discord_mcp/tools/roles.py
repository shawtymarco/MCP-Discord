from __future__ import annotations

from typing import Any, List

from mcp.types import TextContent, Tool

from discord_mcp.client import discord_client

TOOL_DEFINITIONS: List[Tool] = [
    Tool(
        name="reorder_roles",
        description=(
            "Reorder roles in a Discord server. "
            "Provide a list of role_id + position pairs to set new positions. "
            "Position 1 is the lowest (above @everyone). Higher numbers = higher in the list. "
            "You do not need to include every role — only the ones you want to move."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "server_id": {
                    "type": "string",
                    "description": "Discord server (guild) ID",
                },
                "positions": {
                    "type": "array",
                    "description": "List of role position assignments",
                    "items": {
                        "type": "object",
                        "properties": {
                            "role_id": {"type": "string", "description": "Role ID to move"},
                            "position": {"type": "number", "description": "New position (1 = lowest above @everyone)"},
                        },
                        "required": ["role_id", "position"],
                    },
                },
            },
            "required": ["server_id", "positions"],
        },
    ),
]


async def handle(name: str, arguments: Any) -> List[TextContent] | None:
    if name == "reorder_roles":
        guild = discord_client.get_guild(int(arguments["server_id"]))
        if not guild:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))

        # Force-fetch all roles to populate cache
        all_roles = await guild.fetch_roles()
        role_map = {r.id: r for r in all_roles}

        positions = arguments["positions"]

        role_positions: dict[Any, int] = {}
        not_found: list[str] = []

        for entry in positions:
            role = role_map.get(int(entry["role_id"]))
            if not role:
                not_found.append(entry["role_id"])
                continue
            role_positions[role] = int(entry["position"])

        if not_found:
            return [TextContent(
                type="text",
                text=f"Role(s) not found: {', '.join(not_found)}",
            )]

        await guild.edit_role_positions(
            positions=role_positions,
            reason="Role positions updated via MCP",
        )

        result_lines = [f"Role positions updated in '{guild.name}':"]
        for role, pos in role_positions.items():
            result_lines.append(f"  {role.name} (ID: {role.id}) → position {pos}")

        return [TextContent(type="text", text="\n".join(result_lines))]

    return None
