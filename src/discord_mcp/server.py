from __future__ import annotations
import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Any, List
from functools import wraps
import discord
from discord.ext import commands
from mcp.server import Server
from mcp.types import Tool, TextContent, Resource
from mcp.server.stdio import stdio_server

def _configure_windows_stdout_encoding():
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

_configure_windows_stdout_encoding()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord-mcp-server")

# Helper function to format datetime
def format_dt(dt: datetime) -> str:
    """Format datetime to readable string"""
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

# Discord bot setup
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")

class DiscordMCPClient(discord.Client):
    def __init__(self):
        # Enable privileged intents for fetching server members and message content
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

discord_client = DiscordMCPClient()
app = Server("discord-mcp")

@app.list_resources()
async def list_resources() -> List["Resource"]:
    """List available Discord resources."""
    return []

@app.read_resource()
async def read_resource(uri: Any) -> str:
    """Read a specific Discord resource."""
    raise ValueError(f"Resource not found: {uri}")

@app.list_tools()
async def list_tools() -> List["Tool"]:
    """List available Discord tools."""
    return [
        Tool(
            name="list_servers",
            description="Get a list of all Discord servers the bot has access to",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        # Server Information Tools
        Tool(
            name="get_server_info",
            description="Get information about a Discord server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    }
                },
                "required": ["server_id"]
            }
        ),
        Tool(
            name="get_channels",
            description="Get a list of all channels in a Discord server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    }
                },
                "required": ["server_id"]
            }
        ),
        Tool(
            name="get_user_info",
            description="Get information about a Discord user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "Discord user ID"
                    }
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="list_members",
            description="Get a list of members in a server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of members to fetch",
                        "default": 100
                    }
                },
                "required": ["server_id"]
            }
        ),
        Tool(
            name="list_roles",
            description="Get a list of all roles in a Discord server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    }
                },
                "required": ["server_id"]
            }
        ),
        Tool(
            name="inspect_role",
            description="Get detailed information about a specific role in a Discord server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    },
                    "role_id": {
                        "type": "string",
                        "description": "Discord role ID"
                    }
                },
                "required": ["server_id", "role_id"]
            }
        ),
        Tool(
            name="inspect_channel",
            description="Get detailed information about a channel, including permission overwrites",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    },
                    "channel_id": {
                        "type": "string",
                        "description": "Discord channel ID"
                    }
                },
                "required": ["server_id", "channel_id"]
            }
        ),
        Tool(
            name="get_audit_log",
            description="Get recent audit log entries from the server",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server (guild) ID"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Number of entries to fetch (max 100)",
                        "minimum": 1,
                        "maximum": 100
                    },
                    "action_type": {
                        "type": "string",
                        "description": "Optional filter for action type (e.g. 'member_update', 'message_delete')"
                    }
                },
                "required": ["server_id"]
            }
        ),

        # Role Management Tools
        Tool(
            name="add_role",
            description="Add a role to a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server ID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User to add role to"
                    },
                    "role_id": {
                        "type": "string",
                        "description": "Role ID to add"
                    }
                },
                "required": ["server_id", "user_id", "role_id"]
            }
        ),
        Tool(
            name="remove_role",
            description="Remove a role from a user",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server ID"
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User to remove role from"
                    },
                    "role_id": {
                        "type": "string",
                        "description": "Role ID to remove"
                    }
                },
                "required": ["server_id", "user_id", "role_id"]
            }
        ),

        # Channel Management Tools
        Tool(
            name="create_text_channel",
            description="Create a new text channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_id": {
                        "type": "string",
                        "description": "Discord server ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "Channel name"
                    },
                    "category_id": {
                        "type": "string",
                        "description": "Optional category ID to place channel in"
                    },
                    "topic": {
                        "type": "string",
                        "description": "Optional channel topic"
                    }
                },
                "required": ["server_id", "name"]
            }
        ),
        Tool(
            name="delete_channel",
            description="Delete a channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "ID of channel to delete"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for deletion"
                    }
                },
                "required": ["channel_id"]
            }
        ),

        # Message Tools
        Tool(
            name="send_message",
            description="Send a message to a specific channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Discord channel ID"
                    },
                    "content": {
                        "type": "string",
                        "description": "Message content"
                    }
                },
                "required": ["channel_id", "content"]
            }
        ),
        Tool(
            name="read_messages",
            description="Read recent messages from a channel",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Discord channel ID"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Number of messages to fetch (max 100)",
                        "default": 50
                    }
                },
                "required": ["channel_id"]
            }
        ),
        
        # Reaction Tools
        Tool(
            name="add_reaction",
            description="Add a reaction to a message",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Channel containing the message"
                    },
                    "message_id": {
                        "type": "string",
                        "description": "Message to react to"
                    },
                    "emoji": {
                        "type": "string",
                        "description": "Emoji to react with (Unicode or custom emoji ID)"
                    }
                },
                "required": ["channel_id", "message_id", "emoji"]
            }
        ),
        
        # Moderation Tools
        Tool(
            name="moderate_message",
            description="Delete a message and optionally timeout the user",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "Channel ID containing the message"
                    },
                    "message_id": {
                        "type": "string",
                        "description": "ID of message to moderate"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for moderation"
                    },
                    "timeout_minutes": {
                        "type": "number",
                        "description": "Optional timeout duration in minutes"
                    }
                },
                "required": ["channel_id", "message_id", "reason"]
            }
        )
    ]

