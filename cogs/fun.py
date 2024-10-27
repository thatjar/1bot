import discord
from discord.ext import commands
from discord import app_commands
import requests

import random
from urllib.parse import quote_plus


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="quote", description="Create a quote image")
    @app_commands.describe(
        quote="The quote", user="The author of the quote (default: yourself)"
    )
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def quote(
        self, i: discord.Interaction, quote: str, user: discord.Member = None
    ):
        if user is None:
            user = i.user
        if len(quote) > 100:
            await i.response.send_message("❌ The quote is too long.", ephemeral=True)
        embed = discord.Embed(
            colour=self.bot.colour,
            title=f"a beautiful quote from {user.name}",
        )
        embed.set_image(
            url=f"https://api.popcat.xyz/quote?image={quote_plus(user.display_avatar.url)}&text={quote_plus(quote)}&name={quote_plus(user.name)}"
        )

        await i.response.send_message(embed=embed)

    @app_commands.command(name="pickupline", description="Get a pickup line")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.channel)
    async def pickupline(self, i: discord.Interaction):
        r = requests.get("https://api.popcat.xyz/pickuplines")
        pickupline = r.json()["pickupline"]
        await i.response.send_message(pickupline)

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
    async def coinflip(self, i: discord.Interaction):
        await i.response.send_message(
            f"🪙 Flipped a coin for you, it's **{random.choice(('heads', 'tails'))}**!"
        )

    @app_commands.command(name="dice", description="Roll dice")
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
