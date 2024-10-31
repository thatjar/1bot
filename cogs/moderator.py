import discord
from discord.ext import commands
from discord import app_commands

from datetime import datetime, timedelta


class EmbedSetup(discord.ui.Modal, title="Embed Setup"):
    def __init__(self):
        super().__init__(timeout=300)

    embed_title = discord.ui.TextInput(label="Title", max_length=256)
    contents = discord.ui.TextInput(
        label="Contents",
        placeholder="Markdown supported",
        max_length=1024,
        style=discord.TextStyle.paragraph,
    )
    thumbnail = discord.ui.TextInput(
        label="Thumbnail", placeholder="URL", required=False
    )
    image = discord.ui.TextInput(label="Main Image", placeholder="URL", required=False)
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
            embed.set_author(name=i.user.display_name, icon_url=i.user.avatar.url)
        await i.channel.send(embed=embed)
        await i.response.send_message("Sent.", ephemeral=True)


class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="embed", description="Create a rich embed")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True)
    async def embed(self, i: discord.Interaction):
        await i.response.send_modal(EmbedSetup())

    purge_group = app_commands.Group(name="purge", description="Bulk delete messages")

    @purge_group.command(name="any", description="Bulk delete messages of any type")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.checks.bot_has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.describe(count="The number of messages to delete")
    async def purge(self, i: discord.Interaction, count: int):
        await i.response.defer(ephemeral=True)
        deleted = await i.channel.purge(
            limit=count,
            after=datetime.utcnow() - timedelta(14),
            oldest_first=False,
            reason=f"Purged by {i.user.name}",
        )
        await i.followup.send(f"Found and deleted {len(deleted)} messages.")

    @purge_group.command(
        name="bots", description="Bulk delete messages sent by bots only"
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.checks.bot_has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.describe(count="The number of messages to search through")
    async def purgebots(self, i: discord.Interaction, count: int):
        await i.response.defer(ephemeral=True)
        deleted = await i.channel.purge(
            limit=count,
            after=datetime.utcnow() - timedelta(14),
            oldest_first=False,
            check=lambda m: m.author.bot,
            reason=f"Purged by {i.user.name}",
        )
        await i.followup.send(f"Found and deleted {len(deleted)} messages from bots.")

    @purge_group.command(
        name="humans", description="Bulk delete messages sent by humans only"
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.checks.bot_has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.describe(count="The number of messages to search through")
    async def purgehumans(self, i: discord.Interaction, count: int):
        await i.response.defer(ephemeral=True)
        deleted = await i.channel.purge(
            limit=count,
            after=datetime.utcnow() - timedelta(14),
            oldest_first=False,
            check=lambda m: not m.author.bot,
            reason=f"Purged by {i.user.name}",
        )
        await i.followup.send(f"Found and deleted {len(deleted)} messages from humans.")

    @purge_group.command(name="user", description="Bulk delete messages sent by a user")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.checks.bot_has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.describe(
        user="The user to search for", count="The number of messages to search through"
    )
    async def purgeuser(self, i: discord.Interaction, user: discord.User, count: int):
        await i.response.defer(ephemeral=True)
        deleted = await i.channel.purge(
            limit=count,
            after=datetime.utcnow() - timedelta(14),
            oldest_first=False,
            check=lambda m: m.author == user,
            reason=f"Purged by {i.user.name}",
        )
        await i.followup.send(f"Found and deleted {len(deleted)} messages from {user}.")

    @app_commands.command(
        name="disablethreads", description="Remove permissions to create threads"
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.describe(
        role="The role to remove permissions from (default: @everyone)",
        channel="The channel to remove permissions from (default: current channel)",
    )
    async def disablethreads(
        self,
        i: discord.Interaction,
        role: discord.Role = None,
        channel: discord.TextChannel = None,
    ):
        if role is None:
            role = i.guild.default_role
        if channel is None:
            channel = i.channel

        await i.response.send_message("Disabling threads...", ephemeral=True)
        overwrite = discord.PermissionOverwrite(
            create_public_threads=False,
            create_private_threads=False,
            reason=f"{i.user.name} disabled threads",
        )
        await channel.set_permissions(role, overwrite=overwrite)
        await i.followup.send("Done.", ephemeral=True)

    @app_commands.command(name="slowmode", description="Set slowmode")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.checks.cooldown(3, 20, key=lambda i: i.channel)
    @app_commands.describe(
        amount="The amount of seconds to slowmode (default: 0)",
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
        amount: float = 0.0,
        unit: app_commands.Choice[int] = 1,
    ):
        await i.response.defer(ephemeral=True)

        seconds = amount if unit == 1 else amount * unit.value

        if seconds < 0 or seconds > 21600:
            await i.response.send_message(
                "❌ Slowmode must be between 0 and 6 hours.",
                ephemeral=True,
            )
            return

        await i.channel.edit(
            slowmode_delay=seconds, reason=f"{i.user.name} set slowmode"
        )
        await i.followup.send(
            f"Slowmode set to {amount} {'seconds' if unit == 1 else unit.name}.",
            ephemeral=True,
        )

    @app_commands.command(name="lock", description="Make a channel read-only")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.describe(
        channel="The channel to lock (default: current channel)",
        reason="The reason for locking the channel",
    )
    async def lock(
        self,
        i: discord.Interaction,
        channel: discord.TextChannel = None,
        reason: str = None,
    ):
        if channel is None:
            channel = i.channel
        await i.response.send_message("Locking channel...", ephemeral=True)
        await channel.set_permissions(
            i.guild.default_role,
            send_messages=False,
            create_public_threads=False,
            create_private_threads=False,
            reason=reason,
        )
        await i.followup.send("Done.")

    @app_commands.command(
        name="unlock", description="Undo the lock command (allow users to message)"
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.describe(
        channel="The channel to unlock (default: current channel)",
        reason="The reason for unlocking the channel",
    )
    async def unlock(
        self,
        i: discord.Interaction,
        channel: discord.TextChannel = None,
        reason: str = None,
    ):
        if channel is None:
            channel = i.channel
        await i.response.send_message("Unlocking channel...", ephemeral=True)
        await channel.set_permissions(
            i.guild.default_role,
            send_messages=None,
            create_public_threads=None,
            create_private_threads=None,
            reason=reason,
        )
        await i.followup.send("Done.")


async def setup(bot):
    await bot.add_cog(Moderator(bot))
