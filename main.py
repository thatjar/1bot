import os
from datetime import datetime

import discord
from discord.ext import commands

from config import config


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix=commands.when_mentioned,
            help_command=None,
            intents=discord.Intents.default(),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(everyone=False),
        )

    async def setup_hook(self):
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")
        await self.load_extension("jishaku")
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                await self.load_extension(f"cogs.{cog[:-3]}")

        self.error_channel = await self.fetch_channel(config["error_channel"])

    version = "v1.0.0beta"

    colour = 0xFF7000
    server_invite = config["server_invite"]
    website_url = config["website"]
    launch_time = int(datetime.now().timestamp())


bot = Bot()


if __name__ == "__main__":
    bot.run(config["token"])
