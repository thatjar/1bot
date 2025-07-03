from __future__ import annotations

import random
from datetime import UTC, datetime, timedelta
from io import BytesIO
from typing import TYPE_CHECKING, Literal
from urllib.parse import quote_plus

import discord
from aiohttp import ClientSession
from discord import app_commands
from discord.ext import commands

from utils.utils import Embed
from utils.views import Confirm, DeleteButton

from . import battleship
from .hangman import HangmanGame, HangmanView, CustomWordView, get_random_word
from .rps import RockPaperScissors
from .ttt import TicTacToe

if TYPE_CHECKING:
    from main import OneBot


class Fun(commands.Cog):
    def __init__(self, bot: OneBot):
        self.bot = bot
        self.bot.tree.add_command(
            app_commands.ContextMenu(name="Quote", callback=self.quote)
        )
        self.bot.tree.add_command(
            app_commands.ContextMenu(name="Mock", callback=self.mock_ctx),
        )
        self.bot.tree.add_command(
            app_commands.ContextMenu(name="Woosh", callback=self.woosh_ctx),
        )

    games = app_commands.Group(name="games", description="Play minigames")

    # tic tac toe
    @games.command(name="tictactoe", description="Play Tic Tac Toe with another user")
    @app_commands.describe(user="The user to play with")
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    async def tictactoe(self, i: discord.Interaction, user: discord.User):
        if i.guild and i.permissions.use_external_apps is False:
            raise RuntimeError("External apps are disabled in this channel.")
        if i.user.id == user.id:
            raise RuntimeError("You can't play with yourself!")
        if user.bot:
            raise RuntimeError("You can't play with a bot!")

        view = Confirm(user)
        expires = (datetime.now(UTC) + timedelta(seconds=61)).timestamp()
        await i.response.send_message(
            content=f"{user.mention}, you have been challenged to **Tic Tac Toe** by {i.user.mention}! Expires <t:{expires:.0f}:R>.",
            view=view,
        )
        await view.wait()
        if view.accepted is False:
            await i.edit_original_response(
                content=f"The challenge was **rejected** by {user.mention}.", view=None
            )
            return
        elif view.accepted is None:
            await i.edit_original_response(
                content=f"{user.mention} did not respond in time.", view=None
            )
            return

        view = TicTacToe(i.user, user)
        await i.edit_original_response(
            content=f"{i.user.mention} as **X** vs. {user.mention} as **O**", view=view
        )
        timed_out = await view.wait()
        if timed_out:
            await i.edit_original_response(content="⌛ The game timed out.", view=None)

    # rock paper scissors
    @games.command(
        name="rockpaperscissors",
        description="Play Rock Paper Scissors with another user",
    )
    @app_commands.describe(user="The user to play with")
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    async def rps(self, i: discord.Interaction, user: discord.User):
        if i.guild and i.permissions.use_external_apps is False:
            raise RuntimeError("External apps are disabled in this channel.")
        if i.user.id == user.id:
            raise RuntimeError("You can't play with yourself!")
        if user.bot:
            raise RuntimeError("You can't play with a bot!")

        view = Confirm(user)
        expires = (datetime.now(UTC) + timedelta(seconds=61)).timestamp()
        await i.response.send_message(
            f"{user.mention}, you have been challenged to **Rock Paper Scissors** by {i.user.mention}! Expires <t:{expires:.0f}:R>.",
            view=view,
        )
        await view.wait()
        if view.accepted is False:
            await i.edit_original_response(
                content=f"The challenge was **rejected** by {user.mention}.",
                view=None,
            )
            return
        elif view.accepted is None:
            await i.edit_original_response(
                content=f"{user.mention} did not respond in time.",
                view=None,
            )
            return

        view = RockPaperScissors(i.user, user)
        embed = discord.Embed(
            title="Rock Paper Scissors",
            description=f"### {i.user.mention} vs {user.mention}\nWaiting for players to choose...",
            colour=self.bot.colour,
        )
        await i.edit_original_response(content=None, embed=embed, view=view)
        timed_out = await view.wait()
        if timed_out:
            await i.edit_original_response(
                content="⌛ The game timed out.",
                view=None,
                embed=None,
            )
            return
        if view.winner is not None:
            winning_choice = (
                view.choices[i.user.id]
                if view.winner == view.p1
                else view.choices[user.id]
            )
            losing_choice = (
                view.choices[user.id]
                if view.winner == view.p1
                else view.choices[i.user.id]
            )
            embed.description = f"### {view.winner.mention} is the **winner!**"
            embed.add_field(name="Winning pick:", value=winning_choice)
            embed.add_field(name="Losing pick:", value=losing_choice)
            await i.edit_original_response(embed=embed, view=None)
        else:
            embed.description = "### It's a tie!"
            embed.add_field(name="Both players chose:", value=view.choices[i.user.id])
            await i.edit_original_response(embed=embed, view=None)

    # battleship
    @games.command(name="battleship", description="Play Battleship with another user")
    @app_commands.describe(user="The user to play with")
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    async def battleship(self, i: discord.Interaction, user: discord.User):
        if i.guild and i.permissions.use_external_apps is False:
            raise RuntimeError("External apps are disabled in this channel.")
        if i.user.id == user.id:
            raise RuntimeError("You can't play with yourself!")
        if user.bot:
            raise RuntimeError("You can't play with a bot!")

        prompt = battleship.Prompt(i.user, user)
        prompt.message = (
            await i.response.send_message(
                f"{user.mention}, you have been challenged to **Battleship** by {i.user.mention}!"
                "\nPress your button to start setting up your ships.",
                view=prompt,
            )
        ).resource

    # hangman
    @games.command(name="hangman", description="Play a game of Hangman")
    @app_commands.describe(
        difficulty="The difficulty of the random word to guess for yourself (default: medium)",
        player="User to give a custom word to. (default: play by yourself with a random word)",
    )
    @app_commands.checks.cooldown(2, 20, key=lambda i: i.channel)
    async def hangman(
        self,
        i: discord.Interaction,
        difficulty: Literal["easy", "medium", "hard"] = "medium",
        player: discord.User | None = None,
    ):
        if player:
            if i.guild and i.permissions.use_external_apps is False:
                raise RuntimeError("External apps are disabled in this channel.")
            if player.id == i.user.id:
                raise RuntimeError("You can't play with yourself!")
            if player.bot:
                raise RuntimeError("You can't play with a bot!")

            word_input_btn = CustomWordView(i.user, player)
            word_input_btn.message = (
                await i.response.send_message(
                    f"{i.user.mention} is creating a Hangman game for {player.mention} with a custom word...",
                    view=word_input_btn,
                )
            ).resource
        else:
            word = get_random_word(difficulty)

            game = HangmanGame(word)
            view = HangmanView(game, i.user)
            view.message = (
                await i.response.send_message(
                    f"{i.user.mention} is playing Hangman",
                    embed=view.get_game_embed(),
                    view=view,
                )
            ).resource

    # quote
    @app_commands.checks.cooldown(2, 20, key=lambda i: i.channel)
    async def quote(self, i: discord.Interaction, message: discord.Message):
        if not message.content:
            raise RuntimeError("The message has no text content.")
        if len(message.content) > 100:
            raise RuntimeError("The text must have no more than 100 characters.")

        await i.response.defer()

        user = message.author

        async with self.bot.session.get(
            "https://api.popcat.xyz/v2/quote",
            params={
                "image": user.display_avatar.url,
                "text": discord.utils.remove_markdown(message.clean_content).strip(),
                "name": user.display_name,
            },
        ) as r:
            if not r.ok:
                raise RuntimeError()
            image = await r.read()

        attachment = discord.File(BytesIO(image), filename="quote.png")

        embed = discord.Embed(
            colour=self.bot.colour,
            title=f"a beautiful quote from {user.display_name}",
        )
        embed.set_image(url="attachment://quote.png")

        await i.followup.send(
            embed=embed, file=attachment, view=DeleteButton(user, i.user)
        )

    # 8ball
    @app_commands.command(name="8ball", description="Ask the Magic 8Ball a question")
    @app_commands.describe(question="The question to ask")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.channel)
    async def eightball(self, i: discord.Interaction, question: str):
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
        embed = Embed(
            colour=self.bot.colour,
        )
        embed.add_field(name="Your question:", value=question, inline=False)
        embed.add_field(name="The Magic 8Ball says:", value=f"🎱 ||{fortune}||")
        await i.response.send_message(embed=embed)

    # coinflip
    @app_commands.command(name="coinflip", description="Flip a coin")
    @app_commands.checks.cooldown(3, 15, key=lambda i: i.channel)
    async def coinflip(self, i: discord.Interaction):
        await i.response.send_message(
            f"🪙 Flipped a coin for you, it's **{random.choice(('heads', 'tails'))}**!"
        )

    # dice
    @app_commands.command(name="dice", description="Roll dice")
    @app_commands.checks.cooldown(3, 15, key=lambda i: i.channel)
    @app_commands.describe(
        number="The number of dice to roll (default: 1)",
    )
    async def dice(
        self, i: discord.Interaction, number: app_commands.Range[int, 1, 6] = 1
    ):
        rolls = random.sample(range(1, 7), number)
        await i.response.send_message(
            f"🎲 Rolled {number} {'die' if number == 1 else 'dice'}:\n **{', '.join([str(r) for r in rolls])}**"
        )

    # mock
    @app_commands.command(name="mock", description="Mock text")
    @app_commands.checks.cooldown(2, 10, key=lambda i: i.channel)
    @app_commands.describe(text="The text to mock")
    async def mock(
        self, i: discord.Interaction, text: app_commands.Range[str, 1, 2000]
    ):
        mock_text = "".join(
            [char.upper() if i % 2 else char.lower() for i, char in enumerate(text)]
        ).replace("<A:", "<a:")
        # fix for animated emojis

        await i.response.send_message(
            mock_text,
            allowed_mentions=discord.AllowedMentions.none(),
        )

    # mock (ctxmenu)
    @app_commands.checks.cooldown(2, 10, key=lambda i: i.channel)
    async def mock_ctx(self, i: discord.Interaction, message: discord.Message):
        if not message.content:
            raise RuntimeError("The message has no text.")
        if len(message.content) > 2000:
            raise RuntimeError("The text must be no more than 2000 characters.")
        await self.mock.callback(self, i, message.content)

    # dadjoke
    @app_commands.command(name="dadjoke", description="Get a dad joke")
    @app_commands.checks.cooldown(2, 10, key=lambda i: i.channel)
    async def dadjoke(self, i: discord.Interaction):
        await i.response.defer()
        async with self.bot.session.get(
            "https://icanhazdadjoke.com/", headers={"Accept": "application/json"}
        ) as r:
            if not r.ok:
                raise RuntimeError()
            json = await r.json()
            await i.followup.send(json["joke"])

    # dog
    @app_commands.command(name="dog", description="Get a random dog image and fact")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def dog(self, i: discord.Interaction):
        await i.response.defer()
        async with self.bot.session.get("https://some-random-api.com/animal/dog") as r:
            if not r.ok:
                raise RuntimeError()
            json = await r.json()

        embed = discord.Embed(colour=self.bot.colour)
        embed.set_image(url=json["image"])
        embed.set_footer(text="Dog fact: " + json["fact"])
        await i.followup.send(embed=embed)

    # cat
    @app_commands.command(name="cat", description="Get a random cat image and fact")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def cat(self, i: discord.Interaction):
        await i.response.defer()
        async with self.bot.session.get("https://some-random-api.com/animal/cat") as r:
            if not r.ok:
                raise RuntimeError()
            json = await r.json()

        embed = discord.Embed(colour=self.bot.colour)
        embed.set_image(url=json["image"])
        embed.set_footer(text="Cat fact: " + json["fact"])
        await i.followup.send(embed=embed)

    # panda
    @app_commands.command(name="panda", description="Get a random panda image and fact")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def panda(self, i: discord.Interaction):
        await i.response.defer()
        async with self.bot.session.get(
            "https://some-random-api.com/animal/panda"
        ) as r:
            if not r.ok:
                raise RuntimeError()
            json = await r.json()

        embed = discord.Embed(colour=self.bot.colour)
        embed.set_image(url=json["image"])
        embed.set_footer(text="Panda fact: " + json["fact"])
        await i.followup.send(embed=embed)

    # megamind
    @app_commands.command(name="megamind", description="Generate a megamind meme")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def megamind(
        self, i: discord.Interaction, text: app_commands.Range[str, 1, 200]
    ):
        embed = discord.Embed(colour=self.bot.colour)
        embed.set_image(
            url=f"https://some-random-api.com/canvas/misc/nobitches?no={quote_plus(text)}"
        )
        await i.response.send_message(embed=embed)

    # woosh
    @app_commands.command(
        name="woosh", description="Generate a woosh (joke-over-head) image"
    )
    @app_commands.describe(user="The user who didn't get the joke")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def woosh(self, i: discord.Interaction, user: discord.Member | discord.User):
        # remove url parameters at the end of avatar url
        avatar = user.display_avatar.replace(format="png").url
        embed = discord.Embed(
            colour=self.bot.colour,
            description=f"*Woosh*... that's the sound of a joke going over {user.display_name}'s head",
        )
        embed.set_image(url=f"https://api.popcat.xyz/v2/jokeoverhead?image={avatar}")
        await i.response.send_message(embed=embed)

    # woosh (ctxmenu)
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def woosh_ctx(self, i: discord.Interaction, message: discord.Message):
        await self.woosh.callback(self, i, message.author)

    # xkcd
    @app_commands.command(name="xkcd", description="Get xkcd comics")
    @app_commands.describe(mode="Random or latest comic (default: random)")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def xkcd(
        self, i: discord.Interaction, mode: Literal["random", "latest"] = "random"
    ):
        async with self.bot.session.get("https://xkcd.com/info.0.json") as r:
            if not r.ok:
                raise RuntimeError()
            json = await r.json()

        if mode == "random":
            latest_num = json["num"]
            comic_num = random.randint(1, latest_num)
            async with self.bot.session.get(
                f"https://xkcd.com/{comic_num}/info.0.json"
            ) as r:
                if not r.ok:
                    raise RuntimeError()
                json = await r.json()

        embed = discord.Embed(
            title=f"xkcd #{json['num']}: {json['safe_title']}",
            description=f"[Comic explanation](https://explainxkcd.com/{json['num']})",
            url=f"https://xkcd.com/{json['num']}",
            colour=self.bot.colour,
        )
        embed.set_image(url=json["img"])
        await i.response.send_message(embed=embed)

    # get non-nsfw reddit post
    @staticmethod
    async def get_reddit_post(session: ClientSession) -> dict:
        nsfw = True
        while nsfw:
            async with session.get("https://meme-api.com/gimme") as r:
                json = await r.json()
                if "message" in json:
                    return json
                nsfw = json["nsfw"]
        return json

    # meme
    @app_commands.command(name="meme", description="Get a random meme")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def meme(self, i: discord.Interaction):
        await i.response.defer()
        try:
            json = await self.get_reddit_post(self.bot.session)
        except Exception:
            raise RuntimeError()

        if "message" in json:
            raise RuntimeError(json["message"])

        embed = (
            discord.Embed(
                title=json["title"], url=json["postLink"], colour=self.bot.colour
            )
            .set_image(url=json["url"])
            .set_footer(text=f"⬆️ {json['ups']}")
        )
        await i.followup.send(embed=embed)
