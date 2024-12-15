<div align=right>
  <a href="https://discord.gg/JGcnKxEPsW">
    <img src="https://img.shields.io/discord/884078410010333235?label=server&logo=discord&logoColor=white">
  </a>
  <a href="https://www.codefactor.io/repository/github/thatjar/1bot">
    <img src="https://www.codefactor.io/repository/github/thatjar/1bot/badge" alt="CodeFactor" />
  </a>
</div>

# 1Bot - One bot, several uses.

[![Banner](https://1bot.netlify.app/banner.png)](https://1bot.netlify.app/)

1Bot is a free Discord bot that lets you get things done without leaving Discord - from poking fun at your friends to managing channels.

- [Add the bot to your server/account](https://discord.com/oauth2/authorize?client_id=884080176416309288)
- [Website (ToS & Privacy Policy)](https://1bot.netlify.app)
- [Server for Updates and Support](https://discord.gg/JGcnKxEPsW)
- [Top.gg page (upvote 1Bot!)](https://top.gg/bot/884080176416309288)

## Self-hosting

1Bot is **not intended to be a self-hosted bot**, but it is possible.  
Copyright notices must be preserved, and if your bot is made public, its source code must be published under the AGPL.  
You will have to create a `config.py` file in the root directory with the following contents:

```py
# Everything except "token" and "error_channel" is optional.
config: dict = {
    "token": BOT_TOKEN,
    "error_channel": ERROR_CHANNEL_ID, # Where unhandled exceptions will be reported. Bot must have access to the channel
    "server_invite": "https://discord.gg/JGcnKxEPsW",
    "bot_invite": "https://discord.com/oauth2/authorize?client_id=884080176416309288",
    "website": "https://1bot.netlify.app",
    # Emoji IDs to appear in buttons
    "emojis": {
        "add_to_server": ...,
        "website": ...,
        "support": ...,
    },
    "debug": True # to use logging.DEBUG as log_level. Prints a LOT of stuff to the console
}

```

###### Copyright &copy; 2024 thatjar. Not affiliated with Discord, Inc.
