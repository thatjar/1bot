import discord
import googletrans
from discord.ext.commands import errors

translator = googletrans.Translator()
lang_dict = googletrans.LANGUAGES


class GenericError(errors.CommandInvokeError):
    """A generic error that can be raised to provide a custom error message to the end user."""

    def __init__(self, message: str = "Something went wrong. Please try again later."):
        self.message = message

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"GenericError('{self.message}')"


class Embed(discord.Embed):
    """Embed with automatic truncating."""

    def __init__(self, *args, **kwargs):
        # Truncate the description to 4096 characters
        if "description" in kwargs:
            description = kwargs["description"]
            if len(description) > 4096:
                kwargs["description"] = description[:4093] + "..."
        # Truncate the title to 256 characters
        if "title" in kwargs:
            title = kwargs["title"]
            if len(title) > 256:
                kwargs["title"] = title[:253] + "..."
        super().__init__(*args, **kwargs)

    def add_field(self, *, name, value, inline=True):
        # Truncate the field name to 256 characters
        if len(name) > 256:
            name = name[:253] + "..."
        # Truncate the field value to 1024 characters
        if len(value) > 1024:
            value = value[:1021] + "..."
        return super().add_field(name=name, value=value, inline=inline)

    def set_footer(self, *, text=None, icon_url=None):
        # Truncate the footer text to 2048 characters
        if text and len(text) > 2048:
            text = text[:2045] + "..."
        return super().set_footer(text=text, icon_url=icon_url)

    def set_author(self, *, name=None, icon_url=None, url=None):
        # Truncate the author name to 256 characters
        if name and len(name) > 256:
            name = name[:253] + "..."
        return super().set_author(name=name, icon_url=icon_url, url=url)


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
