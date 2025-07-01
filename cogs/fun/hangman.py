from __future__ import annotations

import random
from typing import Optional, Set

import discord

from main import OneBot


class HangmanGame:
    """Class to handle the logic for a Hangman game."""

    def __init__(self, word: str, max_attempts: int = 6):
        self.word = word.lower()
        self.guessed_letters: Set[str] = set()
        self.max_attempts = max_attempts
        self.attempts_left = max_attempts
        self.game_over = False
        self.won = False

    def guess(self, letter: str) -> bool:
        """Process a guess. Return True if correct, False otherwise."""
        letter = letter.lower()
        if letter in self.guessed_letters:
            return False

        self.guessed_letters.add(letter)

        if letter in self.word:
            if all(c in self.guessed_letters for c in self.word if c.isalpha()):
                self.game_over = True
                self.won = True
            return True
        else:
            self.attempts_left -= 1
            if self.attempts_left <= 0:
                self.game_over = True
            return False

    def get_word_display(self) -> str:
        """Return the word with unguessed letters replaced by underscores."""
        return "".join(
            c if c in self.guessed_letters or not c.isalpha() else r"\_"
            for c in self.word
        )

    def get_hangman_art(self) -> str:
        """Return ASCII art of the hangman."""
        stages = [
            """```
  +---+
  |   |
      |
      |
      |
      |
=========```""",
            """```
  +---+
  |   |
  O   |
      |
      |
      |
=========```""",
            """```
  +---+
  |   |
  O   |
  |   |
      |
      |
=========```""",
            """```
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========```""",
            r"""```
  +---+
  |   |
  O   |
 /|\  |
      |
      |
=========```""",
            r"""```
  +---+
  |   |
  O   |
 /|\  |
 /    |
      |
=========```""",
            r"""```
  +---+
  |   |
  O   |
 /|\  |
 / \  |
      |
=========```""",
        ]
        return stages[self.max_attempts - self.attempts_left]


class GuessLetterModal(discord.ui.Modal, title="Guess a Letter"):
    letter = discord.ui.TextInput(
        label="Enter a single letter",
        placeholder="Type a letter A-Z",
        min_length=1,
        max_length=1,
    )

    def __init__(self, game_view: HangmanView):
        super().__init__()
        self.game_view = game_view

    async def on_submit(self, i: discord.Interaction):
        letter = self.letter.value.upper()

        if not letter.isalpha():
            return await i.response.send_message(
                "Please enter a valid letter (A-Z).", ephemeral=True
            )
        if letter.lower() in self.game_view.game.guessed_letters:
            return await i.response.send_message(
                f"You've already guessed the letter '{letter}'.", ephemeral=True
            )

        is_correct = self.game_view.game.guess(letter)
        result_message = (
            f"Your guess: '{letter}' - {'Correct!' if is_correct else 'Incorrect!'}"
        )
        await i.response.send_message(result_message, ephemeral=True)

        await self.game_view.update_game()

        if self.game_view.game.game_over:
            if not self.game_view.game.won:
                # show the word if they lost
                await i.followup.send(
                    f"Game over! The word was: **{self.game_view.game.word}**"
                )
            self.game_view.stop()


class HangmanView(discord.ui.View):
    """UI View for the Hangman game."""

    def __init__(self, game: HangmanGame, player: discord.User, timeout: float = 180.0):
        super().__init__(timeout=timeout)
        self.game = game
        self.player = player
        self.message: Optional[discord.Message] = None

        guess_button = discord.ui.Button(
            label="Guess a Letter", style=discord.ButtonStyle.primary, emoji="🔤"
        )
        guess_button.callback = self.show_guess_modal
        self.add_item(guess_button)

    async def show_guess_modal(self, i: discord.Interaction) -> None:
        if i.user.id != self.player.id:
            return await i.response.send_message(
                "❌ This isn't your game.", ephemeral=True
            )

        modal = GuessLetterModal(self)
        await i.response.send_modal(modal)

    async def update_game(self) -> None:
        """Update the game embed with the current state."""
        if self.message:
            embed = self.get_game_embed()
            await self.message.edit(embed=embed, view=self)

    def get_game_embed(self) -> discord.Embed:
        embed = discord.Embed(title="Hangman Game", colour=OneBot.colour)
        embed.add_field(name="Word", value=self.game.get_word_display(), inline=False)
        embed.add_field(
            name="Incorrect attempts left",
            value=f"{self.game.attempts_left}/{self.game.max_attempts}",
            inline=False,
        )

        if self.game.guessed_letters:
            guessed = ", ".join(self.game.guessed_letters)
            embed.add_field(name="Guessed Letters", value=guessed, inline=False)

        embed.add_field(name="Hangman", value=self.game.get_hangman_art(), inline=False)

        if self.game.game_over:
            if self.game.won:
                embed.add_field(name="Result", value="🎉 You won!", inline=False)
            else:
                embed.add_field(name="Result", value="😔 You lost!", inline=False)

            for item in self.children:
                assert isinstance(item, discord.ui.Button)
                item.disabled = True

        return embed


WORD_LISTS = {
    "easy": [
        "cat",
        "dog",
        "sun",
        "hat",
        "bee",
        "fox",
        "cow",
        "pen",
        "cup",
        "fish",
        "book",
        "tree",
        "door",
        "star",
        "bird",
        "duck",
        "cake",
        "ball",
        "game",
        "home",
    ],
    "medium": [
        "apple",
        "dance",
        "happy",
        "juice",
        "music",
        "ocean",
        "party",
        "queen",
        "tiger",
        "zebra",
        "garden",
        "planet",
        "winter",
        "summer",
        "dragon",
        "flower",
        "rabbit",
        "turtle",
        "sunset",
        "bridge",
    ],
    "hard": [
        "blossom",
        "charity",
        "dolphin",
        "elephant",
        "fantasy",
        "gravity",
        "harmony",
        "jealous",
        "kangaroo",
        "library",
        "mystery",
        "notebook",
        "octopus",
        "penguin",
        "quantum",
        "romance",
        "symphony",
        "universe",
        "volcano",
        "whisper",
    ],
}


def get_random_word(difficulty: str = "medium") -> str:
    """Get a random word from the list with the given difficulty."""
    word_list = WORD_LISTS.get(difficulty, WORD_LISTS["medium"])
    return random.choice(word_list)
