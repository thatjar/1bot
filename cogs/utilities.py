import unicodedata
from typing import TYPE_CHECKING, Literal
from urllib.parse import quote, quote_plus

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils import GenericError, lang_autocomplete, lang_dict, translator

if TYPE_CHECKING:
    from main import Bot


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.bot.tree.add_command(
            app_commands.ContextMenu(
                name="Translate to English",
                callback=self.translate_ctx,
            )
        )

    # weather
    @app_commands.command(name="weather", description="Get weather information")
    @app_commands.describe(
        location="The location to get weather information for",
    )
    @app_commands.checks.cooldown(3, 25, key=lambda i: i.channel)
    async def weather(self, i: discord.Interaction, location: str):
        await i.response.defer()
        async with self.bot.session.get(
            f"https://api.popcat.xyz/weather?q={location}"
        ) as r:
            try:
                json = await r.json()
            except aiohttp.ContentTypeError:
                raise GenericError("Invalid location")
        if not json:  # handle empty response
            raise GenericError("Invalid location")

        data = json[0]

        embed = discord.Embed(
            colour=self.bot.colour,
            description=data["current"]["skytext"],
            title=f"Weather in {data['current']['observationpoint']}",
        )

        embed.add_field(
            name="Temperature",
            value=f'{data["current"]["temperature"]}°{data["location"]["degreetype"]}',
        )
        embed.add_field(
            name="Feels like",
            value=f"{data['current']['feelslike']}°{data['location']['degreetype']}",
        )
        embed.add_field(
            name="Wind",
            value=data["current"]["winddisplay"],
            inline=False,
        )
        embed.add_field(
            name="Humidity",
            value=f"{data['current']['humidity']}%",
        )
        embed.add_field(
            name="Alerts",
            value=data["location"].get("alert") or "No alerts for this area",
            inline=False,
        )

        await i.followup.send(embed=embed)

    # group for /convert
    convert = app_commands.Group(name="convert", description="Convert units")

    # convert temperature
    @convert.command(
        name="temperature",
        description="Convert temperatures between Celsius and Fahrenheit",
    )
    @app_commands.describe(
        temperature="The temperature to convert",
        target="Convert to Fahrenheit or Celsius?",
    )
    async def convert_temp(
        self,
        i: discord.Interaction,
        temperature: float,
        target: Literal["Fahrenheit", "Celsius"],
    ):
        if target == "Fahrenheit":
            await i.response.send_message(
                f"{temperature}°C = **{((temperature * 1.8) + 32):.2f}°F**"
            )
        else:
            await i.response.send_message(
                f"{temperature}°F = **{((temperature - 32) / 1.8):.2f}°C**"
            )

    # convert distance
    @convert.command(
        name="distance",
        description="Convert distances between kilometres and miles",
    )
    @app_commands.describe(
        distance="The distance to convert",
        target="Convert to miles or kilometres?",
    )
    async def convert_distance(
        self,
        i: discord.Interaction,
        distance: float,
        target: Literal["Miles", "Kilometres"],
    ):
        if target == "Miles":
            await i.response.send_message(
                f"{distance} km = **{(distance / 1.609344):.3f} mi**"
            )
        else:
            await i.response.send_message(
                f"{distance} mi = **{(distance * 1.609344):.3f} km**"
            )

    # convert length
    @convert.command(
        name="length", description="Convert lengths between centimetres and inches"
    )
    @app_commands.describe(
        length="The length to convert",
        target="Convert to inches or centimetres?",
    )
    async def convert_length(
        self,
        i: discord.Interaction,
        length: float,
        target: Literal["Inches", "Centimetres"],
    ):
        if target == "Inches":
            await i.response.send_message(f"{length} cm = **{(length / 2.54):.2f} in**")
        else:
            await i.response.send_message(f"{length} in = **{(length * 2.54):.2f} cm**")

    # convert weight
    @convert.command(
        name="weight", description="Convert weights between kilograms and pounds"
    )
    @app_commands.describe(
        weight="The weight to convert",
        target="Convert to pounds or kilograms?",
    )
    async def convert_weight(
        self,
        i: discord.Interaction,
        weight: float,
        target: Literal["Pounds", "Kilograms"],
    ):
        if target == "Pounds":
            await i.response.send_message(
                f"{weight} kg = **{(weight * 2.20462):.2f} lb**"
            )
        else:
            await i.response.send_message(
                f"{weight} lbs = **{(weight / 2.20462):.2f} kg**"
            )

    # lyrics
    @app_commands.command(name="lyrics", description="Get lyrics for a song")
    @app_commands.describe(query="The query to search for")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def lyrics(self, i: discord.Interaction, query: str):
        await i.response.defer()
        async with self.bot.session.get(
            f"https://some-random-api.com/lyrics?title={quote_plus(query)}"
        ) as r:
            json = await r.json()

        if "error" in json:
            await i.followup.send("❌ " + json["error"])
            return

        embed = discord.Embed(
            title=json["title"],
            url=json["links"]["genius"],
            colour=self.bot.colour,
        )
        if "thumbnail" in json and "genius" in json["thumbnail"]:
            embed.set_thumbnail(url=json["thumbnail"]["genius"])
        if len(json["lyrics"]) > 4096:
            embed.description = json["lyrics"][:4093] + "..."
        else:
            embed.description = json["lyrics"]

        await i.followup.send(embed=embed)

    # translate
    @app_commands.command(
        name="translate", description="Translate text via Google Translate"
    )
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    @app_commands.describe(
        text="The text to translate",
        destination="The language to translate to (default: English)",
        source="The language to translate from (default: auto-detect)",
    )
    @app_commands.autocomplete(destination=lang_autocomplete, source=lang_autocomplete)
    async def translate(
        self,
        i: discord.Interaction,
        text: str,
        destination: str = "en",
        source: str = "auto",
    ):
        if destination == source:
            raise GenericError("Source and destination languages cannot be the same")

        await i.response.defer()

        translation = await translator.translate(text, dest=destination, src=source)
        detected_lang_name = lang_dict[translation.src.lower()].title()
        output_lang_name = lang_dict[translation.dest.lower()].title()

        embed = (
            discord.Embed(colour=self.bot.colour)
            .add_field(
                name=f"Original ({detected_lang_name.title()})",
                value=text if len(text) <= 1024 else text[:1021] + "...",
                inline=False,
            )
            .add_field(
                name=f"Translation ({output_lang_name})",
                value=(
                    translation.text
                    if len(translation.text) <= 1024
                    else translation.text[:1021] + "..."
                ),
                inline=False,
            )
        )

        # Add pronunciations if one of the languages is not English
        if translation.src != "en":
            # Translate text into itself to get pronunciation
            pronunciation = await translator.translate(
                text, dest=translation.src, src=translation.src
            )
            pronunciation = pronunciation.pronunciation

            if (
                type(pronunciation) is str
                and pronunciation
                and pronunciation.lower() != text.lower()
            ):
                embed.add_field(
                    name="Original Pronunciation",
                    value=(
                        pronunciation
                        if len(pronunciation) <= 1024
                        else pronunciation[:1021] + "..."
                    ),
                    inline=False,
                )
        if translation.dest != "en":
            if type(translation.pronunciation) is str and translation.pronunciation:
                embed.add_field(
                    name="Translation Pronunciation",
                    value=(
                        translation.pronunciation
                        if len(translation.pronunciation) <= 1024
                        else translation.pronunciation[:1021] + "..."
                    ),
                    inline=False,
                )

        await i.followup.send(embed=embed)

    # translate (ctxmenu)
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    async def translate_ctx(self, i: discord.Interaction, message: discord.Message):
        await self.translate.callback(self, i, message.content)

    # define
    @app_commands.command(
        name="define", description="Get the definition of a word/term"
    )
    @app_commands.describe(
        word="The word/term to define",
    )
    @app_commands.checks.cooldown(3, 20, key=lambda i: i.channel)
    async def define(self, i: discord.Interaction, word: str):
        await i.response.defer()
        async with self.bot.session.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}"
        ) as r:
            try:
                json = await r.json()
            except aiohttp.ContentTypeError:
                raise GenericError("Something went wrong. Please try again later.")
        if not json:  # handle empty response
            raise GenericError("Something went wrong. Please try again later.")
        if isinstance(json, dict) and "title" in json:
            if json["title"] == "No Definitions Found":
                raise GenericError("No definitions found for that word")
            else:
                raise GenericError("Something went wrong. Please try again later.")

        data = json[0]

        embed = discord.Embed(
            colour=self.bot.colour,
            title=f"Definition of {data['word']}",
            url=data["sourceUrls"][0],
        )

        for meaning in data["meanings"]:
            defs = "\n".join([f"- {i['definition']}" for i in meaning["definitions"]])
            if len(defs) > 1024:
                defs = (
                    defs[: 1010 - len(data["sourceUrls"][0])]
                    + f" [...(more)]({data['sourceUrls'][0]})"
                )
            embed.add_field(
                name=meaning["partOfSpeech"].title(),
                value=defs,
                inline=False,
            )

        await i.followup.send(embed=embed)

    # charinfo
    @app_commands.command(
        name="charinfo", description="Get information about a character (unicode)"
    )
    @app_commands.describe(
        character="The character to get information about",
    )
    @app_commands.checks.cooldown(3, 20, key=lambda i: i.channel)
    async def charinfo(self, i: discord.Interaction, character: str):
        # code semi-stolen from rapptz/robodanny :3
        digit = f"{ord(character):x}"
        name = unicodedata.name(character, "Name not found.")
        character = "\\`" if character == "`" else character
        msg = f"[`U+{digit:>04}`](http://www.fileformat.info/info/unicode/char/{digit}): {name} **\N{EM DASH}** {character}"

        await i.response.send_message(msg, suppress_embeds=True)


async def setup(bot):
    await bot.add_cog(Utilities(bot))
