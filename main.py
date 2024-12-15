import logging
import os
from datetime import datetime

from aiohttp import ClientSession
import discord
from discord.ext import commands

from config import config


class Bot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            command_prefix=commands.when_mentioned,
            help_command=None,
            intents=discord.Intents.default(),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions(everyone=False),
            allowed_installs=discord.app_commands.AppInstallationType(
                guild=True, user=True
            ),
            allowed_contexts=discord.app_commands.AppCommandContext(
                guild=True, dm_channel=True, private_channel=True
            ),
        )

    async def setup_hook(self) -> None:
        await self.load_extension("jishaku")
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                await self.load_extension(f"cogs.{cog[:-3]}")

        self.error_channel = await self.fetch_channel(config["error_channel"])

        self.session = ClientSession()

    async def on_ready(self) -> None:
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    colour = 0xFF7000
    launch_time = int(datetime.now().timestamp())


bot = Bot()

if __name__ == "__main__":
    logging_level = logging.DEBUG if config.get("debug") else logging.WARNING

    bot.run(config["token"], log_level=logging_level, root_logger=True)
