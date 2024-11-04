# This file is a cog to handle command errors


import sys

import discord
from discord import app_commands
from discord.ext import commands

sys.path.insert(0, "/")  # to get access to config module
from config import config


class ErrorButton(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label="Join the Server",
                url=bot.server_invite,
                emoji=bot.get_emoji(config["emojis"]["support"]),
            )
        )


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    def cog_load(self):
        # attaching the handler when the cog is loaded and storing the old handler
        tree = self.bot.tree
        self._old_tree_error = tree.on_error
        tree.on_error = self.tree_on_error

    # automatically report exceptions that are not handled by the cog
    async def report_unknown_exception(self, i: discord.Interaction, error):
        error_embed = discord.Embed(
            title="❌ Unhandled error",
            description="Oops, looks like that command returned an unknown error. The error has been automatically reported.\n",
            colour=0xFF0000,
        )
        error_embed.add_field(
            name="Join our server to track this error",
            value="If you would like to see more about this error and our progress on fixing it, join our server.",
        )

        # Embed to send to error channel
        embed = (
            discord.Embed(
                title="Error",
                colour=0xFF0000,
                description=f"Error while invoking command `/{i.command.name}`",
            )
            .add_field(name="Error:", value=error)
            .set_footer(text=f"User ID: {i.user.id}")
        )

        if i.namespace:
            for option, value in i.namespace:
                embed.add_field(
                    name=f"Param: {option}", value=f"Value: {value}", inline=False
                )

        await self.bot.error_channel.send(embed=embed)
        try:
            await i.response.send_message(
                embed=error_embed, ephemeral=True, view=ErrorButton(self.bot)
            )
        except discord.InteractionResponded:
            await i.followup.send(
                embed=error_embed, ephemeral=True, view=ErrorButton(self.bot)
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        else:
            print(error)

    async def tree_on_error(self, i: discord.Interaction, error):
        if isinstance(error, app_commands.CommandNotFound):
            return

        elif isinstance(error, app_commands.CommandInvokeError):
            if isinstance(error.original, ValueError):
                try:
                    await i.response.send_message(
                        f"❌ {error.original}", ephemeral=True
                    )
                except discord.InteractionResponded:
                    await i.followup.send(f"❌ {error.original}", ephemeral=True)
            else:
                await self.report_unknown_exception(i, error.original)
        elif isinstance(error, app_commands.BotMissingPermissions):
            msg = (
                "❌ I don't have enough permissions to run this command!\n"
                + f"Missing permissions: `{', '.join([perm.title().replace('_', ' ') for perm in error.missing_permissions])}`\n\n"
                + f"Please add these permissions to my role ('{self.bot.user.global_name}') in your server settings."
            )
            try:
                await i.response.send_message(msg, ephemeral=True)
            except discord.InteractionResponded:
                await i.followup.send(msg, ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            msg = (
                "❌ You don't have enough permissions to use this command.\n"
                + f"Required permissions: `{', '.join([perm.title().replace('_', ' ') for perm in error.missing_permissions])}`"
            )
            try:
                await i.response.send_message(msg, ephemeral=True)
            except discord.InteractionResponded:
                await i.followup.send(msg, ephemeral=True)
        elif isinstance(error, app_commands.CommandOnCooldown):
            msg = f"❌ This command is on cooldown, try again in {round(error.retry_after, 1)} seconds."
            try:
                await i.response.send_message(msg, ephemeral=True)
            except discord.InteractionResponded:
                await i.followup.send(msg, ephemeral=True)
        elif isinstance(error, discord.Forbidden) or "Forbidden" in str(error):
            msg = "❌ **No Access**. Check if my roles are high enough in the list, and if I have permissions in the channel I need to access (if any)."
            try:
                await i.response.send_message(msg, ephemeral=True)
            except discord.InteractionResponded:
                await i.followup.send(msg, ephemeral=True)
        elif "cannot identify image file" in str(
            error
        ) or "Unsupported image type" in str(error):
            try:
                await i.response.send_message(
                    "❌ Image may be malformed.", ephemeral=True
                )
            except discord.InteractionResponded:
                await i.followup.send("❌ Image may be malformed.", ephemeral=True)
        elif isinstance(error, discord.HTTPException):
            if error.status == 429:
                if error.response.content["global"]:
                    print(
                        "GLOBAL RATELIMIT\n"
                        + f"Retry after:{error.response.content['retry_after']}\n"
                        + f"Caused by: {i.user}"
                    )

        else:
            await self.report_unknown_exception(i, error)


async def setup(bot):
    await bot.add_cog(Errors(bot))
