from contextlib import suppress
from typing import Union
from urllib.parse import quote_plus

import discord
import requests
from discord import app_commands
from discord.ext import commands


class Utilities(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @app_commands.command(name="weather", description="Get weather information")
    @app_commands.describe(
        location="The location to get weather information for",
    )
    @app_commands.checks.cooldown(1, 20, key=lambda i: i.channel)
    async def weather(self, i: discord.Interaction, location: str):
        await i.response.defer()
        req = requests.get(f"https://api.popcat.xyz/weather?q={location}")
        try:
            json = req.json()
        except ValueError:
            await i.followup.send("❌ Invalid location")
            return

        data = json[0]

        embed = discord.Embed(
            colour=self.bot.colour, description=data["current"]["skytext"]
        )
        embed.set_author(
            icon_url=data["current"]["imageUrl"],
            name=f"Weather in {data['current']['observationpoint']}",
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
            value=data["location"]["alert"] or "No alerts for this area",
            inline=False,
        )

        await i.followup.send(embed=embed)

    @app_commands.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(
        user="The user to get the avatar of (default: yourself)",
        type="Server avatar or user avatar (default: server avatar)",
    )
    @app_commands.choices(
        type=[
            app_commands.Choice(name="Server", value=0),
            app_commands.Choice(name="User", value=1),
        ]
    )
    @app_commands.checks.cooldown(2, 15, key=lambda i: i.channel)
    async def avatar(
        self,
        i: discord.Interaction,
        user: Union[discord.Member, discord.User] = None,
        type: app_commands.Choice[int] = 0,
    ):
        user = user or i.user
        embed = discord.Embed(colour=self.bot.colour, title=(f"{user.name}'s avatar"))
        embed.set_image(url=user.avatar.url if type else user.display_avatar.url)
        await i.response.send_message(embed=embed)

    convert = app_commands.Group(name="convert", description="Convert units")

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
                f"{temperature}°F = **{round((temperature - 32) / 1.8, 2)}°C**"
            )
        else:
            await i.response.send_message(
                f"{temperature}°C = **{round((temperature * 9 / 5) + 32, 2)}°F**"
            )

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
                f"{distance} km = **{round(distance / 1.609344, 3)} mi**"
            )
        else:
            await i.response.send_message(
                f"{distance} mi = **{round(distance * 1.609344, 3)} km**"
            )

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
            await i.response.send_message(
                f"{length} cm = **{round(length / 2.54, 2)} in**"
            )
        else:
            await i.response.send_message(
                f"{length} in = **{round(length * 2.54, 2)} cm**"
            )

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
                f"{weight} kg = **{round(weight * 2.20462, 2)} lbs**"
            )
        else:
            await i.response.send_message(
                f"{weight} lbs = **{round(weight / 2.20462, 2)} kg**"
            )

    @app_commands.command(name="github", description="Search GitHub repositories")
    @app_commands.describe(query="The query to search for")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def github(self, i: discord.Interaction, query: str):
        json = requests.get(
            f"https://api.github.com/search/repositories?q={query}"
        ).json()

        if json["total_count"] == 0:
            await i.response.send_message(
                "❌ No matching repositories found.", ephemeral=True
            )
        else:
            await i.response.send_message(
                f'First result for your query:\n{json["items"][0]["html_url"]}'
            )

    @app_commands.command(name="pypi", description="Get info for a PyPI package")
    @app_commands.describe(package="The package to look for")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def pypi(self, i: discord.Interaction, package: str):
        res = requests.get(f"https://pypi.org/pypi/{package}/json")

        if res.status_code == 404:
            raise ValueError("Package does not exist. Check for spelling errors.")

        json = res.json()

        embed = discord.Embed(
            title=json["info"]["name"],
            colour=self.bot.colour,
            url=json["info"]["package_url"],
        )

        if json["info"]["summary"] != "UNKNOWN":
            embed.description = json["info"]["summary"]

        # Max length for embed fields is 1024
        if len(json["info"]["description"]) <= 1024:
            embed.add_field(
                name="Description", value=json["info"]["description"], inline=False
            )
        else:
            # Slice description to 1021 characters and add ellipsis
            embed.add_field(
                name="Description",
                value=json["info"]["description"][:1021] + "...",
                inline=False,
            )

        if json["info"]["home_page"]:
            embed.add_field(name="Homepage", value=json["info"]["home_page"])

        embed.add_field(name="Version", value=json["info"]["version"])
        embed.add_field(name="Author", value=json["info"]["author"])

        if json["info"]["license"]:
            if len(json["info"]["license"]) <= 1024:
                embed.add_field(name="License", value=json["info"]["license"])
            else:
                embed.add_field(
                    name="License",
                    value=json["info"]["license"][:1021] + "...",
                    inline=False,
                )

        await i.response.send_message(embed=embed)

    @app_commands.command(name="npm", description="Get info for a NPM package")
    @app_commands.describe(package="The package to look for")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def npm(self, i: discord.Interaction, package: str):
        json = requests.get(f"https://registry.npmjs.org/{package}").json()

        if json.get("error") is not None:
            await i.response.send_message("❌ " + json["error"], ephemeral=True)
            return

        embed = discord.Embed(
            title=json["name"],
            colour=0xCA3836,
            url="https://www.npmjs.com/package/" + package,
        )

        with suppress(KeyError):
            embed.description = json["description"]
        with suppress(KeyError):
            embed.add_field(name="Homepage", value=json["homepage"], inline=False)
        with suppress(KeyError):
            embed.add_field(name="Author", value=json["author"]["name"])
        with suppress(KeyError):
            embed.add_field(
                name="Repository",
                value=json["repository"]["url"],
                inline=False,
            )
        embed.add_field(
            name="Repository maintainers",
            value=", ".join(maintainer["name"] for maintainer in json["maintainers"]),
            inline=False,
        )
        with suppress(KeyError):
            embed.add_field(name="License", value=json["license"], inline=False)

        await i.response.send_message(embed=embed)

    @app_commands.command(name="lyrics", description="Get lyrics for a song")
    @app_commands.describe(query="The query to search for")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.channel)
    async def lyrics(self, i: discord.Interaction, query: str):
        await i.response.defer()
        json = requests.get(
            f"https://some-random-api.com/lyrics?title={quote_plus(query)}"
        ).json()

        with suppress(KeyError):
            if json["error"]:
                await i.followup.send("❌ " + json["error"])
                return

        embed = discord.Embed(
            title=json["title"],
            url=json["links"]["genius"],
            colour=self.bot.colour,
        )
        with suppress(KeyError):
            embed.set_thumbnail(url=json["thumbnail"]["genius"])
        if len(json["lyrics"]) > 4096:
            embed.description = json["lyrics"][:4093] + "..."
        else:
            embed.description = json["lyrics"]

        await i.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Utilities(bot))
