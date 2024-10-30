import discord
from discord.ext import commands
from discord import app_commands

import sys

sys.path.insert(0, "/")  # to get access to config module
from config import config


class InfoButtons(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label="Add to server",
                url=config["bot_invite"],
                emoji=bot.get_emoji(config["emojis"]["add_to_server"]),
            )
        )
        self.add_item(
            discord.ui.Button(
                label="Website",
                url=bot.website_url,
                emoji=bot.get_emoji(config["emojis"]["website"]),
            )
        )
        self.add_item(
            discord.ui.Button(
                label="Support Server",
                url=bot.server_invite,
                emoji=bot.get_emoji(config["emojis"]["support"]),
            )
        )

    @discord.ui.button(label="License", emoji=f"<:emoji:{config['emojis']['license']}>")
    async def license(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            """1Bot - a free Discord bot to let you get things done without leaving Discord.
Copyright (C) 2024-present thatjar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
""",
            ephemeral=True,
        )


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
        embed.add_field(
            name="Bot version", value=f"v{config['bot_version']}", inline=False
        )
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
