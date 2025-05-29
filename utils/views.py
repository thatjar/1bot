import discord

from config import config


class Confirm(discord.ui.View):
    """Creates Accept and Reject buttons

    :param target: the User to confirm with
    :type target: discord.User
    :param timeout: View timeout
    :type timeout: float"""

    def __init__(self, target: discord.User, timeout=60, *args, **kwargs):
        super().__init__(*args, **kwargs, timeout=timeout)
        self.target = target
        self.accepted = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, i: discord.Interaction, _: discord.ui.Button):
        await i.response.defer(ephemeral=True)
        if i.user.id != self.target.id:
            await i.followup.send("❌ This is not for you.", ephemeral=True)
            return
        self.accepted = True
        self.stop()

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, i: discord.Interaction, _: discord.ui.Button):
        await i.response.defer(ephemeral=True)
        if i.user.id != self.target.id:
            await i.followup.send("❌ This is not for you.", ephemeral=True)
            return
        self.accepted = False
        self.stop()

    async def on_error(self, interaction, error, item):
        if isinstance(error, discord.NotFound):
            return


class InfoButtons(discord.ui.View):
    """Link buttons for the bot's website, support server, and invite link as configured in config.py"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        emoji_id = config.get("emojis", {}).get("wiki")
        if emoji_id:
            emoji = f"<:_:{emoji_id}>"
        else:
            emoji = "📖"

        self.add_item(
            discord.ui.Button(
                label="Wiki", url="https://github.com/thatjar/1bot/wiki", emoji=emoji
            )
        )

        if config.get("bot_invite"):
            emoji_id = config.get("emojis", {}).get("add_bot")
            if emoji_id:
                emoji = f"<:_:{emoji_id}>"
            else:
                emoji = "➕"
            self.add_item(
                discord.ui.Button(label="Add Me", url=config["bot_invite"], emoji=emoji)
            )

        if config.get("website"):
            emoji_id = config.get("emojis", {}).get("website")
            if emoji_id:
                emoji = f"<:_:{emoji_id}>"
            else:
                emoji = "🌐"
            self.add_item(
                discord.ui.Button(label="Website", url=config["website"], emoji=emoji)
            )

        if config.get("server_invite"):
            emoji_id = config.get("emojis", {}).get("support")
            if emoji_id:
                emoji = f"<:_:{emoji_id}>"
            else:
                emoji = "💬"
            self.add_item(
                discord.ui.Button(
                    label="Server", url=config["server_invite"], emoji=emoji
                )
            )


class DeleteButton(discord.ui.View):
    def __init__(self, *allowed_users: discord.User):
        """Button to delete a command response from 1Bot.

        :param allowed_users: The users allowed to delete the message. Users with manage_messages permission can always delete the message.
        :type allowed_users: discord.User"""

        super().__init__(timeout=None)
        self.allowed_users = [u.id for u in allowed_users]

    @discord.ui.button(label="Delete", emoji="🗑️")
    async def delete(self, i: discord.Interaction, _: discord.ui.Button):
        if i.user.id in self.allowed_users or i.permissions.manage_messages:
            await i.response.defer(ephemeral=True)
            await i.edit_original_response(
                content=f"-# *Removed by {i.user.mention}*",
                view=None,
                embed=None,
                attachments=[],
                allowed_mentions=discord.AllowedMentions.none(),
            )
        else:
            await i.response.send_message("❌ You cannot delete this.", ephemeral=True)
            return
