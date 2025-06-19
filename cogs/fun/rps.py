import discord


class RPSButton(discord.ui.Button):
    def __init__(self, label: str, emoji: str):
        super().__init__(label=label, emoji=emoji)

    async def callback(self, i: discord.Interaction):
        view = self.view
        if i.user.id not in (view.p1.id, view.p2.id):
            await i.response.send_message(
                "❌ You are not part of this game.", ephemeral=True
            )
            return
        if view.choices.get(i.user.id):
            await i.response.send_message(
                f"❌ You have already chosen {view.choices[i.user.id]}.", ephemeral=True
            )
            return

        await i.response.defer()

        view.choices[i.user.id] = self.label
        if len(view.choices) == 2:
            if view.choices[view.p1.id] == view.choices[view.p2.id]:
                view.winner = None
            elif (
                view.choices[view.p1.id] == "Rock"
                and view.choices[view.p2.id] == "Scissors"
                or view.choices[view.p1.id] == "Paper"
                and view.choices[view.p2.id] == "Rock"
                or view.choices[view.p1.id] == "Scissors"
                and view.choices[view.p2.id] == "Paper"
            ):
                view.winner = view.p1
            else:
                view.winner = view.p2
            view.stop()


class RockPaperScissors(discord.ui.View):
    def __init__(self, p1: discord.User, p2: discord.User):
        super().__init__(timeout=60)
        self.p1 = p1
        self.p2 = p2
        self.choices = {}
        self.winner = None
        self.add_item(RPSButton(label="Rock", emoji="🪨"))
        self.add_item(RPSButton(label="Paper", emoji="📄"))
        self.add_item(RPSButton(label="Scissors", emoji="✂️"))
