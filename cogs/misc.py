import sys

import discord
from discord import app_commands
from discord.ext import commands

sys.path.insert(0, "/")  # to get access to config module
from views import InfoButtons


class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.bot.tree.add_command(
            app_commands.ContextMenu(name="User Info", callback=self.userinfo_ctx)
        )

    # botinfo
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
            + f"**Websocket latency**: {round(self.bot.latency * 1000)} ms\n"
            + f"**Command count**: {len(self.bot.tree.get_commands())} (not including subcommands)\n",
        )
        if i.guild:
            embed.description += f"**Shard ID**: {i.guild.shard_id}"

        embed.add_field(
            name="Source code",
            value="The bot's original source code is hosted on [GitHub](https://github.com/thatjar/1bot) "
            + "under the [GNU Affero General Public License](https://github.com/thatjar/1bot/blob/main/LICENSE).\n",
            inline=False,
        )

        embed.set_footer(
            text="Copyright (C) 2024-present thatjar. Not affiliated with Discord, Inc."
        )
        await i.response.send_message(embed=embed, view=InfoButtons(self.bot))

    # avatar
    @app_commands.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(
        user="The user to get the avatar of (default: yourself)",
        type="Server avatar or user avatar (default: server avatar)",
    )
    @app_commands.choices(
        type=[
            app_commands.Choice(name="Server", value=0),
            app_commands.Choice(name="User", value=1),
        ]
    )
    @app_commands.checks.cooldown(2, 15, key=lambda i: i.channel)
    async def avatar(
        self,
        i: discord.Interaction,
        user: discord.Member | discord.User = None,
        type: app_commands.Choice[int] = 0,
    ):
        user = user or i.user
        embed = discord.Embed(colour=self.bot.colour, title=(f"{user.name}'s avatar"))
        embed.set_image(url=user.avatar.url if type else user.display_avatar.url)
        await i.response.send_message(embed=embed)

    # userinfo
    @app_commands.command(name="userinfo", description="Get information about a user")
    @app_commands.describe(user="The user to get information on (default: yourself)")
    async def userinfo(
        self, i: discord.Interaction, user: discord.Member | discord.User = None
    ):
        user = user or i.user
        embed = discord.Embed(
            title=user.name,
            colour=self.bot.colour,
            description=f"**ID**: {user.id}\n"
            + f"**Bot**: {user.bot}\n"
            + f"**Display name**: {user.display_name}\n"
            + f"**Created at**: <t:{round(user.created_at.timestamp())}:F>\n",
        )
        if i.guild:
            try:
                embed.description += (
                    f"**Joined at**: <t:{round(user.joined_at.timestamp())}:F>\n"
                )
            except AttributeError:
                embed.description += "**Joined at**: Could not determine\n"
            if i.is_guild_integration():
                embed.description += f"**Role count**: {len(user.roles)-1}"
        embed.set_thumbnail(url=user.avatar.url)
        await i.response.send_message(embed=embed, ephemeral=True)

    # userinfo (ctxmenu)
    async def userinfo_ctx(
        self, i: discord.Interaction, user: discord.Member | discord.User
    ):
        await self.userinfo.callback(self, i, user)


async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
