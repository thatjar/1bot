import importlib
import logging

from discord.ext import commands, tasks

from config import config
from main import Bot


class Etc(commands.Cog):
    """Cog for owner commands, background tasks, and other things not related to the end user."""

    def __init__(self, bot):
        self.bot: Bot = bot

    @tasks.loop(hours=6)
    async def post_stats(self):
        """Post guild count to top.gg automatically."""

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

    @commands.command(aliases=["re"])
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, *, cogs: str = None):
        try:
            if not cogs:
                cogs_to_reload = [
                    ext for ext in self.bot.extensions if ext.startswith("cogs.")
                ]
            else:
                cogs_to_reload = [f"cogs.{cog}" for cog in cogs.split()]

            for cog in cogs_to_reload:
                await self.bot.reload_extension(cog)
            await ctx.send("✅ Reloaded successfully.")
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


async def setup(bot):
    await bot.add_cog(Etc(bot))