# Helper to verify Discord client connectivity
def require_discord_client(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not discord_client.is_ready():
            # Try to wait a bit for connection
            try:
                await asyncio.wait_for(discord_client.wait_until_ready(), timeout=5.0)
            except asyncio.TimeoutError:
                pass
                
        if not discord_client.is_ready():
             return [TextContent(
                type="text",
                text="Error: Discord client is not connected. Please check your BOT_TOKEN."
            )]
        return await func(*args, **kwargs)
    return wrapper

@app.call_tool()
@require_discord_client
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """Handle Discord tool calls."""
    if name == "list_servers":
        servers = []
        for guild in discord_client.guilds:
            servers.append(f"{guild.name} (ID: {guild.id}) - Members: {guild.member_count}")
        return [TextContent(
            type="text",
            text="Connected Servers:\n" + "\n".join(servers)
        )]

    elif name == "send_message":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        message = await channel.send(arguments["content"])
        return [TextContent(
            type="text",
            text=f"Message sent successfully. Message ID: {message.id}"
        )]

    elif name == "read_messages":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        limit = min(int(arguments.get("limit", 50)), 100)
        messages = []
        async for message in channel.history(limit=limit):
            messages.append({
                "id": str(message.id),
                "author": str(message.author),
                "content": message.content,
                "timestamp": format_dt(message.created_at),
            })
            
        return [TextContent(
            type="text",
            text=f"Retrieved {len(messages)} messages:\n\n" + 
                 "\n".join([
                     f"{m['author']} ({m['timestamp']}): {m['content']}"
                     for m in messages
                 ])
        )]

    elif name == "get_user_info":
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
            f"Created At: {format_dt(user.created_at)}"
        ]
        return [TextContent(type="text", text="\n".join(info))]

    elif name == "moderate_message":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        message = await channel.fetch_message(int(arguments["message_id"]))
        
        # Delete the message
        await message.delete(reason=arguments["reason"])
        
        # Handle timeout if specified
        if "timeout_minutes" in arguments and arguments["timeout_minutes"] > 0:
            if isinstance(message.author, discord.Member):
                duration = arguments["timeout_minutes"]
                # Discord timeout expects a timedelta object
                timeout_duration = datetime.timedelta(minutes=duration)
                await message.author.timeout(
                    timeout_duration,
                    reason=arguments["reason"]
                )
                return [TextContent(
                    type="text",
                    text=f"Message deleted and user timed out for {arguments['timeout_minutes']} minutes."
                )]
        
        return [TextContent(
            type="text",
            text="Message deleted successfully."
        )]

    # Server Information Tools
    elif name == "get_server_info":
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
            f"Channels: {len(guild.channels)}"
        ]
        return [TextContent(type="text", text="\n".join(info))]

    elif name == "get_channels":
        try:
            guild = discord_client.get_guild(int(arguments["server_id"]))
            if not guild:
                guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            
            channel_list = []
            for channel in guild.channels:
                channel_list.append(f"#{channel.name} (ID: {channel.id}) - {channel.type}")
            
            return [TextContent(
                type="text", 
                text=f"Channels in {guild.name}:\n" + "\n".join(channel_list)
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error: {str(e)}")]

    elif name == "list_members":
        guild = discord_client.get_guild(int(arguments["server_id"]))
        if not guild:
            # Note: list_members might fail if privileged intents are not enabled
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            
        limit = arguments.get("limit", 100)
        members = []
        
        # async interator for large lists if needed, but guild.members is cached if intents enabled
        # If cache is empty, we might need fetch_members
        if not guild.members:
            async for member in guild.fetch_members(limit=limit):
                members.append(member)
        else:
             members = guild.members[:limit]

        member_list = []
        for m in members:
            roles = [r.name for r in m.roles if r.name != "@everyone"]
            member_list.append(f"{m.name} (ID: {m.id}) - Roles: {', '.join(roles)}")
            
        return [TextContent(
            type="text",
            text=f"Members in {guild.name} (First {len(member_list)}):\n" + "\n".join(member_list)
        )]

    elif name == "list_roles":
        guild = discord_client.get_guild(int(arguments["server_id"]))
        if not guild:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            
        roles = []
        for role in guild.roles:
            roles.append({
                "id": str(role.id),
                "name": role.name,
                "position": role.position
            })
        
        # Sort by position descending (highest role first)
        roles.sort(key=lambda x: x['position'], reverse=True)
        
        return [TextContent(
            type="text",
            text=f"Roles in {guild.name} ({len(roles)}):\n" + 
                 "\n".join(f"{r['name']} (ID: {r['id']}, Position: {r['position']})" for r in roles)
        )]

    elif name == "inspect_role":
        guild = discord_client.get_guild(int(arguments["server_id"]))
        if not guild:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            
        role = guild.get_role(int(arguments["role_id"]))
        if not role:
            return [TextContent(type="text", text="Role not found")]

        # Get enabled permissions
        enabled_permissions = [perm[0] for perm in role.permissions if perm[1]]
            
        role_info = {
            "name": role.name,
            "id": str(role.id),
            "position": role.position,
            "color": str(role.color),
            "mentionable": role.mentionable,
            "hoist": role.hoist,
            "managed": role.managed,
            "permissions_value": str(role.permissions.value),
            "permissions_list": ", ".join(enabled_permissions) if enabled_permissions else "None",
            "created_at": format_dt(role.created_at)
        }
        
        return [TextContent(
            type="text",
            text=f"Role Information for '{role.name}':\n" + 
                 "\n".join(f"{k}: {v}" for k, v in role_info.items())
        )]

    elif name == "inspect_channel":
        try:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            channel = await guild.fetch_channel(int(arguments["channel_id"]))
            
            overwrites = []
            for target, overwrite in channel.overwrites.items():
                target_type = "Role" if isinstance(target, discord.Role) else "Member"
                target_name = target.name
                
                allow = [perm[0] for perm in overwrite if perm[1] is True]
                deny = [perm[0] for perm in overwrite if perm[1] is False]
                
                if allow or deny:
                    overwrites.append(f"\n  {target_type} '{target_name}':\n    Allowed: {', '.join(allow) or 'None'}\n    Denied: {', '.join(deny) or 'None'}")

            info = {
                "name": channel.name,
                "id": str(channel.id),
                "type": str(channel.type),
                "category": channel.category.name if channel.category else "None",
                "position": channel.position,
                "created_at": format_dt(channel.created_at)
            }
            
            if isinstance(channel, discord.TextChannel):
                info["topic"] = channel.topic or "None"
                info["nsfw"] = channel.nsfw
                info["slowmode_delay"] = f"{channel.slowmode_delay}s"
            elif isinstance(channel, discord.VoiceChannel):
                info["bitrate"] = f"{channel.bitrate/1000}kbps"
                info["user_limit"] = channel.user_limit or "Unlimited"
                # Add connected members
                connected_members = [f"{m.name} ({m.display_name})" for m in channel.members]
                info["connected_members"] = ", ".join(connected_members) if connected_members else "None"
            
            return [TextContent(
                type="text",
                text=f"Channel Information for '#{channel.name}':\n" + 
                     "\n".join(f"{k}: {v}" for k, v in info.items()) +
                     f"\n\nPermission Overwrites:{''.join(overwrites) if overwrites else ' None'}"
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error inspecting channel: {str(e)}")]

    elif name == "get_audit_log":
        try:
            guild = await discord_client.fetch_guild(int(arguments["server_id"]))
            limit = min(int(arguments.get("limit", 20)), 100)
            action_type = arguments.get("action_type") # Optional filter
            
            entries = []
            async for entry in guild.audit_logs(limit=limit):
                if action_type and action_type.lower() not in str(entry.action).lower():
                    continue
                    
                entries.append(f"[{format_dt(entry.created_at)}] {entry.user.name}: {str(entry.action).replace('AuditLogAction.', '')} -> {entry.target}")

            return [TextContent(
                type="text",
                text=f"Audit Log (Last {len(entries)} entries):\n" + "\n".join(entries)
            )]
        except Exception as e:
            return [TextContent(type="text", text=f"Error fetching audit log: {str(e)}")]

    # Role Management Tools
    elif name == "add_role":
        guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        member = await guild.fetch_member(int(arguments["user_id"]))
        role = guild.get_role(int(arguments["role_id"]))
        
        await member.add_roles(role, reason="Role added via MCP")
        return [TextContent(
            type="text",
            text=f"Added role {role.name} to user {member.name}"
        )]

    elif name == "remove_role":
        guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        member = await guild.fetch_member(int(arguments["user_id"]))
        role = guild.get_role(int(arguments["role_id"]))
        
        await member.remove_roles(role, reason="Role removed via MCP")
        return [TextContent(
            type="text",
            text=f"Removed role {role.name} from user {member.name}"
        )]

    # Channel Management Tools
    elif name == "create_text_channel":
        guild = await discord_client.fetch_guild(int(arguments["server_id"]))
        category = None
        if "category_id" in arguments:
            category = guild.get_channel(int(arguments["category_id"]))
        
        channel = await guild.create_text_channel(
            name=arguments["name"],
            category=category,
            topic=arguments.get("topic"),
            reason="Channel created via MCP"
        )
        
        return [TextContent(
            type="text",
            text=f"Created text channel #{channel.name} (ID: {channel.id})"
        )]

    elif name == "delete_channel":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        await channel.delete(reason=arguments.get("reason", "Channel deleted via MCP"))
        return [TextContent(
            type="text",
            text=f"Deleted channel successfully"
        )]

    # Message Reaction Tools
    elif name == "add_reaction":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        message = await channel.fetch_message(int(arguments["message_id"]))
        await message.add_reaction(arguments["emoji"])
        return [TextContent(
            type="text",
            text=f"Added reaction {arguments['emoji']} to message"
        )]

    elif name == "add_multiple_reactions":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        message = await channel.fetch_message(int(arguments["message_id"]))
        for emoji in arguments["emojis"]:
            await message.add_reaction(emoji)
        return [TextContent(
            type="text",
            text=f"Added reactions: {', '.join(arguments['emojis'])} to message"
        )]

    elif name == "remove_reaction":
        channel = await discord_client.fetch_channel(int(arguments["channel_id"]))
        message = await channel.fetch_message(int(arguments["message_id"]))
        await message.remove_reaction(arguments["emoji"], discord_client.user)
        return [TextContent(
            type="text",
            text=f"Removed reaction {arguments['emoji']} from message"
        )]

    elif name == "list_servers":
        servers = []
        for guild in discord_client.guilds:
            servers.append({
                "id": str(guild.id),
                "name": guild.name,
                "member_count": guild.member_count,
                "created_at": guild.created_at.isoformat()
            })
        
        return [TextContent(
            type="text",
            text=f"Available Servers ({len(servers)}):\n" + 
                 "\n".join(f"{s['name']} (ID: {s['id']}, Members: {s['member_count']})" for s in servers)
        )]

    raise ValueError(f"Unknown tool: {name}")

async def main():
    # Start Discord bot in the background
    asyncio.create_task(discord_client.start(DISCORD_TOKEN))
    
    # Run MCP server
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
