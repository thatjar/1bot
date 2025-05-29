import discord
from discord import Interaction
from discord.ui import Button, View


class Paginator(View):
    def __init__(
        self, *, interaction: Interaction, pages: list[discord.Embed], timeout: int = 60
    ):
        """Paginator with back, forward, jump, and stop buttons.

        :param interaction: The interaction to respond to.
        :type interaction: discord.Interaction
        :param pages: List of embeds to paginate through. Must not have a footer.
        :type pages: List[discord.Embed]"""

        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.pages = pages
        self.current_page: int = 0
        self.total_pages: int = len(pages)
        self.message: discord.Message | None = None

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user != self.interaction.user:
            await interaction.response.send_message(
                "❌ This is not for you.", ephemeral=True
            )
            return False
        return True

    async def start(self) -> None:
        # Add footer to the first page
        embed = self.pages[0]
        if embed.footer.text:
            raise ValueError("Embed footer must not be set.")
        else:
            embed.set_footer(text=f"Result {self.current_page + 1}/{self.total_pages}")

        try:
            await self.interaction.response.send_message(embed=embed, view=self)
        except discord.InteractionResponded:
            await self.interaction.followup.send(embed=embed, view=self)

        self.message = await self.interaction.original_response()

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)

    async def on_error(self, interaction, error, item):
        if isinstance(error, discord.NotFound):
            return

    @discord.ui.button(emoji="⬅️", style=discord.ButtonStyle.green)
    async def previous_button(self, i: Interaction, _: Button) -> None:
        self.current_page = (self.current_page - 1) % self.total_pages
        await self.update_page(i)

    @discord.ui.button(emoji="🔢", style=discord.ButtonStyle.gray)
    async def jump_button(self, i: Interaction, _: Button) -> None:
        modal = PageSelectModal(self)
        await i.response.send_modal(modal)

    @discord.ui.button(emoji="➡️", style=discord.ButtonStyle.green)
    async def next_button(self, i: Interaction, _: Button) -> None:
        self.current_page = (self.current_page + 1) % self.total_pages
        await self.update_page(i)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.red)
    async def stop_button(self, i: Interaction, _: Button) -> None:
        await i.response.edit_message(view=None)
        self.stop()

    async def update_page(self, i: Interaction | None = None) -> None:
        embed = self.pages[self.current_page]
        if isinstance(embed, discord.Embed) and not embed.footer.text:
            embed.set_footer(text=f"Page {self.current_page + 1}/{self.total_pages}")

        if i:
            await i.response.edit_message(embed=embed)
        elif self.message:
            await self.message.edit(embed=embed)


class PageSelectModal(discord.ui.Modal, title="Jump to Page"):
    page_number = discord.ui.TextInput(
        label="Page Number", placeholder="Enter page number", min_length=1, max_length=5
    )

    def __init__(self, paginator: Paginator):
        super().__init__()
        self.paginator = paginator

    async def on_submit(self, i: Interaction) -> None:
        try:
            page = int(self.page_number.value)
            if 1 <= page <= self.paginator.total_pages:
                self.paginator.current_page = page - 1
                await i.response.defer()
                await self.paginator.update_page()
            else:
                await i.response.send_message(
                    f"Page must be between 1 and {self.paginator.total_pages}",
                    ephemeral=True,
                )
        except ValueError:
            await i.response.send_message(
                "Please enter a valid number.", ephemeral=True
            )
