import discord
from discord.ext import commands
from discord import app_commands


class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

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


async def setup(bot):
    await bot.add_cog(Moderator(bot))
