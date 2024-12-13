import discord
from discord.ext import commands

from config import config


class Confirm(discord.ui.View):
    def __init__(self, target: discord.User):
        super().__init__(timeout=60)
        self.target = target
        self.accepted = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, i: discord.Interaction, button: discord.ui.Button):
        await i.response.defer(ephemeral=True)
        if i.user.id != self.target.id:
            await i.followup.send("❌ This is not for you.", ephemeral=True)
            return
        self.accepted = True
        self.stop()

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, i: discord.Interaction, button: discord.ui.Button):
        await i.response.defer(ephemeral=True)
        if i.user.id != self.target.id:
            await i.followup.send("❌ This is not for you.", ephemeral=True)
            return
        self.accepted = False
        self.stop()


class InfoButtons(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label="Add to server",
                url=config["bot_invite"],
                emoji=f"<:_:{config['emojis']['add_to_server']}>",
            )
        )
        self.add_item(
            discord.ui.Button(
                label="Website",
                url=bot.website_url,
                emoji=f"<:_:{config['emojis']['website']}>",
            )
        )
        self.add_item(
            discord.ui.Button(
                label="Server",
                url=bot.server_invite,
                emoji=f"<:_:{config['emojis']['support']}>",
            )
        )
