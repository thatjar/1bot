import logging
import os
from datetime import UTC, datetime

import discord
from aiohttp import ClientSession
from discord.ext import commands

from config import config


class OneBot(commands.AutoShardedBot):
    """1Bot's AutoShardedBot subclass"""

    session: ClientSession
    launch_time: int
    # Global embed colour
    colour = 0xFF7000

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            # Prefix for owner-only commands
            command_prefix=commands.when_mentioned,
            help_command=None,
            case_insensitive=True,
            intents=discord.Intents.default(),
            allowed_mentions=discord.AllowedMentions(everyone=False),
            allowed_installs=discord.app_commands.AppInstallationType(
                guild=True, user=True
            ),
            allowed_contexts=discord.app_commands.AppCommandContext(
                guild=True, dm_channel=True, private_channel=True
            ),
        )

    async def setup_hook(self) -> None:
        logging.info("Starting up...")
        # Load jishaku and all modules in the ./cogs dir
        await self.load_extension("jishaku")
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                await self.load_extension(f"cogs.{cog[:-3]}")

        # aiohttp session for making requests
        self.session = ClientSession()
        self.launch_time = round(datetime.now(UTC).timestamp())

    async def on_connect(self) -> None:
        self.user: discord.ClientUser
        logging.info(f"Connected: {self.user} ({self.user.id})")

    async def on_ready(self) -> None:
        logging.info("Ready: Client successfully initialised.")

    async def close(self) -> None:
        logging.info("Disconnecting.")
        await super().close()
        if hasattr(self, "session"):
            await self.session.close()


bot = OneBot()

if __name__ == "__main__":
    # Set logging levels
    level = logging.DEBUG if config.get("debug") else logging.WARNING

    logging.getLogger("httpx").setLevel(level)
    logging.getLogger("werkzeug").setLevel(level)
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(level)

    bot.run(config["token"], root_logger=True)
