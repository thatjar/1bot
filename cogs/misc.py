import sys

import discord
from discord import app_commands
from discord.ext import commands

sys.path.insert(0, "/")  # to get access to config module
from views import InfoButtons


class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="botinfo", description="Get information about the bot")
    @app_commands.checks.cooldown(2, 10, key=lambda i: i.channel)
    async def botinfo(self, i: discord.Interaction):
        appinfo = await self.bot.application_info()
        user_installs = appinfo.approximate_user_install_count
        embed = discord.Embed(
            title="1Bot Stats and Information",
            colour=self.bot.colour,
            description=f"**Servers**: {len(self.bot.guilds)}\n"
            + f"**User installs**: {user_installs}\n"
            + f"**Uptime**: <t:{self.bot.launch_time}:R>\n"
            + f"**Websocket latency**: {round(self.bot.latency * 1000)} ms\n",
        )
        if i.guild:
            embed.description += f"**Shard ID**: {i.guild.shard_id}"

        embed.add_field(
            name="Source code",
            value="The bot's original source code is hosted on [GitHub](https://github.com/thatjar/1bot) "
            + "under the [GNU Affero General Public License](https://github.com/thatjar/1bot/blob/main/LICENSE).\n",
            inline=False,
        )

        # COPYRIGHT NOTICE
        embed.set_footer(
            text="Copyright (C) 2024-present thatjar. Not affiliated with Discord, Inc."
        )
        await i.response.send_message(embed=embed, view=InfoButtons(self.bot))


async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
