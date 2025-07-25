# An extension to handle command errors

from __future__ import annotations

import logging
from contextlib import suppress
from traceback import format_exception
from typing import TYPE_CHECKING

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from config import config

if TYPE_CHECKING:
    from main import OneBot


class Support(discord.ui.View):
    """A view with a button to join the support server, if its url is configured."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if config.get("server_invite"):
            self.add_item(
                discord.ui.Button(
                    label="Join Support Server",
                    url=config["server_invite"],
                    emoji=f"<:_:{config.get('emojis', {}).get('support', 0)}>",
                )
            )


class Errors(commands.Cog):
    """Cog to handle command errors. Does not contain any commands."""

    def __init__(self, bot: OneBot):
        self.bot = bot
        self.error_channel = None

    async def cog_load(self):
        if config.get("error_channel"):
            self.error_channel = await self.bot.fetch_channel(config["error_channel"])
        # attaching the handler when the cog is loaded and storing the old handler
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.tree_on_error

    # prefixed command error handler
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.NotOwner):
            return
        else:
            await ctx.reply(f"❌ {error}")

    # actual app command error handling method
    async def tree_on_error(self, i: discord.Interaction, error: Exception) -> None:
        if "handled" in getattr(error, "__notes__", []):
            return

        if await self.handle(i, error):
            return

        elif isinstance(error, app_commands.CommandInvokeError):
            if isinstance(error.original, RuntimeError):
                await self.send_error(
                    i,
                    str(error.original)
                    or "Something went wrong. Please try again later.",
                )
            elif isinstance(error.original, aiohttp.ConnectionTimeoutError):
                await self.send_error(
                    i, "Connection timed out. Please try again later."
                )
            else:
                if not await self.handle(i, error.original):
                    await self.report_unknown_exception(i, error.original)

        else:
            await self.report_unknown_exception(i, error)

    async def handle(self, i: discord.Interaction, error: Exception) -> bool:
        """Send a corresponding error message for an exception, and return whether it was handled."""

        if isinstance(
            error, app_commands.CommandNotFound
        ) or "Unknown interaction" in str(error):
            return True
        elif isinstance(error, discord.NotFound):
            return True
        elif "You are being rate limited" in str(error):
            return logging.warning(f"Rate limited: Command {i.command.name}")

        elif isinstance(error, app_commands.CommandSignatureMismatch):
            await self.send_error(
                i,
                "Command signature mismatch. Please report this to the developers.",
                view=Support(),
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
                        "RATELIMIT\n"
                        f"Retry after:{error.response.content['retry_after']}"
                    )
        else:
            return False

        # if we reach here, the error was handled
        return True

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

        if self.error_channel:
            report_embed = self.create_error_embed(i, error)
            await self.error_channel.send(embed=report_embed)

        else:
            logging.error(
                f"In command '{i.command.name}': {''.join(format_exception(error))}"
            )

        user_embed = discord.Embed(
            title="⚠️ Unexpected error",
            description="An unknown error was encountered. It has been automatically reported.",
            colour=0xFF0000,
        )
        if config.get("server_invite"):
            user_embed.description += "\nIf you would like to know more about this error and the progress on addressing it, join the server."

        try:
            await i.response.send_message(
                embed=user_embed, ephemeral=True, view=Support()
            )
        except discord.InteractionResponded:
            await i.followup.send(embed=user_embed, ephemeral=True, view=Support())

    @staticmethod
    async def send_error(
        i: discord.Interaction,
        error_message: str,
        view: discord.ui.View = discord.utils.MISSING,
    ) -> None:
        """Send an error message to the user."""

        try:
            await i.response.send_message(
                f"❌ {error_message}", ephemeral=True, view=view
            )
        except discord.InteractionResponded:
            await i.followup.send(f"❌ {error_message}", ephemeral=True, view=view)
