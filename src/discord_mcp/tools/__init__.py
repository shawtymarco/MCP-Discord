from __future__ import annotations

from typing import Any, List

from mcp.types import TextContent, Tool

from discord_mcp.tools import channels, members, messages, moderation, reactions, roles, server_info

ALL_TOOLS: List[Tool] = (
    server_info.TOOL_DEFINITIONS
    + members.TOOL_DEFINITIONS
    + channels.TOOL_DEFINITIONS
    + messages.TOOL_DEFINITIONS
    + reactions.TOOL_DEFINITIONS
    + moderation.TOOL_DEFINITIONS
    + roles.TOOL_DEFINITIONS
)

_MODULES = [server_info, members, channels, messages, reactions, moderation, roles]


async def route_tool(name: str, arguments: Any) -> List[TextContent]:
    for module in _MODULES:
        result = await module.handle(name, arguments)
        if result is not None:
            return result
    raise ValueError(f"Unknown tool: {name}")
