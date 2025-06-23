import zoneinfo

import discord
from googletrans import LANGUAGES as lang_dict


async def lang_autocomplete(
    _: discord.Interaction, current: str
) -> list[discord.app_commands.Choice[str]]:
    langs = lang_dict.values()
    return [
        discord.app_commands.Choice(name=lang.title(), value=lang)
        for lang in langs
        if lang.startswith(current.lower()) or current.lower() in lang
    ][:25]


TIMEZONES = zoneinfo.available_timezones()


async def timezone_autocomplete(
    _: discord.Interaction, current: str
) -> list[discord.app_commands.Choice[str]]:
    return [
        discord.app_commands.Choice(name=tz, value=tz)
        for tz in TIMEZONES
        if tz.lower().startswith(current.lower()) or current.lower() in tz.lower()
    ][:25]
