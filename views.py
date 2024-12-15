import discord

from config import config


class Confirm(discord.ui.View):
    def __init__(self, target: discord.User, *args, **kwargs):
        super().__init__(*args, **kwargs, timeout=60)
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


class InfoButtons(discord.ui.View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if config.get("bot_invite"):
            self.add_item(
                discord.ui.Button(
                    label="Add to server",
                    url=config["bot_invite"],
                    emoji=f"<:_:{config.get('emojis', {}).get('add_to_server', 0)}>",
                )
            )

        if config.get("website"):
            self.add_item(
                discord.ui.Button(
                    label="Website",
                    url=config["website"],
                    emoji=f"<:_:{config.get('emojis', {}).get('website', 0)}>",
                )
            )

        if config.get("server_invite"):
            self.add_item(
                discord.ui.Button(
                    label="Server",
                    url=config["server_invite"],
                    emoji=f"<:_:{config.get('emojis', {}).get('support', 0)}>",
                )
            )
