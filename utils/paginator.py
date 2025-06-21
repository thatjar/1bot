import discord
from discord import Interaction
from discord.ui import Button, View


class Paginator(View):
    def __init__(
        self,
        *,
        interaction: Interaction,
        pages: list[discord.Embed],
        timeout: int = 60,
        message_content: str | None = None,
    ):
        """Paginator with back, forward, jump, and stop buttons.

        :param interaction: The interaction to respond to.
        :type interaction: discord.Interaction
        :param pages: List of embeds to paginate through.
        :type pages: List[discord.Embed]
        :param timeout: Timeout for the paginator view, defaults to 60 seconds.
        :type timeout: Optional[int]
        :param message_content: Message to send with the embeds.
        :type message_content: Optional[str]
        """

        super().__init__(timeout=timeout)
        self.interaction = interaction
        self.pages = pages
        self.current_page: int = 0
        self.total_pages: int = len(pages)
        self.message: discord.Message | None = None
        self.message_content = message_content
        self.update_jump_button()

    def update_jump_button(self):
        """Update the jump button label to show current page number."""
        self.jump_button.label = f"{self.current_page + 1} / {self.total_pages}"

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user != self.interaction.user:
            await interaction.response.defer()
            return False
        return True

    async def start(self) -> None:
        embed = self.pages[0]
        try:
            await self.interaction.response.send_message(
                self.message_content, embed=embed, view=self
            )
        except discord.InteractionResponded:
            await self.interaction.followup.send(
                self.message_content, embed=embed, view=self
            )

        self.message = await self.interaction.original_response()

    async def on_timeout(self) -> None:
        if self.message:
            await self.message.edit(view=None)

    async def on_error(self, interaction, error, item):
        if isinstance(error, discord.NotFound):
            return

    @discord.ui.button(emoji="⬅️")
    async def previous_button(self, i: Interaction, _: Button) -> None:
        self.current_page = (self.current_page - 1) % self.total_pages
        await self.update_page(i)

    @discord.ui.button(style=discord.ButtonStyle.blurple)
    async def jump_button(self, i: Interaction, _: Button) -> None:
        modal = PageSelectModal(self)
        await i.response.send_modal(modal)

    @discord.ui.button(emoji="➡️")
    async def next_button(self, i: Interaction, _: Button) -> None:
        self.current_page = (self.current_page + 1) % self.total_pages
        await self.update_page(i)

    @discord.ui.button(emoji="⏹️", style=discord.ButtonStyle.red)
    async def stop_button(self, i: Interaction, _: Button) -> None:
        await i.response.edit_message(view=None)
        self.stop()

    async def update_page(self, i: Interaction | None = None) -> None:
        embed = self.pages[self.current_page]
        self.update_jump_button()

        if i:
            await i.response.edit_message(embed=embed, view=self)
        elif self.message:
            await self.message.edit(embed=embed, view=self)


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
