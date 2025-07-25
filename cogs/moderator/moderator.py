from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from utils.utils import Embed

if TYPE_CHECKING:
    from main import OneBot


class Moderator(commands.Cog):
    def __init__(self, bot: OneBot):
        self.bot = bot

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
                        name="@" + i.user.name, icon_url=i.user.display_avatar.url
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
    async def purge(
        self, i: discord.Interaction, count: app_commands.Range[int, 1, 100]
    ):
        await i.response.defer(ephemeral=True)
        oldest = datetime.now(UTC) - timedelta(days=14)
        messages_to_delete = []

        async for message in i.channel.history(
            limit=100, oldest_first=False, after=oldest
        ):
            messages_to_delete.append(message)
            if len(messages_to_delete) >= count:
                break

        if not messages_to_delete:
            raise RuntimeError(
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

        oldest = datetime.now(UTC) - timedelta(days=14)
        messages_to_delete = []

        async for message in i.channel.history(oldest_first=False, after=oldest):
            if message.author.bot:
                messages_to_delete.append(message)
            if len(messages_to_delete) >= count:
                break

        if not messages_to_delete:
            raise RuntimeError(
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

        oldest = datetime.now(UTC) - timedelta(days=14)
        messages_to_delete = []

        async for message in i.channel.history(oldest_first=False, after=oldest):
            if not message.author.bot:
                messages_to_delete.append(message)
            if len(messages_to_delete) >= count:
                break

        if not messages_to_delete:
            raise RuntimeError(
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
        user: discord.Member,
        count: app_commands.Range[int, 1, 100],
    ):
        await i.response.defer(ephemeral=True)

        oldest = datetime.now(UTC) - timedelta(days=14)
        messages_to_delete = []

        async for message in i.channel.history(oldest_first=False, after=oldest):
            if message.author == user:
                messages_to_delete.append(message)
            if len(messages_to_delete) >= count:
                break

        if not messages_to_delete:
            raise RuntimeError(
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
        self,
        i: discord.Interaction,
        role: discord.Role | None = None,
        reason: str | None = None,
    ):
        await i.response.defer(ephemeral=True)
        role = role or i.guild.default_role

        try:
            overwrite = i.channel.overwrites_for(role)
        except AttributeError:
            raise RuntimeError("This command cannot be used on a thread.")
        if overwrite.create_public_threads is overwrite.create_private_threads is False:
            raise RuntimeError(
                f"This channel already has disabled threads for `{role.name}`."
            )

        overwrite.create_public_threads = False
        overwrite.create_private_threads = False

        # reason string that appears in audit log
        reason = reason or "disabled threads"

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
                raise RuntimeError("This channel has no slowmode.")
            seconds = i.channel.slowmode_delay
            await i.response.send_message(f"Current slowmode: **{seconds} seconds**")
            return

        seconds = amount if unit == 1 else amount * unit.value

        if not 0 <= seconds <= 21600:
            raise RuntimeError("Slowmode must be between 0 and 6 hours.")
        await i.response.defer(ephemeral=True)

        await i.channel.edit(
            slowmode_delay=seconds, reason=f"{i.user.name} set slowmode"
        )
        await i.followup.send(
            f"✅ Slowmode set to {int(seconds)} seconds.",
            ephemeral=True,
        )

    # lock
    @app_commands.command(name="lock", description="Make the channel read-only")
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
        role: discord.Role | None = None,
        reason: str | None = None,
        silent: bool = False,
    ):
        await i.response.defer(ephemeral=True)
        role = role or i.guild.default_role

        try:
            overwrite = i.channel.overwrites_for(role)
        except AttributeError:
            raise RuntimeError("This command cannot be used on a thread.")

        if (
            overwrite.send_messages
            is overwrite.create_public_threads
            is overwrite.create_private_threads
            is False
        ):
            raise RuntimeError(f"This channel is already locked for `{role.name}`.")

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
        embed = Embed(
            title="Channel Locked",
            color=0xFF0000,
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
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
        role: discord.Role | None = None,
        reason: str | None = None,
        silent: bool = False,
    ):
        await i.response.defer(ephemeral=True)
        role = role or i.guild.default_role

        try:
            overwrite = i.channel.overwrites_for(role)
        except AttributeError:
            raise RuntimeError("This command cannot be used on a thread.")

        if (
            overwrite.send_messages
            is overwrite.create_public_threads
            is overwrite.create_private_threads
            in (None, True)
        ):
            raise RuntimeError(f"This channel is already unlocked for `{role.name}`.")

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
        embed = Embed(
            title="Channel Unlocked",
            color=self.bot.colour,
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
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
        reason: str | None = None,
        silent: bool = False,
    ):
        if user == i.user:
            raise RuntimeError("You cannot time out yourself.")
        if user == i.guild.me:
            raise RuntimeError("I cannot time out myself.")
        if user.top_role >= i.user.top_role:
            raise RuntimeError(
                "You cannot time out a user with a higher or equal role than you."
            )

        total_minutes = days * 1440 + hours * 60 + minutes
        if not 0 <= total_minutes <= 40320:
            raise RuntimeError("Timeout duration must be between 0 and 28 days.")

        # reason string that appears in audit log
        log_reason = reason or f"{i.user.name}: No reason specified"
        # if total_minutes is 0, pass None for a proper removal of timeout and audit log message
        await user.timeout(
            timedelta(minutes=total_minutes) if total_minutes else None,
            reason=log_reason,
        )

        embed = Embed(
            title="User Timed Out",
            description=f"🕒 {user.mention} has been timed out for {days} days, {hours} hours and {minutes} minutes.",
            color=self.bot.colour,
        )
        if reason:
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
        delete_days="Number of days of messages to delete (default: 0 days, 1 hour)",
        delete_hours="Number of hours of messages to delete (default: 1 hour)",
        reason="The reason for banning the user (optional)",
        silent="Disable publicly sending the ban message & DMing the user (default: False)",
    )
    async def ban(
        self,
        i: discord.Interaction,
        user: discord.Member | discord.User,
        delete_days: int = 0,
        delete_hours: int = 1,
        reason: str | None = None,
        silent: bool = False,
    ):
        if user == i.user:
            raise RuntimeError("You cannot ban yourself.")
        if user == i.guild.me:
            raise RuntimeError("I cannot ban myself.")
        if delete_days * 86400 + delete_hours * 3600 > 604800:
            raise RuntimeError("Total duration must be between 0 and 7 days.")
        if isinstance(user, discord.Member):
            if user.top_role >= i.user.top_role:
                raise RuntimeError(
                    "You cannot ban a user with a higher or equal role than you."
                )

        # reason string that appears in audit log
        log_reason = reason or f"{i.user.name}: No reason specified"

        try:
            if not silent:
                dm_embed = Embed(
                    description=f"You have been banned from {i.guild.name}.",
                    color=0xFF0000,
                )
                if reason:
                    dm_embed.add_field(name="Reason", value=reason, inline=False)

                await user.send(embed=dm_embed)
        except (discord.Forbidden, discord.HTTPException):
            pass

        try:
            await i.guild.ban(
                user,
                reason=log_reason,
                delete_message_seconds=delete_days * 86400 + delete_hours * 3600,
            )
        except discord.Forbidden:
            raise RuntimeError("I do not have permission to ban that user.")

        embed = Embed(
            title="User Banned",
            description=f"🔨 {user.mention} has been banned.",
            color=self.bot.colour,
        )
        embed.add_field(name="Reason", value=reason, inline=False)
        if delete_days:
            embed.add_field(
                name="Messages Deleted", value=f"{delete_days} days", inline=False
            )

        await i.response.send_message(embed=embed, ephemeral=silent)
