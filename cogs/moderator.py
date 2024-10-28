import discord
from discord.ext import commands
from discord import app_commands


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

    @app_commands.command(name="purge", description="Bulk delete messages")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(
        manage_messages=True, read_message_history=True
    )
    @app_commands.describe(amount="The amount of messages to delete")
    async def purge(self, i: discord.Interaction, amount: int):
        await i.response.defer(ephemeral=True)
        deleted = await i.channel.purge(limit=amount)
        await i.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

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
            create_public_threads=False, create_private_threads=False
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

        await i.channel.edit(slowmode_delay=seconds)
        await i.followup.send(
            f"Slowmode set to {amount} {'seconds' if unit == 1 else unit.name}.",
            ephemeral=True,
        )


async def setup(bot):
    await bot.add_cog(Moderator(bot))
