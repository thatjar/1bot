import discord
import googletrans
from discord.ext.commands import errors

translator = googletrans.Translator()
lang_dict = googletrans.LANGUAGES


class GenericError(errors.CommandInvokeError):
    """A generic error that can be raised to provide a custom error message to the end user."""

    def __init__(self, message):
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"GenericError('{self.message}')"


async def lang_autocomplete(
    _: discord.Interaction, current: str
) -> list[discord.app_commands.Choice[str]]:
    langs = lang_dict.values()
    return [
        discord.app_commands.Choice(name=lang.title(), value=lang)
        for lang in langs
        if lang.startswith(current.lower())
    ][:25]


vl = discord.VerificationLevel
VL_STRINGS = {
    vl.none: "None",
    vl.low: "Members must have a verified email on their Discord account.",
    vl.medium: "Members must have a verified email and be registered on Discord for more than five minutes.",
    vl.high: "Members must have a verified email, be registered on Discord for more than five minutes,"
    " and be a member of the server for more than ten minutes.",
    vl.highest: "Members must have a verified phone number.",
}
