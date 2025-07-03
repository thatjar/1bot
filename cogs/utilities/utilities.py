from __future__ import annotations

import re
import unicodedata
import zoneinfo
from datetime import datetime
from typing import TYPE_CHECKING, Literal
from urllib.parse import quote

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

from utils.paginator import Paginator
from utils.utils import Embed, lang_dict, translator

from .autocompletes import lang_autocomplete, timezone_autocomplete

if TYPE_CHECKING:
    from main import OneBot


class Utilities(commands.Cog):
    def __init__(self, bot: OneBot):
        self.bot = bot
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
            "https://api.popcat.xyz/v2/weather", params={"q": location}
        ) as r:
            try:
                json = await r.json()
            except aiohttp.ContentTypeError:
                raise RuntimeError("Invalid location. Try with a more specific query.")
        if not json or not json.get("message"):  # handle empty response
            raise RuntimeError("Invalid location. Try with a more specific query.")

        pages = []
        for entry in json["message"]:
            embed = Embed(
                colour=self.bot.colour,
                description=entry["current"]["skytext"],
                title=f"Weather in {entry['current']['observationpoint']}",
            )

            embed.add_field(
                name="Temperature",
                value=f'{entry["current"]["temperature"]}°{entry["location"]["degreetype"]}',
            )
            embed.add_field(
                name="Feels like",
                value=f"{entry['current']['feelslike']}°{entry['location']['degreetype']}",
            )
            embed.add_field(
                name="Wind",
                value=entry["current"]["winddisplay"],
                inline=False,
            )
            embed.add_field(
                name="Humidity",
                value=f"{entry['current']['humidity']}%",
            )
            embed.add_field(
                name="Alerts",
                value=entry["location"].get("alert") or "No alerts for this area",
                inline=False,
            )

            pages.append(embed)

        if len(pages) == 1:
            await i.followup.send("Found 1 result:", embed=pages[0])
        else:
            paginator = Paginator(
                interaction=i,
                pages=pages,
                message_content=f"Found {len(pages)} results:",
            )
            await paginator.start()

    # group for /convert
    convert = app_commands.Group(name="convert", description="Convert units")

    # convert temperature
    @convert.command(
        name="temperature",
        description="Convert temperatures between Celsius and Fahrenheit",
    )
    @app_commands.describe(
        temperature="The temperature to convert",
        to="Convert to Fahrenheit or Celsius?",
    )
    async def convert_temp(
        self,
        i: discord.Interaction,
        temperature: float,
        to: Literal["Fahrenheit", "Celsius"],
    ):
        if to == "Fahrenheit":
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
        to="Convert to miles or kilometres?",
    )
    async def convert_distance(
        self,
        i: discord.Interaction,
        distance: float,
        to: Literal["Miles", "Kilometres"],
    ):
        if to == "Miles":
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
        to="Convert to inches or centimetres?",
    )
    async def convert_length(
        self,
        i: discord.Interaction,
        length: float,
        to: Literal["Inches", "Centimetres"],
    ):
        if to == "Inches":
            await i.response.send_message(f"{length} cm = **{(length / 2.54):.2f} in**")
        else:
            await i.response.send_message(f"{length} in = **{(length * 2.54):.2f} cm**")

    # convert weight
    @convert.command(
        name="weight", description="Convert weights between kilograms and pounds"
    )
    @app_commands.describe(
        weight="The weight to convert",
        to="Convert to pounds or kilograms?",
    )
    async def convert_weight(
        self,
        i: discord.Interaction,
        weight: float,
        to: Literal["Pounds", "Kilograms"],
    ):
        if to == "Pounds":
            await i.response.send_message(
                f"{weight} kg = **{(weight * 2.20462):.2f} lb**"
            )
        else:
            await i.response.send_message(
                f"{weight} lbs = **{(weight / 2.20462):.2f} kg**"
            )

    # convert currency
    @convert.command(
        name="currency", description="Convert currency from one to another"
    )
    @app_commands.describe(
        amount="The amount of money to convert",
        source="Currency code to convert from (e.g. USD, EUR)",
        to="Currency code to convert to (e.g. EUR, USD)",
    )
    @app_commands.rename(source="from")
    async def currency(
        self,
        i: discord.Interaction,
        amount: float,
        source: str,
        to: str,
    ):
        if source == to:
            raise RuntimeError("Source and target currencies cannot be the same")

        await i.response.defer()

        async with self.bot.session.get(
            "https://api.exchangerate-api.com/v4/latest/" + source.upper()
        ) as r:
            if not r.ok:
                raise RuntimeError("Invalid source currency code")
            json = await r.json()

        if to.upper() not in json["rates"]:
            raise RuntimeError("Invalid target currency code")

        rate = json["rates"][to.upper()]
        converted_amount = amount * rate

        await i.followup.send(
            f"{amount} {source.upper()} = **{converted_amount:.2f} {to.upper()}**"
        )

    # lyrics
    @app_commands.command(name="lyrics", description="Get lyrics for a song")
    @app_commands.describe(query="The query to search for")
    @app_commands.checks.cooldown(2, 15, key=lambda i: i.channel)
    async def lyrics(self, i: discord.Interaction, query: str):
        await i.response.defer()
        async with self.bot.session.get(
            "https://lrclib.net/api/search", params={"q": query}
        ) as r:
            if not r.ok:
                raise RuntimeError()
            json = await r.json()
            if not json:  # handle empty response
                raise RuntimeError("No results found for that query.")

        pages = []
        for entry in json:
            if not entry["plainLyrics"]:
                continue

            embed = Embed(
                colour=self.bot.colour,
                title=f"{entry['trackName']} \N{EM DASH} {entry['artistName']}",
                description=entry["plainLyrics"],
            )
            embed.set_author(name="Lyrics from LRCLIB", url="https://lrclib.net/")

            pages.append(embed)

        if not pages:
            raise RuntimeError("No lyrics found for that query.")

        if len(pages) == 1:
            await i.followup.send("Found 1 result:", embed=pages[0])
        else:
            paginator = Paginator(
                interaction=i,
                pages=pages,
                message_content=f"Found {len(pages)} results:",
            )
            await paginator.start()

    # translate
    @app_commands.command(
        name="translate", description="Translate text via Google Translate"
    )
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    @app_commands.describe(
        text="The text to translate",
        to="The language to translate to (default: English)",
        source="The language to translate from (default: auto-detect)",
    )
    @app_commands.rename(source="from")
    @app_commands.autocomplete(to=lang_autocomplete, source=lang_autocomplete)
    async def translate(
        self,
        i: discord.Interaction,
        text: str,
        to: str = "en",
        source: str = "auto",
    ):
        if to == source:
            raise RuntimeError("Source and destination languages cannot be the same")
        if to not in lang_dict and to not in lang_dict.values():
            raise RuntimeError("Invalid destination language")
        if (
            source not in lang_dict
            and source not in lang_dict.values()
            and source != "auto"
        ):
            raise RuntimeError("Invalid source language")

        await i.response.defer()

        translation = await translator.translate(text, dest=to, src=source)
        detected_lang_name = lang_dict[translation.src.lower()].title()
        output_lang_name = lang_dict[translation.dest.lower()].title()

        embed = (
            Embed(colour=self.bot.colour)
            .add_field(
                name=f"Original ({detected_lang_name.title()})",
                value=text,
                inline=False,
            )
            .add_field(
                name=f"Translation ({output_lang_name})",
                value=translation.text,
                inline=False,
            )
        )

        await i.followup.send(embed=embed)

    # translate (ctxmenu)
    @app_commands.checks.cooldown(2, 30, key=lambda i: i.channel)
    async def translate_ctx(self, i: discord.Interaction, message: discord.Message):
        await self.translate.callback(self, i, message.content)

    # define
    @app_commands.command(
        name="define", description="Get the definition of a term/word"
    )
    @app_commands.describe(
        term="The term/word to define",
    )
    @app_commands.checks.cooldown(3, 20, key=lambda i: i.channel)
    async def define(self, i: discord.Interaction, term: str):
        await i.response.defer()
        async with self.bot.session.get(
            f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(term)}"
        ) as r:
            try:
                json = await r.json()
            except aiohttp.ContentTypeError:
                raise RuntimeError()
        if not json:  # handle empty response
            raise RuntimeError()
        if isinstance(json, dict) and json.get("title") == "No Definitions Found":
            if json["title"] == "No Definitions Found":
                raise RuntimeError("No definitions found for that word")
            else:
                raise RuntimeError()

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
        name="charinfo", description="Get information about characters (unicode)"
    )
    @app_commands.describe(
        characters="The characters to get information about",
    )
    @app_commands.checks.cooldown(3, 20, key=lambda i: i.channel)
    async def charinfo(
        self, i: discord.Interaction, characters: app_commands.Range[str, 1, 20]
    ):
        # code stolen from rapptz/robodanny :3
        def to_string(c):
            digit = f"{ord(c):X}"
            name = unicodedata.name(c, "Name not found.")
            c = "\\`" if c == "`" else c
            return f"[`U+{digit:>04}`](http://www.fileformat.info/info/unicode/char/{digit}): {name} \N{EM DASH} {c}"

        msg = "\n".join(map(to_string, characters.strip()))
        if len(msg) > 2000:
            raise RuntimeError(
                "Result too long to send. Please try again with fewer characters."
            )
        await i.response.send_message(msg, suppress_embeds=True)

    # create emoji
    @app_commands.command(name="emoji", description="Create an emoji from a link")
    @app_commands.default_permissions(create_expressions=True)
    @app_commands.checks.has_permissions(create_expressions=True)
    @app_commands.checks.bot_has_permissions(create_expressions=True)
    @app_commands.checks.cooldown(2, 20, key=lambda i: i.channel)
    @app_commands.describe(url="The link to the emoji", name="The name of the emoji")
    async def emoji(
        self, i: discord.Interaction, url: str, name: app_commands.Range[str, 2, 32]
    ):
        await i.response.defer()
        try:
            async with self.bot.session.get(url) as r:
                if r.status != 200:
                    raise RuntimeError("Invalid/incomplete URL.")

                emoji_bytes = await r.read()

        except aiohttp.ClientError:
            raise RuntimeError("Invalid/incomplete URL.")

        emoji = await i.guild.create_custom_emoji(
            name=name, image=emoji_bytes, reason=f"Uploaded by {i.user}"
        )

        await i.followup.send(f"✅ Created emoji {emoji}")

    @emoji.error
    async def emoji_error(
        self, i: discord.Interaction, e: app_commands.AppCommandError
    ):
        if "String value did not match validation regex" in str(e):
            await i.followup.send(
                "❌ Invalid emoji name; you have unsupported characters in the emoji name."
            )
        elif "Must be between 2 and 32 in length" in str(e):
            await i.followup.send("❌ The emoji name must be 2 to 32 characters long.")
        elif "Maximum number of emojis reached" in str(e):
            await i.followup.send("❌ This server has reached its emoji limit.")
        elif "Failed to resize asset below the maximum size" in str(
            e
        ) or "File cannot be larger than" in str(e):
            await i.followup.send(
                "❌ The image is too large to be resized to an emoji."
            )
        elif "Unsupported image type given" in str(e):
            await i.followup.send(
                "❌ URL must directly point to a PNG, JPEG, GIF or WEBP."
            )
        elif "cannot identify image file" in str(e):
            await i.followup.send(
                "❌ Invalid image type. Supported types are PNG, JPEG, GIF and WEBP."
            )
        else:
            return

        # if we reach here, the error was handled
        e.add_note("handled")

    # method to replace "[word]" with "word"
    @staticmethod
    def ud_hyperlink(text):
        return re.sub(r"\[([^\]]+)\]", lambda m: m.group(1), text)

    # urban
    @app_commands.command(
        name="urban",
        description="Get the definition of a term/word from Urban Dictionary",
    )
    @app_commands.describe(
        term="The term/word to define",
    )
    @app_commands.checks.cooldown(3, 20, key=lambda i: i.channel)
    async def urban(self, i: discord.Interaction, term: str):
        await i.response.defer()
        async with self.bot.session.get(
            "https://api.urbandictionary.com/v0/define", params={"term": term}
        ) as r:
            if not r.ok:
                raise RuntimeError()
            json = await r.json()
            if not json or not json.get("list"):  # handle empty response
                raise RuntimeError("No results found for that query.")

        pages = []
        for entry in json["list"]:
            definition = self.ud_hyperlink(entry["definition"])
            example = self.ud_hyperlink(entry["example"])

            embed = Embed(
                colour=self.bot.colour,
                title=f"Definition of {entry['word']}",
                url=entry["permalink"],
            )

            embed.add_field(name="Definition", value=definition, inline=False)
            embed.add_field(name="Example", value=example, inline=False)
            embed.set_author(
                name=f"👍 {entry['thumbs_up']} | 👎 {entry['thumbs_down']}"
            )

            pages.append(embed)

        if len(pages) == 1:
            await i.followup.send("Found 1 result:", embed=pages[0])
        else:
            paginator = Paginator(
                interaction=i,
                pages=pages,
                message_content=f"Found {len(pages)} results:",
            )
            await paginator.start()

    # world clock
    @app_commands.command(
        name="worldclock", description="Get the current time in a timezone"
    )
    @app_commands.describe(
        timezone="The timezone to get the current time for",
    )
    @app_commands.autocomplete(timezone=timezone_autocomplete)
    async def worldclock(self, i: discord.Interaction, timezone: str):
        try:
            current_time = datetime.now(zoneinfo.ZoneInfo(timezone))
        except zoneinfo.ZoneInfoNotFoundError:
            raise RuntimeError("Invalid timezone.")

        formatted_time_12h = current_time.strftime("%I:%M:%S %p")
        formatted_time_24h = current_time.strftime("%H:%M:%S")
        offset = current_time.strftime("%z")
        offset_str = offset[:3] + ":" + offset[3:]

        embed = discord.Embed(
            colour=self.bot.colour,
            description=f"Current time in {timezone} ({offset_str})",
        )
        embed.add_field(
            name="12-hour format",
            value=formatted_time_12h,
            inline=False,
        )
        embed.add_field(
            name="24-hour format",
            value=formatted_time_24h,
            inline=False,
        )
        await i.response.send_message(embed=embed)
