import logging
import os
from datetime import datetime

import discord
import requests
from discord.ext import commands, tasks

from config import config


class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
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

    async def setup_hook(self):
        await self.load_extension("jishaku")
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                await self.load_extension(f"cogs.{cog[:-3]}")

        self.error_channel = await self.fetch_channel(config["error_channel"])

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")

    colour = 0xFF7000
    server_invite = config["server_invite"]
    website_url = config["website"]
    launch_time = int(datetime.now().timestamp())


bot = Bot()


@bot.command()
@commands.is_owner()
async def reload(ctx, extension: str = None):
    if not extension:
        for cog in os.listdir("./cogs"):
            if cog.endswith(".py"):
                await bot.reload_extension(f"cogs.{cog[:-3]}")
        await ctx.send("✅ Reloaded all cogs.")
    else:
        try:
            await bot.reload_extension(f"cogs.{extension}")
            await ctx.send(f"✅ Reloaded cog `{extension}`.")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"❌ Invalid cog `cogs.{extension}`")


# Post server count to top.gg
@tasks.loop(hours=6)
async def post_stats():
    try:
        r = requests.post(
            f"https://top.gg/api/bots/{bot.user.id}/stats",
            headers={"Authorization": config["topgg_token"]},
            json={"server_count": len(bot.guilds)},
        )
        if not r.ok:
            logging.error(f"Failed to post guild count to top.gg:\n{r.text}")
    except Exception as e:
        logging.error(f"Failed to post guild count to top.gg:\n{e}")


if __name__ == "__main__":
    bot.run(config["token"], log_level=logging.WARNING, root_logger=True)
