import sys

import discord
from discord import app_commands
from discord.ext import commands

sys.path.insert(0, "/")  # to get access to config module
from views import InfoButtons


class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="ping", description="Test the bot's latency")
    async def ping(self, i: discord.Interaction):
        await i.response.send_message(f"Pong! `{round(self.bot.latency * 1000)} ms`")

    @app_commands.command(name="botinfo", description="Get information about the bot")
    async def botinfo(self, i: discord.Interaction):
        embed = discord.Embed(
            title="1Bot Stats and Information", colour=self.bot.colour
        )
        embed.add_field(name="Bot version", value=f"{self.bot.version}", inline=False)
        embed.add_field(
            name="Source code",
            value="The bot's original source code is hosted on [GitHub](https://github.com/thatjar/1bot) under the [GNU Affero General Public License](https://github.com/thatjar/1bot/blob/main/LICENSE).\n",
            inline=False,
        )
        embed.add_field(name="Servers", value=f"{len(self.bot.guilds)} servers")
        embed.add_field(name="Uptime", value=f"<t:{self.bot.launch_time}:R>")
        if i.guild:
            embed.add_field(name="Shard ID", value=f"{i.guild.shard_id}")
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        # COPYRIGHT NOTICE
        embed.set_footer(text="Copyright (C) 2024-present thatjar")
        await i.response.send_message(embed=embed, view=InfoButtons(self.bot))


async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
