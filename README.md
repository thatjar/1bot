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
Contributions and suggestions are welcome.

- [Add the bot to your server/account](https://discord.com/oauth2/authorize?client_id=884080176416309288)
- [Website (ToS & Privacy Policy)](https://1bot.netlify.app)
- [Server for Updates and Support](https://discord.gg/JGcnKxEPsW)
- [Top.gg page (upvote 1Bot!)](https://top.gg/bot/884080176416309288)

## Self-hosting

This project is under the AGPL, so **if your bot is made public, you must publish its source code under the AGPL** as well.

### Instructions

You will have to create a `config.py` file in the root directory with the following structure:

```py
config = {
    "token": str, # REQUIRED
    "error_channel": int,
    "server_invite": "https://discord.gg/JGcnKxEPsW",
    "bot_invite": "https://discord.com/oauth2/authorize?client_id=884080176416309288",
    "website": "https://1bot.netlify.app",
    "repository": "https://github.com/thatjar/1bot",
    "emojis": {
        "support": int,
        "add_to_server": int,
        "website": int,
    },
    "debug": False
}

```

- `token`: Your Discord application's bot token. This is the only required value in the dict.
- `error_channel`: The ID of the channel where unhandled runtime exceptions will be reported to. Not required, but I recommend setting it to get error notifications directly on Discord.
- `server_invite`: If set, will be used as a support server invite. Unhandled exceptions will give the user this invite. Also used in the botinfo command.
- `bot_invite`: If set, will be used as a button to invite the bot to other servers in the botinfo command.
- `website`: If set, will be used as a button to the bot's website.
- `repository`: If your bot is made public, you must publish its source code under the AGPL. Set this to your repo URL.
- `emojis`: Dictionary of custom emoji IDs. If set, will be used as emojis on the buttons for `server_invite`, `bot_invite` and `website` respectively.
- `debug`: If set to True, `logging.DEBUG` will be used as the `log_level` in [Bot.run](https://discordpy.readthedocs.io/en/latest/ext/commands/api.html?highlight=log_level#discord.ext.commands.Bot.run). Otherwise, `logging.WARNING` will be used. DEBUG will print a lot of information to the console, expect to see stuff printed every few seconds if enabled.

###### Copyright &copy; 2024-present thatjar. Not affiliated with Discord, Inc.
