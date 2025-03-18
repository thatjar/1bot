from sys import version_info
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from config import config
from views import InfoButtons

if TYPE_CHECKING:
    from main import Bot


class Miscellaneous(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.bot.tree.add_command(
            app_commands.ContextMenu(name="User Info", callback=self.userinfo_ctx)
        )
        self.bot.tree.add_command(
            app_commands.ContextMenu(
                name="Delete Response", callback=self.deleteresponse
            ),
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
            f"**User installs**: {user_installs}\n"
            f"**Uptime**: <t:{self.bot.launch_time}:R>\n"
            f"**Websocket latency**: {(self.bot.latency * 1000):.0f} ms\n"
            f"**Command count**: {len(self.bot.tree.get_commands())} (not including subcommands)\n",
        )
        if i.guild:
            embed.description += f"**Shard ID**: {i.guild.shard_id}"

        embed.add_field(
            name="Software versions",
            value=f"Python: {version_info.major}.{version_info.minor}.{version_info.micro}\n"
            f"discord.py: {discord.__version__}\n",
        )

        if config.get("repository"):
            embed.add_field(
                name="Source code",
                value=f"The bot's original source code is hosted on [GitHub]({config['repository']}) "
                "under the [GNU Affero General Public License](https://gnu.org/licenses/agpl-3.0.html).\n",
                inline=False,
            )

        embed.set_footer(
            text="Copyright (C) 2024-present thatjar. Not affiliated with Discord, Inc."
        )
        await i.response.send_message(embed=embed, view=InfoButtons())

    # avatar
    @app_commands.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(
        user="The user to get the avatar of (default: yourself)",
        type="Server avatar or user avatar (default: server avatar)",
    )
    @app_commands.choices(
        type=[
            app_commands.Choice(name="Server", value=0),
            app_commands.Choice(name="User (Global)", value=1),
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
        embed = discord.Embed(colour=self.bot.colour)

        if type == 1:
            embed.title = f"{user.global_name or user.name}'s global avatar"
        else:
            embed.title = f"{user.display_name}'s avatar in this server"

        asset: discord.Asset = (
            user.avatar if type == 1 and user.avatar else user.display_avatar
        )
        embed.set_image(url=asset.url)

        # Download links for all formats
        links = []
        if user.avatar is not None:
            for format in ("png", "jpg", "webp", "gif"):
                # Skip GIF if the avatar is not animated
                if format == "gif" and not asset.is_animated():
                    continue

                links.append(f"[{format.upper()}]({asset.with_format(format).url})")
        else:
            # If user has no avatar, only PNG is available
            links.append(f"[PNG]({asset.url})")

        embed.description = "**Download Links**\n" + " | ".join(links)
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
            f"**Display name**: {user.global_name}\n",
        )
        embed.add_field(
            name="Account created:",
            value=f"<t:{user.created_at.timestamp():.0f}:F>\n",
        )

        if i.guild:
            if user.nick:
                embed.description += f"**Nickname**: {user.nick}\n"

            if user.joined_at is not None:
                embed.add_field(
                    name="Joined this server:",
                    value=f"<t:{user.joined_at.timestamp():.0f}:F>",
                )
            else:
                embed.add_field(name="Joined at", value="Unknown")

            if i.is_guild_integration():
                # -1 to exclude the @everyone role
                embed.description += f"**Role count**: {len(user.roles)-1}\n"

        embed.set_thumbnail(url=user.avatar.url)
        await i.response.send_message(embed=embed)

    # userinfo (ctxmenu)
    async def userinfo_ctx(
        self, i: discord.Interaction, user: discord.Member | discord.User
    ):
        await self.userinfo.callback(self, i, user)

    # server info
    @app_commands.command(
        name="serverinfo", description="Get information about the server"
    )
    @app_commands.allowed_installs(guilds=True, users=False)
    @app_commands.allowed_contexts(guilds=True, dms=False, private_channels=False)
    @app_commands.checks.cooldown(2, 15, key=lambda i: i.channel)
    async def serverinfo(self, i: discord.Interaction):
        vl = discord.VerificationLevel
        vl_strings = {
            vl.none: "None",
            vl.low: "Members must have a verified email on their Discord account.",
            vl.medium: "Members must have a verified email and be registered on Discord for more than five minutes.",
            vl.high: "Members must have a verified email, be registered on Discord for more than five minutes,"
            " and be a member of the server for more than ten minutes.",
            vl.highest: "Members must have a verified phone number.",
        }

        guild = await self.bot.fetch_guild(i.guild.id)

        embed = discord.Embed(
            title=guild.name,
            colour=self.bot.colour,
            description=f"**Member count**: {guild.approximate_member_count}\n"
            f"**Created at**: <t:{guild.created_at.timestamp():.0f}:F>\n"
            f"**Boost level**: {guild.premium_tier}\n"
            f"**Boosts**: {guild.premium_subscription_count}\n"
            f"**Roles**: {len(guild.roles)}\n"
            f"**Emojis**: {len(guild.emojis)}\n"
            f"**Verification**: {vl_strings[guild.verification_level]}\n",
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=f"Server ID: {guild.id} | Shard ID: {guild.shard_id}")
        await i.response.send_message(embed=embed)

    # delete response
    async def deleteresponse(self, i: discord.Interaction, message: discord.Message):
        if not message.interaction_metadata or message.author.id != self.bot.user.id:
            raise ValueError(f"Not a {self.bot.user.name} command response.")

        if (
            message.interaction_metadata.user.id == i.user.id
            or i.channel.permissions_for(i.user).manage_messages
        ):
            await message.delete()
            await i.response.send_message("✅ Response deleted.", ephemeral=True)
        else:
            raise ValueError(
                "This response can only be deleted by its invoker or a moderator."
            )


async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
