from __future__ import annotations

from sys import version_info
from typing import TYPE_CHECKING, Literal

import discord
from discord import app_commands
from discord.ext import commands

from config import config
from utils.utils import VL_STRINGS, GenericError
from utils.views import InfoButtons

if TYPE_CHECKING:
    from main import OneBot


class Miscellaneous(commands.Cog):
    def __init__(self, bot: OneBot):
        self.bot = bot
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
    async def botinfo(self, i: discord.Interaction):
        appinfo = await self.bot.application_info()
        user_installs = appinfo.approximate_user_install_count
        command_count = 0
        for command in self.bot.tree.get_commands():
            command_count += 1
            if isinstance(command, app_commands.Group):
                command_count += len(command.commands) - 1
        embed = discord.Embed(
            title=f"{self.bot.user.name} Stats and Information",
            colour=self.bot.colour,
            description=f"**Servers**: {len(self.bot.guilds)}\n"
            f"**User installs**: {user_installs}\n"
            f"**Websocket latency**: {(self.bot.latency * 1000):.0f} ms\n"
            f"**Command count**: {command_count}\n",
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
    @app_commands.command(name="avatar", description="Get any user's avatar")
    @app_commands.describe(
        user="The user or user ID to get the avatar of (default: yourself)",
        profile="Server avatar / User avatar (default: server)",
    )
    async def avatar(
        self,
        i: discord.Interaction,
        user: discord.Member | discord.User | None = None,
        profile: Literal["Server", "User"] = "Server",
    ):
        user = user or i.user
        embed = discord.Embed(colour=self.bot.colour)

        if profile == "User" or not i.guild:
            embed.title = f"{user.global_name or user.name}'s global avatar"
            asset = user.avatar or user.display_avatar
        else:
            embed.title = f"{user.display_name}'s avatar in this server"
            asset = user.display_avatar

        embed.set_image(url=asset.url)

        # Download links for all formats
        hyperlinks = []
        if user.avatar is not None:
            for format in ("gif", "png", "jpg", "webp"):
                # Skip GIF if the avatar is not animated
                if format == "gif" and not asset.is_animated():
                    continue

                hyperlinks.append(
                    f"[{format.upper()}]({asset.with_format(format).url})"
                )
        else:
            # If user has no avatar, only PNG is available
            hyperlinks.append(f"[PNG]({asset.url})")

        embed.description = "**Download Links**\n" + " | ".join(hyperlinks)

        await i.response.send_message(embed=embed)

    # banner
    @app_commands.command(name="banner", description="Get any user's banner")
    @app_commands.describe(
        user="The user to get the banner of (default: yourself)",
        profile="Server banner / User banner (default: user)",
    )
    async def banner(
        self,
        i: discord.Interaction,
        user: discord.Member | discord.User | None = None,
        profile: Literal["Server", "User"] = "User",
    ):
        await i.response.defer()
        colour = None

        if profile == "User" or not i.guild:
            user: discord.User = await self.bot.fetch_user(
                user.id if user else i.user.id
            )
            asset = user.banner
            if asset is None:
                colour = user.accent_colour.value if user.accent_colour else None
        else:
            user = user or i.user
            asset = getattr(user, "display_banner", None)
            if asset is None:
                fetched = await self.bot.fetch_user(user.id)
                colour = fetched.accent_colour.value if fetched.accent_colour else None

        if asset is None:
            err_msg = f"This user has no {profile.lower()} banner image."
            if colour is not None:
                hexcode = f"{colour:X}"
                err_msg += f" Their banner colour is `#{hexcode:>06}`."
            raise GenericError(err_msg)

        embed = discord.Embed(
            colour=self.bot.colour,
            title=f"{user.global_name or user.name}'s banner",
        )

        embed.set_image(url=asset.url)

        # Download links for all formats
        hyperlinks = []
        for format in ("gif", "png", "jpg", "webp"):
            # Skip GIF if the avatar is not animated
            if format == "gif" and not asset.is_animated():
                continue

            hyperlinks.append(f"[{format.upper()}]({asset.with_format(format).url})")

        embed.description = "**Download Links**\n" + " | ".join(hyperlinks)

        await i.followup.send(embed=embed)

    # userinfo
    @app_commands.command(name="userinfo", description="Get information about any user")
    @app_commands.describe(user="User/User ID (default: yourself)")
    async def userinfo(
        self, i: discord.Interaction, user: discord.Member | discord.User | None = None
    ):
        await i.response.defer()

        user = user or i.user
        fetched = await self.bot.fetch_user(user.id)
        colour = fetched.accent_colour
        embed = discord.Embed(
            title=user.name,
            colour=colour,
            description=f"**ID**: {user.id}\n"
            f"**Display name**: {user.global_name or user.name}\n",
        )
        embed.add_field(
            name="Account created:",
            value=f"<t:{user.created_at.timestamp():.0f}:F>\n",
        )

        if isinstance(user, discord.Member):
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

        embed.set_thumbnail(
            url=user.avatar.url if user.avatar else user.display_avatar.url
        )
        await i.followup.send(embed=embed)

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
            f"**Verification**: {VL_STRINGS[guild.verification_level]}\n",
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.set_footer(text=f"Server ID: {guild.id} | Shard ID: {guild.shard_id}")
        await i.response.send_message(embed=embed)

    # delete response
    @app_commands.allowed_installs(guilds=True, users=False)
    async def deleteresponse(self, i: discord.Interaction, message: discord.Message):
        if not message.interaction_metadata or message.author.id != self.bot.user.id:
            raise GenericError(f"Not a {self.bot.user.name} command response.")

        if (
            message.interaction_metadata.user.id == i.user.id
            or i.permissions.manage_messages
        ):
            await message.delete()
            await i.response.send_message("✅ Response deleted.", ephemeral=True)
        else:
            raise GenericError(
                "This response can only be deleted by its invoker or a moderator."
            )
