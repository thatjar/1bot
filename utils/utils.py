import discord
import googletrans

translator = googletrans.Translator()
lang_dict = googletrans.LANGUAGES


class Embed(discord.Embed):
    """Embed with automatic truncating."""

    def __init__(self, *args, **kwargs):
        if kwargs.get("description"):
            description = kwargs["description"]
            if type(description) is str:
                description = description.strip()
                if len(description) > 4096:
                    kwargs["description"] = description[:4093] + "..."
        if kwargs.get("title"):
            title = kwargs["title"]
            if type(title) is str:
                title = title.strip()
                if len(title) > 256:
                    kwargs["title"] = title[:253] + "..."
        super().__init__(*args, **kwargs)

    def add_field(self, *, name, value, inline=True):
        if type(name) is str:
            name = name.strip()
            if len(name) > 256:
                name = name[:253] + "..."
        if type(value) is str:
            value = value.strip()
            if len(value) > 1024:
                value = value[:1021] + "..."
        return super().add_field(name=name, value=value, inline=inline)

    def set_footer(self, *, text=None, icon_url=None):
        if type(text) is str:
            text = text.strip()
            if len(text) > 2048:
                text = text[:2045] + "..."
        return super().set_footer(text=text, icon_url=icon_url)

    def set_author(self, *, name=None, icon_url=None, url=None):
        if type(name) is str:
            name = name.strip()
            if len(name) > 256:
                name = name[:253] + "..."
        return super().set_author(name=name, icon_url=icon_url, url=url)


vl = discord.VerificationLevel
VL_STRINGS = {
    vl.none: "None",
    vl.low: "Members must have a verified email on their Discord account.",
    vl.medium: "Members must have a verified email and be registered on Discord for more than five minutes.",
    vl.high: "Members must have a verified email, be registered on Discord for more than five minutes,"
    " and be a member of the server for more than ten minutes.",
    vl.highest: "Members must have a verified phone number.",
}
