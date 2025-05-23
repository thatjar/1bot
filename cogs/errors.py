# An extension to handle command errors


import logging
from contextlib import suppress
from traceback import format_exception
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import MISSING

from config import config
from utils.utils import GenericError

if TYPE_CHECKING:
    from main import OneBot


class ErrorButton(discord.ui.View):
    """A view with a button to join the support server, if its url is configured."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if config.get("server_invite"):
            self.add_item(
                discord.ui.Button(
                    label="Join the Server",
                    url=config["server_invite"],
                    emoji=f"<:_:{config.get('emojis', {}).get('support', 0)}>",
                )
            )


class Errors(commands.Cog):
    """Cog to handle command errors. Does not contain any commands."""

    def __init__(self, bot):
        self.bot: OneBot = bot
        self.error_channel = None

    async def cog_load(self):
        if config.get("error_channel"):
            self.error_channel = await self.bot.fetch_channel(config["error_channel"])
        # attaching the handler when the cog is loaded and storing the old handler
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.tree_on_error

    @staticmethod
    def create_error_embed(
        i: discord.Interaction, error: app_commands.AppCommandError
    ) -> discord.Embed:
        """Creates an error report embed from an interaction and its error."""

        formatted_error = "".join(format_exception(error))
        # Leave room for other parts of embed description
        if len(formatted_error) > 4000:
            # Truncate from the beginning to preserve the error message at the end
            truncated = "...[truncated]...\n" + formatted_error[-4000:]
            traceback_str = "```py\n" + truncated + "```"
        else:
            traceback_str = "```py\n" + formatted_error + "```"

        embed = discord.Embed(
            title="Error",
            colour=0xFF0000,
            description=f"Error while invoking command `{i.command.name}`:\n{traceback_str}",
        )
        embed.add_field(name="Via user install?", value=i.is_user_integration())
        embed.add_field(name="Used in guild?", value=i.guild is not None)
        if hasattr(i.command, "type"):
            embed.add_field(name="Command type", value=i.command.type)
        else:
            embed.add_field(name="Command type", value="Slash")
        embed.set_footer(text=f"User ID: {i.user.id}")

        if i.namespace:
            for option, value in i.namespace:
                embed.add_field(
                    name=f"Param: {option}", value=f"Value: {value}", inline=False
                )

        return embed

    async def report_unknown_exception(
        self, i: discord.Interaction, error: app_commands.AppCommandError
    ) -> None:
        """Reports an unknown exception to the error channel and send an error message to the user."""

        user_embed = discord.Embed(
            title="⚠️ Unexpected error",
            description="An unknown error was encountered. It has been automatically reported.",
            colour=0xFF0000,
        )
        if config.get("server_invite"):
            user_embed.description += "\nIf you would like to know more about this error and the progress on addressing it, join the server."

        if self.error_channel:
            report_embed = self.create_error_embed(i, error)
            await self.error_channel.send(embed=report_embed)

        else:
            logging.error(
                f"In command '{i.command.name}': {''.join(format_exception(error))}"
            )

        try:
            await i.response.send_message(
                embed=user_embed, ephemeral=True, view=ErrorButton()
            )
        except discord.InteractionResponded:
            await i.followup.send(embed=user_embed, ephemeral=True, view=ErrorButton())

    @staticmethod
    async def send_error(
        i: discord.Interaction,
        error_message: str,
        view: discord.ui.View = MISSING,
    ) -> None:
        """Send an error message to the user."""

        try:
            await i.response.send_message(
                f"❌ {error_message}", ephemeral=True, view=view
            )
        except discord.InteractionResponded:
            await i.followup.send(f"❌ {error_message}", ephemeral=True, view=view)

    # Prefixed command error listener
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.NotOwner):
            return
        else:
            await ctx.reply(f"❌ {error}")

    # Main application command error handler
    async def tree_on_error(self, i: discord.Interaction, error: Exception) -> None:
        # Check if the error is already handled
        if "handled" in getattr(error, "__notes__", []):
            return

        if isinstance(
            error, app_commands.CommandNotFound
        ) or "Unknown interaction" in str(error):
            return
        elif isinstance(error, discord.NotFound):
            return
        elif "You are being rate limited" in str(error):
            return logging.warning(f"Rate limited: Command {i.command.name}")

        elif isinstance(error, app_commands.CommandSignatureMismatch):
            await self.send_error(
                i,
                "Command signature mismatch. Please report this to the developers.",
                view=ErrorButton(),
            )
        elif isinstance(error, app_commands.BotMissingPermissions):
            msg = (
                "I don't have enough permissions to run this command!\n"
                f"Missing permissions: `{', '.join([perm.title().replace('_', ' ') for perm in error.missing_permissions])}`\n\n"
                f"Please add these permissions to my role ('{self.bot.user.name}') in your server/channel settings."
            )
            await self.send_error(i, msg)
        elif isinstance(error, app_commands.MissingPermissions):
            msg = (
                "You don't have enough permissions to use this command.\n"
                f"Required permissions: `{', '.join([perm.title().replace('_', ' ') for perm in error.missing_permissions])}`"
            )
            await self.send_error(i, msg)
        elif isinstance(error, app_commands.CommandOnCooldown):
            msg = f"This command is on cooldown, try again in {error.retry_after:.1f} seconds."
            await self.send_error(i, msg)
        elif isinstance(error, app_commands.TransformerError):
            await self.send_error(i, error)
        elif isinstance(error, discord.Forbidden) or "Forbidden" in str(error):
            msg = "**No Access**. Check if my roles are high enough in the list, and if I have permissions in the channel I need to access (if any)."
            with suppress(discord.Forbidden):
                await self.send_error(i, msg)
        elif isinstance(error, discord.HTTPException):
            if error.status == 429:
                if error.response.content.get("global"):
                    logging.warning(
                        "GLOBAL RATELIMIT\n"
                        f"Retry after:{error.response.content['retry_after']}\n"
                        f"Caused by: {i.user.name} ({i.user.id})"
                    )

        elif isinstance(error, app_commands.CommandInvokeError):
            if isinstance(error.original, GenericError):
                await self.send_error(i, error.original)
            else:
                await self.report_unknown_exception(i, error.original)

        else:
            await self.report_unknown_exception(i, error)


async def setup(bot):
    await bot.add_cog(Errors(bot))
