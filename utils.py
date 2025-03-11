import discord
import googletrans

translator = googletrans.Translator()
lang_dict = googletrans.LANGUAGES


async def lang_autocomplete(_: discord.Interaction, current: str | None):
    langs = lang_dict.values()
    return [
        discord.app_commands.Choice(name=lang.title(), value=lang)
        for lang in langs
        if lang.startswith(current.lower())
    ][:25]
