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
        if i.user.id != self.target.id:
            await i.response.send_message("❌ This is not for you.", ephemeral=True)
            return
        self.accepted = True
        self.stop()

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red)
    async def reject(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.target.id:
            await i.response.send_message("❌ This is not for you.", ephemeral=True)
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

    @discord.ui.button(label="License", emoji=f"<:_:{config['emojis']['license']}>")
    async def license(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            """1Bot - a free Discord bot to let you get things done without leaving Discord.
Copyright (C) 2024-present thatjar

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
""",
            ephemeral=True,
        )
