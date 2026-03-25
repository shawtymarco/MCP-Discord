from __future__ import annotations

import os
import sys
import asyncio
import logging
from datetime import datetime
from functools import wraps
from typing import List

import discord
from mcp.types import TextContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord-mcp-server")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")


def format_dt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")


class DiscordMCPClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")


discord_client = DiscordMCPClient()


def require_discord_client(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        if not discord_client.is_ready():
            try:
                await asyncio.wait_for(discord_client.wait_until_ready(), timeout=5.0)
            except asyncio.TimeoutError:
                pass

        if not discord_client.is_ready():
            return [TextContent(
                type="text",
                text="Error: Discord client is not connected. Please check your BOT_TOKEN.",
            )]
        return await func(*args, **kwargs)
    return wrapper
