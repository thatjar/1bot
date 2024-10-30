import discord
from discord.ext import commands
from discord import app_commands
import requests

import random
from urllib.parse import quote_plus


class RockPaperScissors(discord.ui.View):
    def __init__(self, p1: discord.User, p2: discord.User):
        super().__init__(timeout=60)
        self.p1 = p1
        self.p2 = p2
        self.p1_choice = None
        self.p2_choice = None

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.primary, emoji="🪨")
    async def rock(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id == self.p1.id:
            if self.p1_choice is not None:
                await i.response.send_message(
                    f"❌ You have already chosen {self.p1_choice}.", ephemeral=True
                )
                return

            self.p1_choice = "rock"

        elif i.user.id == self.p2.id:
            if self.p2_choice is not None:
                await i.response.send_message(
                    f"You have already chosen {self.p2_choice}.", ephemeral=True
                )
                return

            self.p2_choice = "rock"

        else:
            await i.response.send_message(
                "❌ You are not part of this game.", ephemeral=True
            )
            return

        await self.check_winner(i)

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.primary, emoji="📄")
    async def paper(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id == self.p1.id:
            if self.p1_choice is not None:
                await i.response.send_message(
                    f"❌ You have already chosen {self.p1_choice}.", ephemeral=True
                )
                return

            self.p1_choice = "paper"

        elif i.user.id == self.p2.id:
            if self.p2_choice is not None:
                await i.response.send_message(
                    f"You have already chosen {self.p2_choice}.", ephemeral=True
                )
                return

            self.p2_choice = "paper"

        else:
            await i.response.send_message(
                "❌ You are not part of this game.", ephemeral=True
            )
            return

        await self.check_winner(i)

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.primary, emoji="✂")
    async def scissors(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id == self.p1.id:
            if self.p1_choice is not None:
                await i.response.send_message(
                    f"❌ You have already chosen {self.p1_choice}.", ephemeral=True
                )
                return

            self.p1_choice = "scissors"

        elif i.user.id == self.p2.id:
            if self.p2_choice is not None:
                await i.response.send_message(
                    f"You have already chosen {self.p2_choice}.", ephemeral=True
                )
                return

            self.p2_choice = "scissors"

        else:
            await i.response.send_message(
                "❌ You are not part of this game.", ephemeral=True
            )
            return

        await self.check_winner(i)

    async def check_winner(self, i: discord.Interaction):
        if self.p1_choice is not None and self.p2_choice is not None:
            if self.p1_choice == self.p2_choice:
                self.winner = None
                self.stop()
            elif (
                self.p1_choice == "rock"
                and self.p2_choice == "scissors"
                or self.p1_choice == "paper"
                and self.p2_choice == "rock"
                or self.p1_choice == "scissors"
                and self.p2_choice == "paper"
            ):
                self.winner = self.p1
                self.stop()
            else:
                self.winner = self.p2
                self.stop()


class Challenge(discord.ui.View):
    def __init__(self, target: discord.User):
        super().__init__(timeout=60)
        self.target = target
        self.accepted = None

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, i: discord.Interaction, button: discord.ui.Button):
        if i.user.id != self.target.id:
            await i.response.send_message(
                "❌ This invitation is not for you!", ephemeral=True
            )
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


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.bot.tree.add_command(
            app_commands.ContextMenu(name="Quote", callback=self.quote_ctx)
        )

    @app_commands.command(
        name="rockpaperscissors",
        description="Play Rock Paper Scissors with another user",
    )
    @app_commands.guild_only()
    @app_commands.describe(user="The user to play with")
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    async def rps(self, i: discord.Interaction, user: discord.User):
        if i.user.id == user.id:
            await i.response.send_message(
                "❌ You can't play with yourself!", ephemeral=True
            )
            return
        elif user.bot:
            await i.response.send_message(
                "❌ You can't play with a bot!", ephemeral=True
            )
            return

        view = Challenge(user)
        await i.response.defer()
        first_msg = await i.followup.send(
            f"{user.mention}, you have been challenged to **Rock Paper Scissors** by {i.user.mention}! Respond within 60 seconds.",
            view=view,
        )
        await view.wait()
        if view.accepted is True:
            view = RockPaperScissors(i.user, user)
            embed = discord.Embed(
                title="Rock Paper Scissors",
                description=f"### {i.user.mention} vs {user.mention}\nWaiting for players to choose...",
                colour=self.bot.colour,
            )
            await first_msg.edit(content=None, embed=embed, view=view)
            await view.wait()
            if view.winner is not None:
                winning_choice = (
                    view.p1_choice if view.winner == view.p1 else view.p2_choice
                )
                losing_choice = (
                    view.p2_choice if view.winner == view.p1 else view.p1_choice
                )
                embed.description = f"### {view.winner.mention} is the **winner!**"
                embed.add_field(name="Winning pick:", value=winning_choice)
                embed.add_field(name="Losing pick:", value=losing_choice)
                await first_msg.edit(embed=embed, view=None)
            else:
                embed.description = "### It's a tie!"
                embed.add_field(name="Both players chose:", value=view.p1_choice)
                await first_msg.edit(embed=embed, view=None)
        elif view.accepted is False:
            await first_msg.edit(
                content=f"The challenge was **rejected** by {user.mention}.",
                view=None,
            )
        elif view.accepted is None:
            await first_msg.edit(
                content=f"{i.user.mention} did not respond in time.",
                view=None,
            )

    @app_commands.checks.cooldown(1, 20, key=lambda i: i.channel)
    async def quote_ctx(self, i: discord.Interaction, message: discord.Message):
        await i.response.defer()
        if len(message.content) > 100:
            await i.followup.send("❌ The quote is too long.")
            return
        embed = discord.Embed(
            colour=self.bot.colour,
            title=f"a beautiful quote from {message.author.display_name}",
        )
        embed.set_image(
            url=f"https://api.popcat.xyz/quote?image={quote_plus(message.author.display_avatar.url)}&text={quote_plus(message.content)}&name={quote_plus(message.author.name)}"
        )

        await i.followup.send(embed=embed)

    @app_commands.command(name="quote", description="Create a quote image")
    @app_commands.describe(
        quote="The quote", user="The author of the quote (default: yourself)"
    )
    @app_commands.checks.cooldown(1, 20, key=lambda i: i.channel)
    async def quote(
        self, i: discord.Interaction, quote: str, user: discord.Member = None
    ):
        await i.response.defer()
        if user is None:
            user = i.user
        if len(quote) > 100:
            await i.followup.send("❌ The quote is too long.")
            return
        embed = discord.Embed(
            colour=self.bot.colour,
            title=f"a beautiful quote from {user.display_name}",
        )
        embed.set_image(
            url=f"https://api.popcat.xyz/quote?image={quote_plus(user.display_avatar.url)}&text={quote_plus(quote)}&name={quote_plus(user.name)}"
        )

        await i.followup.send(embed=embed)

    @app_commands.command(name="pickupline", description="Get a pickup line")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def pickupline(self, i: discord.Interaction):
        await i.response.defer()
        r = requests.get("https://api.popcat.xyz/pickuplines")
        pickupline = r.json()["pickupline"]
        await i.followup.send(pickupline)

    @app_commands.command(name="8ball", description="Ask the magic 8ball a question")
    @app_commands.describe(question="The question to ask")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.channel)
    async def _8ball(self, i: discord.Interaction, question: str):
        responses = [
            # Affirmative
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes, definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            # Non-committal
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not to tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            # Negative
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]
        fortune = random.choice(responses)
        embed = discord.Embed(
            colour=self.bot.colour,
            title=f'"{question}"',
            description="**🎱 The Magic 8ball says:**\n\n" + f"||{fortune}||",
        )
        await i.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def coinflip(self, i: discord.Interaction):
        await i.response.send_message(
            f"🪙 Flipped a coin for you, it's **{random.choice(('heads', 'tails'))}**!"
        )

    @app_commands.command(name="dice", description="Roll dice")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    @app_commands.describe(
        number="The number of dice to roll",
    )
    async def dice(self, i: discord.Interaction, number: int = 1):
        if number < 1 or number > 6:
            await i.response.send_message(
                "❌ Number of dice must be between 1 and 6", ephemeral=True
            )
            return
        rolls = random.sample(range(1, 7), number)
        await i.response.send_message(
            f"🎲 Rolled {number} dice: {', '.join([str(r) for r in rolls])}"
        )

    @app_commands.command(name="mock", description="Mock text")
    @app_commands.checks.cooldown(1, 15, key=lambda i: i.channel)
    @app_commands.describe(text="The text to mock")
    async def mock(self, i: discord.Interaction, text: str):
        mock_text = "".join(
            [char.upper() if i % 2 else char.lower() for i, char in enumerate(text)]
        )

        await i.response.send_message(
            mock_text, allowed_mentions=discord.AllowedMentions(users=False)
        )


async def setup(bot):
    await bot.add_cog(Fun(bot))
