# Discord MCP Server (Dockerized)

A Model Context Protocol (MCP) server that provides Discord integration capabilities, now enhanced with Role management tools and optimized for Docker.

This project is a fork of [hanweg/mcp-discord](https://github.com/hanweg/mcp-discord) with added features and simplified containerization.

## Available Tools

### 🛡️ Role & Member Management (New)
- `list_roles`: List all roles in a server with their IDs and positions.
- `inspect_role`: Get detailed metadata for a specific role (permissions, color, etc.).
- `list_members`: List server members and their assigned roles.

### 📊 Server Information
- `list_servers`: List all servers the bot has access to.
- `get_server_info`: Get detailed server metrics.
- `get_channels`: List channels in a server.
- `get_user_info`: Get detailed information about a Discord user.

### 💬 Messaging & Moderation
- `send_message`: Send a message to a channel.
- `read_messages`: Read recent history and reactions.
- `add_reaction` / `remove_reaction`: Manage message reactions.
- `moderate_message`: Delete messages and timeout users.

## 🚀 Getting Started (Docker)

This version is designed to run entirely within Docker, eliminating the need for local Python installations.

### 1. Build the Image
Clone this repository and run:
```bash
docker build -t discord-mcp .
```

### 2. Configure MCP Client
Add the following configuration to your MCP client (e.g., Claude Desktop or Antigravity).

- **Path for Windows (Claude):** `%APPDATA%\Claude\claude_desktop_config.json`
- **Path for Antigravity:** `~/.gemini/antigravity/mcp_config.json`
- **Path for Kiro:** `C:\Users\Admin\.kiro\settings\mcp.json`

```json
{
  "mcpServers": {
    "discord": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "DISCORD_TOKEN",
        "discord-mcp"
      ],
      "env": {
        "DISCORD_TOKEN": "your_bot_token_here"
      }
    }
  }
}
```

### 3. Setting Up Your Discord Bot
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create an Application and a Bot.
3. Enable the following **Privileged Gateway Intents**:
   - `PRESENCE INTENT`
   - `SERVER MEMBERS INTENT`
   - `MESSAGE CONTENT INTENT`
4. Copy your **Bot Token** and paste it into the `env` section above.
5. Invite the bot to your server using the OAuth2 URL Generator (permissions: `Administrator` recommended for full tool access).

## 🔮 Future Plans

We plan to add even more Discord functionality to this MCP server, expanding its capabilities for better server management and interaction. Stay tuned for updates!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
Based on the original work by [Hanweg Altimer](https://github.com/hanweg/mcp-discord).
