from typing import TYPE_CHECKING
from urllib.parse import quote_plus

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
        description="Convert temperatures between Fahrenheit and Celsius",
    )
    @app_commands.describe(
        temperature="The temperature to convert",
        target="Convert to Fahrenheit or Celsius?",
    )
    @app_commands.choices(
        target=[
            app_commands.Choice(name="Celsius", value=0),
            app_commands.Choice(name="Fahrenheit", value=1),
        ]
    )
    async def convert_temp(
        self,
        i: discord.Interaction,
        temperature: float,
        target: app_commands.Choice[int],
    ):
        if target.value == 0:
            await i.response.send_message(
                f"{temperature}°F = **{((temperature - 32) / 1.8):.2f}°C**"
            )
        else:
            await i.response.send_message(
                f"{temperature}°C = **{((temperature * 1.8) + 32):.2f}°F**"
            )

    # convert distance
    @convert.command(
        name="distance",
        description="Convert distances between Kilometres and Miles",
    )
    @app_commands.describe(
        distance="The distance to convert",
        target="Convert to Miles or Kilometres?",
    )
    @app_commands.choices(
        target=[
            app_commands.Choice(name="Miles", value=0),
            app_commands.Choice(name="Kilometres", value=1),
        ]
    )
    async def convert_distance(
        self,
        i: discord.Interaction,
        distance: float,
        target: app_commands.Choice[int],
    ):
        if target.value == 0:
            await i.response.send_message(
                f"{distance} km = **{(distance / 1.609344):.3f} mi**"
            )
        else:
            await i.response.send_message(
                f"{distance} mi = **{(distance * 1.609344):.3f} km**"
            )

    # convert length
    @convert.command(
        name="length", description="Convert lengths between Centimetres and Inches"
    )
    @app_commands.describe(
        length="The length to convert",
        target="Convert to Centimetres or Inches?",
    )
    @app_commands.choices(
        target=[
            app_commands.Choice(name="Inches", value=0),
            app_commands.Choice(name="Centimetres", value=1),
        ]
    )
    async def convert_length(
        self,
        i: discord.Interaction,
        length: float,
        target: app_commands.Choice[int],
    ):
        if target.value == 0:
            await i.response.send_message(f"{length} cm = **{(length / 2.54):.2f} in**")
        else:
            await i.response.send_message(f"{length} in = **{(length * 2.54):.2f} cm**")

    # convert weight
    @convert.command(
        name="weight", description="Convert weights between Kilograms and Pounds"
    )
    @app_commands.describe(
        weight="The weight to convert",
        target="Convert to Pounds or Kilograms?",
    )
    @app_commands.choices(
        target=[
            app_commands.Choice(name="Pounds", value=0),
            app_commands.Choice(name="Kilograms", value=1),
        ]
    )
    async def convert_weight(
        self,
        i: discord.Interaction,
        weight: float,
        target: app_commands.Choice[int],
    ):
        if target.value == 0:
            await i.response.send_message(
                f"{weight} kg = **{(weight * 2.20462):.2f} lbs**"
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

    # create emoji
    @app_commands.command(name="emoji", description="Create an emoji from a link")
    @app_commands.default_permissions(create_expressions=True)
    @app_commands.checks.has_permissions(create_expressions=True)
    @app_commands.checks.bot_has_permissions(create_expressions=True)
    @app_commands.checks.cooldown(2, 20, key=lambda i: i.channel)
    @app_commands.describe(url="The link to the emoji", name="The name of the emoji")
    async def emoji(self, i: discord.Interaction, url: str, name: str):
        await i.response.defer(ephemeral=True)
        try:
            async with self.bot.session.get(url) as r:
                if r.status != 200:
                    raise GenericError("Invalid/incomplete URL.")

                emoji_bytes = await r.read()

        except aiohttp.ClientError:
            raise GenericError("Invalid/incomplete URL.")

        try:
            emoji = await i.guild.create_custom_emoji(
                name=name, image=emoji_bytes, reason=f"Uploaded by {i.user}"
            )
        except discord.HTTPException as e:
            if "String value did not match validation regex" in str(e):
                await i.followup.send(
                    "❌ Invalid emoji name; you have unsupported characters in the emoji name."
                )
            elif "Must be between 2 and 32 in length" in str(e):
                await i.followup.send(
                    "❌ The emoji name must be 2 to 32 characters long."
                )
            elif "Maximum number of emojis reached" in str(e):
                await i.followup.send("❌ This server has reached its emoji limit.")
            elif "Failed to resize asset below the maximum size" in str(
                e
            ) or "File cannot be larger than" in str(e):
                await i.followup.send(
                    "❌ The image is too large to be resized to an emoji."
                )
            else:
                raise

            return
        except Exception as e:
            if isinstance(e, ValueError):
                if "Unsupported image type given" in str(e):
                    await i.followup.send(
                        "❌ URL must directly point to a PNG, JPEG, GIF or WEBP."
                    )
            else:
                raise

            return

        await i.followup.send(f"✅ Created emoji {emoji}")

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
                value=text[:1024],
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
                    value=pronunciation,
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


async def setup(bot):
    await bot.add_cog(Utilities(bot))
