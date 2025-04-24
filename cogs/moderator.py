from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils import GenericError

if TYPE_CHECKING:
    from main import Bot


class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    def cog_load(self):
        for cmd in self.walk_app_commands():
            cmd.allowed_installs = app_commands.AppInstallationType(
                guild=True, user=False
            )
            cmd.allowed_contexts = app_commands.AppCommandContext(
                guild=True, dm_channel=False, private_channel=False
            )

    # embed
    @app_commands.command(name="embed", description="Create a rich embed")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(send_messages=True)
    async def embed(self, i: discord.Interaction):
        class EmbedSetup(discord.ui.Modal, title="Embed Setup"):
            embed_title = discord.ui.TextInput(label="Title (Required)", max_length=256)
            contents = discord.ui.TextInput(
                label="Contents (Required)",
                placeholder="Markdown supported",
                max_length=4000,
                style=discord.TextStyle.paragraph,
            )
            thumbnail = discord.ui.TextInput(
                label="Thumbnail", placeholder="Image URL", required=False
            )
            image = discord.ui.TextInput(
                label="Main Image", placeholder="Image URL", required=False
            )
            show_author = discord.ui.TextInput(
                label="Show you as the author?",
                placeholder="y/n (default: no)",
                min_length=1,
                max_length=1,
                required=False,
            )

            async def on_submit(self, i: discord.Interaction):
                embed = discord.Embed(
                    title=self.embed_title.value,
                    description=self.contents.value,
                )
                if self.thumbnail.value:
                    embed.set_thumbnail(url=self.thumbnail.value)
                if self.image.value:
                    embed.set_image(url=self.image.value)
                if self.show_author.value.lower() == "y":
                    embed.set_author(
                        name=i.user.display_name, icon_url=i.user.avatar.url
                    )
                await i.channel.send(embed=embed)
                await i.response.send_message("✅ Sent the embed.", ephemeral=True)

        await i.response.send_modal(EmbedSetup())

    # group for /purge commands
    purge_group = app_commands.Group(
        name="purge",
        description="Bulk delete messages",
        # default_permissions hides the commands for users without perms
        default_permissions=discord.Permissions(
            manage_messages=True, read_message_history=True
        ),
    )

    # /purge any
    @purge_group.command(name="any", description="Bulk delete messages of any type")
    @app_commands.checks.has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.checks.bot_has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.describe(
        count="The number of messages to delete (1-100, up to two weeks old)"
    )
    async def purge(self, i: discord.Interaction, count: int):
        await i.response.defer(ephemeral=True)
        cutoff = datetime.now(UTC) - timedelta(days=14)
        messages_to_delete = []

        async for message in i.channel.history(
            limit=100, oldest_first=False, after=cutoff
        ):
            messages_to_delete.append(message)
            if len(messages_to_delete) >= count:
                break

        if not messages_to_delete:
            raise GenericError(
                "No messages found to purge (up to 100, up to two weeks old)."
            )

        await i.channel.delete_messages(
            messages_to_delete,
            reason=f"Purged by {i.user.name}",
        )
        await i.followup.send(
            f"✅ Found and deleted {len(messages_to_delete)} messages."
        )

    # /purge bots
    @purge_group.command(
        name="bots", description="Bulk delete messages sent by bots only"
    )
    @app_commands.checks.has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.checks.bot_has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.describe(
        count="The number of messages to delete (1-100, up to two weeks old)"
    )
    async def purgebots(
        self, i: discord.Interaction, count: app_commands.Range[int, 1, 100]
    ):
        await i.response.defer(ephemeral=True)

        cutoff = datetime.now(UTC) - timedelta(days=14)
        messages_to_delete = []

        async for message in i.channel.history(oldest_first=False, after=cutoff):
            if message.author.bot:
                messages_to_delete.append(message)
            if len(messages_to_delete) >= count:
                break

        if not messages_to_delete:
            raise GenericError(
                "No bot messages found to purge (up to 100, up to two weeks old)."
            )

        await i.channel.delete_messages(
            messages_to_delete,
            reason=f"Purged by {i.user.name}",
        )
        await i.followup.send(
            f"✅ Found and deleted {len(messages_to_delete)} messages."
        )

    # /purge humans
    @purge_group.command(
        name="humans", description="Bulk delete messages sent by non-bots only"
    )
    @app_commands.checks.has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.checks.bot_has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.describe(
        count="The number of messages to delete (1-100, up to two weeks old)"
    )
    async def purgehumans(
        self, i: discord.Interaction, count: app_commands.Range[int, 1, 100]
    ):
        await i.response.defer(ephemeral=True)

        cutoff = datetime.now(UTC) - timedelta(days=14)
        messages_to_delete = []

        async for message in i.channel.history(oldest_first=False, after=cutoff):
            if not message.author.bot:
                messages_to_delete.append(message)
            if len(messages_to_delete) >= count:
                break

        if not messages_to_delete:
            raise GenericError(
                "No human messages found to purge (up to 100, up to two weeks old)."
            )

        await i.channel.delete_messages(
            messages_to_delete,
            reason=f"Purged by {i.user.name}",
        )
        await i.followup.send(
            f"✅ Found and deleted {len(messages_to_delete)} messages."
        )

    # /purge user
    @purge_group.command(
        name="user", description="Bulk delete messages sent by any user"
    )
    @app_commands.checks.has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.checks.bot_has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.describe(
        user="The user whose messages to delete",
        count="The number of messages to delete (1-100, up to two weeks old)",
    )
    async def purgeuser(
        self,
        i: discord.Interaction,
        user: discord.Member | discord.User,
        count: app_commands.Range[int, 1, 100],
    ):
        await i.response.defer(ephemeral=True)

        cutoff = datetime.now(UTC) - timedelta(days=14)
        messages_to_delete = []

        async for message in i.channel.history(oldest_first=False, after=cutoff):
            if message.author == user:
                messages_to_delete.append(message)
            if len(messages_to_delete) >= count:
                break

        if not messages_to_delete:
            raise GenericError(
                "No messages found from that user (up to 100, up to two weeks old)."
            )

        await i.channel.delete_messages(
            messages_to_delete,
            reason=f"Purged by {i.user.name}",
        )
        await i.followup.send(
            f"✅ Found and deleted {len(messages_to_delete)} messages.",
        )

    # disable threads
    @app_commands.command(
        name="disablethreads",
        description="Remove permissions to create threads in this channel",
    )
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    @app_commands.describe(
        role="The role to remove permissions from (default: @everyone)",
        reason="Reason (optional)",
    )
    async def disablethreads(
        self, i: discord.Interaction, role: discord.Role = None, reason: str = None
    ):
        role = role or i.guild.default_role
        reason = reason or "disabled threads"

        await i.response.defer(ephemeral=True)
        overwrite = discord.PermissionOverwrite(
            create_public_threads=False,
            create_private_threads=False,
        )
        await i.channel.set_permissions(
            role, overwrite=overwrite, reason=f"{i.user.name}: {reason}"
        )
        await i.followup.send(
            f"✅ Disabled permissions for `{role.name}` to create public and private threads."
        )

    # slowmode
    @app_commands.command(
        name="slowmode", description="View or set slowmode for the current channel"
    )
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.checks.cooldown(3, 20, key=lambda i: i.channel)
    @app_commands.describe(
        amount="The amount of units to set slowmode to",
        unit="The unit of time (default: seconds)",
    )
    @app_commands.choices(
        unit=[
            app_commands.Choice(name="seconds", value=1),
            app_commands.Choice(name="minutes", value=60),
            app_commands.Choice(name="hours", value=3600),
        ]
    )
    async def slowmode(
        self,
        i: discord.Interaction,
        amount: float | None = None,
        unit: app_commands.Choice[int] = 1,
    ):
        if amount is None:
            # if no amount is given, show the current slowmode
            if i.channel.slowmode_delay == 0:
                raise GenericError("This channel has no slowmode.")
            seconds = i.channel.slowmode_delay
            await i.response.send_message(f"Current slowmode: **{seconds} seconds**")
            return

        seconds = amount if unit == 1 else amount * unit.value

        if not 0 <= seconds <= 21600:
            raise GenericError("Slowmode must be between 0 and 6 hours.")
        await i.response.defer(ephemeral=True)

        await i.channel.edit(
            slowmode_delay=seconds, reason=f"{i.user.name} set slowmode"
        )
        await i.followup.send(
            f"✅ Slowmode set to {int(seconds)} seconds.",
            ephemeral=True,
        )

    # lock
    @app_commands.command(name="lock", description="Make a channel read-only")
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    @app_commands.describe(
        role="The role to remove permissions from (default: @everyone)",
        reason="The reason for locking the channel (optional)",
        silent="Keep the lock message private (default: False)",
    )
    async def lock(
        self,
        i: discord.Interaction,
        role: discord.Role = None,
        reason: str = None,
        silent: bool = False,
    ):
        await i.response.defer(ephemeral=True)
        role = role or i.guild.default_role

        overwrite = i.channel.overwrites_for(role)
        if (
            overwrite.send_messages
            is overwrite.create_public_threads
            is overwrite.create_private_threads
            is False
        ):
            raise GenericError(f"This channel is already locked for `{role.name}`.")

        overwrite.send_messages = False
        overwrite.create_public_threads = False
        overwrite.create_private_threads = False

        # reason string that appears in audit log
        log_reason = reason or f"{i.user.name}: No reason specified"

        # allow bot to send messages
        await i.channel.set_permissions(
            i.guild.me,
            reason="Added self permissions for locked channel",
            view_channel=True,
            send_messages=True,
        )
        await i.channel.set_permissions(role, reason=log_reason, overwrite=overwrite)
        embed = discord.Embed(
            title="Channel Locked",
            color=0xFF0000,
        )
        if reason:
            if len(reason) > 1024:
                reason = reason[:1021] + "..."
            embed.description = "**Reason:** " + reason
        else:
            embed.description = f"🔒 This channel has been locked for `{role.name}`."
        if not silent:
            await i.channel.send(embed=embed)
        await i.followup.send(
            f"✅ Removed permissions for `{role.name}` to send messages and create threads in this channel."
        )

    # unlock
    @app_commands.command(
        name="unlock", description="Undo the lock command (allow users to message)"
    )
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    @app_commands.describe(
        role="The role to reset permissions for (default: @everyone)",
        reason="The reason for unlocking the channel (optional)",
        silent="Keep the unlock message private (default: False)",
    )
    async def unlock(
        self,
        i: discord.Interaction,
        role: discord.Role = None,
        reason: str = None,
        silent: bool = False,
    ):
        await i.response.defer(ephemeral=True)
        role = role or i.guild.default_role

        overwrite = i.channel.overwrites_for(role)
        if (
            overwrite.send_messages
            is overwrite.create_public_threads
            is overwrite.create_private_threads
            in (None, True)
        ):
            raise GenericError(f"This channel is already unlocked for `{role.name}`.")

        overwrite.send_messages = None
        overwrite.create_public_threads = None
        overwrite.create_private_threads = None

        # reason string that appears in audit log
        log_reason = reason or f"{i.user.name}: No reason specified"

        # allow bot to send messages
        await i.channel.set_permissions(
            i.guild.me,
            reason="Added self permissions to send messages",
            view_channel=True,
            send_messages=True,
        )

        await i.channel.set_permissions(
            role,
            reason=log_reason,
            overwrite=overwrite,
        )
        embed = discord.Embed(
            title="Channel Unlocked",
            color=self.bot.colour,
        )
        if reason:
            if len(reason) > 1024:
                reason = reason[:1021] + "..."
            embed.description = "**Reason:** " + reason
        else:
            embed.description = f"🔓 This channel has been unlocked for `{role.name}`."
        if not silent:
            await i.channel.send(embed=embed)
        await i.followup.send(
            f"✅ Reset permissions for `{role.name}` to send messages and create threads in this channel."
        )

    # timeout
    @app_commands.command(
        name="timeout", description="Time out a user (or remove timeout)"
    )
    @app_commands.default_permissions(moderate_members=True)
    @app_commands.checks.has_permissions(moderate_members=True)
    @app_commands.checks.bot_has_permissions(moderate_members=True)
    @app_commands.describe(
        user="The user to time out (or remove timeout from)",
        minutes="The number of minutes to time out the user (default: 0)",
        hours="The number of hours to time out the user (default: 0)",
        days="The number of days to time out the user (default: 0)",
        reason="The reason for timing out the user (optional)",
        silent="Keep the timeout message private (default: False)",
    )
    async def timeout(
        self,
        i: discord.Interaction,
        user: discord.Member,
        minutes: int = 0,
        hours: int = 0,
        days: int = 0,
        reason: str = None,
        silent: bool = False,
    ):
        if user == i.user:
            raise GenericError("You cannot time out yourself.")
        if user == i.guild.me:
            raise GenericError("I cannot time out myself.")

        total_minutes = days * 1440 + hours * 60 + minutes
        if not 0 <= total_minutes <= 40320:
            raise GenericError("Timeout duration must be between 0 and 28 days.")

        # reason string that appears in audit log
        log_reason = reason or f"{i.user.name}: No reason specified"
        # if total_minutes is 0, pass None for a proper removal of timeout and audit log message
        await user.timeout(
            timedelta(minutes=total_minutes) if total_minutes else None,
            reason=log_reason,
        )

        embed = discord.Embed(
            title="User Timed Out",
            description=f"🕒 {user.mention} has been timed out for {days} days, {hours} hours and {minutes} minutes.",
            color=self.bot.colour,
        )
        if reason:
            if len(reason) > 1024:
                reason = reason[:1021] + "..."
            embed.add_field(name="Reason", value=reason, inline=False)
        if total_minutes == 0:
            embed.title = "User Removed from Timeout"
            embed.description = f"🕒 {user.mention} has been removed from timeout."

        await i.response.send_message(
            embed=embed,
            ephemeral=silent,
        )

    # ban
    @app_commands.command(
        name="ban",
        description="Ban any member or non-member from this server",
    )
    @app_commands.default_permissions(ban_members=True)
    @app_commands.checks.has_permissions(ban_members=True)
    @app_commands.checks.bot_has_permissions(ban_members=True)
    @app_commands.describe(
        user="Member/User ID to ban",
        days="The number of days of messages to delete (default: 1)",
        hours="The number of hours of messages to delete (default: 1 day, 0 hours)",
        reason="The reason for banning the user (optional)",
        silent="Disable publicly sending the ban message & DMing the user (default: False)",
    )
    async def ban(
        self,
        i: discord.Interaction,
        user: discord.User,
        days: int = 1,
        hours: int = 0,
        reason: str = None,
        silent: bool = False,
    ):
        if user == i.user:
            raise GenericError("You cannot ban yourself.")
        if user == i.guild.me:
            raise GenericError("I cannot ban myself.")
        if days * 86400 + hours * 3600 > 604800:
            raise GenericError("Total duration must be between 0 and 7 days.")

        # reason string that appears in audit log
        log_reason = reason or f"{i.user.name}: No reason specified"

        try:
            if not silent:
                dm_embed = discord.Embed(
                    description=f"You have been banned from {i.guild.name}.",
                    color=0xFF0000,
                )
                if reason:
                    if len(reason) > 1024:
                        reason = reason[:1021] + "..."
                    dm_embed.add_field(name="Reason", value=reason, inline=False)

                await user.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

        await i.guild.ban(
            user,
            reason=log_reason,
            delete_message_seconds=days * 86400 + hours * 3600,
        )

        embed = discord.Embed(
            title="User Banned",
            description=f"🔨 {user.mention} has been banned.",
            color=self.bot.colour,
        )

        embed.add_field(name="Reason", value=reason, inline=False)
        if days:
            embed.add_field(name="Messages Deleted", value=f"{days} days", inline=False)

        await i.response.send_message(embed=embed, ephemeral=silent)

    # create emoji
    @app_commands.command(name="emoji", description="Create an emoji from a link")
    @app_commands.default_permissions(create_expressions=True)
    @app_commands.checks.has_permissions(create_expressions=True)
    @app_commands.checks.bot_has_permissions(create_expressions=True)
    @app_commands.checks.cooldown(2, 20, key=lambda i: i.channel)
    @app_commands.describe(url="The link to the emoji", name="The name of the emoji")
    async def emoji(self, i: discord.Interaction, url: str, name: str):
        await i.response.defer(ephemeral=True)
        try:
            async with self.bot.session.get(url) as r:
                if r.status != 200:
                    raise GenericError("Invalid/incomplete URL.")

                emoji_bytes = await r.read()

        except aiohttp.ClientError:
            raise GenericError("Invalid/incomplete URL.")

        emoji = await i.guild.create_custom_emoji(
            name=name, image=emoji_bytes, reason=f"Uploaded by {i.user}"
        )

        await i.followup.send(f"✅ Created emoji {emoji}")

    @emoji.error
    async def emoji_error(
        self, i: discord.Interaction, e: app_commands.AppCommandError
    ):
        if "String value did not match validation regex" in str(e):
            await i.followup.send(
                "❌ Invalid emoji name; you have unsupported characters in the emoji name."
            )
        elif "Must be between 2 and 32 in length" in str(e):
            await i.followup.send("❌ The emoji name must be 2 to 32 characters long.")
        elif "Maximum number of emojis reached" in str(e):
            await i.followup.send("❌ This server has reached its emoji limit.")
        elif "Failed to resize asset below the maximum size" in str(
            e
        ) or "File cannot be larger than" in str(e):
            await i.followup.send(
                "❌ The image is too large to be resized to an emoji."
            )
        elif "Unsupported image type given" in str(e):
            await i.followup.send(
                "❌ URL must directly point to a PNG, JPEG, GIF or WEBP."
            )
        elif "cannot identify image file" in str(e):
            await i.followup.send(
                "❌ Invalid image type. Supported types are PNG, JPEG, GIF and WEBP."
            )
        else:
            return

        # if we reach here, the error was handled
        e.add_note("handled")


async def setup(bot):
    await bot.add_cog(Moderator(bot))
