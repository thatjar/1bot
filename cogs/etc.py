import importlib
import logging
import subprocess
from typing import TYPE_CHECKING

import discord
from discord.ext import commands, tasks

from config import config

if TYPE_CHECKING:
    from main import OneBot


class Etc(commands.Cog):
    """Cog for owner commands, background tasks, etc. Not for end-user commands/features."""

    def __init__(self, bot):
        self.bot: OneBot = bot
        self.post_stats.start()

    @tasks.loop(hours=6)
    async def post_stats(self):
        """Post guild count to top.gg automatically."""

        if config.get("topgg_token") is None:
            return

        try:
            async with self.bot.session.post(
                f"https://top.gg/api/bots/{self.bot.user.id}/stats",
                headers={"Authorization": config["topgg_token"]},
                json={"server_count": len(self.bot.guilds)},
            ) as r:
                if r.status != 200:
                    logging.error(
                        f"Failed to post guild count to top.gg (status code: {r.status}):\n{r.text}"
                    )
        except Exception as e:
            logging.error(f"Failed to post guild count to top.gg:\n{e}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Reply to the bot mention with a help message."""

        if message.content == self.bot.user.mention:
            await message.reply(
                f"{self.bot.user.name} uses Application Commands \N{EM DASH} "
                "get started by opening your Apps menu or typing `/` in a channel that allows application commands.\n"
                "-# Check out the [Wiki](https://github.com/thatjar/1bot/wiki) for full documentation.\n",
                suppress_embeds=True,
            )

    @commands.command(aliases=["re"])
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, *, cogs: str | None = None):
        try:
            if not cogs:
                cogs_to_reload = [
                    ext for ext in self.bot.extensions if ext.startswith("cogs.")
                ]
            else:
                cogs_to_reload = [f"cogs.{cog}" for cog in cogs.split()]

            for cog in cogs_to_reload:
                await self.bot.reload_extension(cog)
            await ctx.send(
                "✅ Reloaded cogs:\n"
                + "\n".join([f"`{cog}`" for cog in cogs_to_reload])
            )
        except commands.ExtensionError as e:
            await ctx.send(f"❌ {e}")

    @commands.command(aliases=["ri"])
    @commands.is_owner()
    async def reloadimport(self, ctx: commands.Context, module: str):
        try:
            module = importlib.import_module(module)
        except ModuleNotFoundError:
            await ctx.send(f"❌ Module {module} not found.")
            return

        importlib.reload(module)
        await ctx.send("✅ Reloaded successfully.")

    @commands.command(aliases=["u"])
    @commands.is_owner()
    async def update(self, ctx: commands.Context):
        # Requires git to be configured on server
        await ctx.send("Pulling from `origin main`...")

        try:
            # git restore all files to avoid merge conflicts
            subprocess.run(
                ["git", "restore", "."],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            subprocess.run(
                ["git", "pull", "origin", "main"],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError as e:
            await ctx.send(f"❌ {e}")
            return

        await ctx.invoke(self.bot.get_command("reload"))

    @commands.command()
    @commands.is_owner()
    async def activity(self, ctx: commands.Context, *, status: str | None = None):
        await self.bot.change_presence(activity=discord.CustomActivity(status))
        await ctx.send(f"✅ Activity set to `{status}`.")


async def setup(bot):
    await bot.add_cog(Etc(bot))
