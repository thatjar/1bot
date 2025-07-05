import discord
import googletrans

translator = googletrans.Translator()
lang_dict = googletrans.LANGUAGES


class Embed(discord.Embed):
    """Embed with automatic truncating."""

    def __init__(self, *args, **kwargs):
        description = kwargs.get("description")
        if description is not None:
            desc_str = str(description).strip()
            if len(desc_str) > 4096:
                kwargs["description"] = desc_str[:4093] + "..."

        title = kwargs.get("title")
        if title is not None:
            title_str = str(title).strip()
            if len(title_str) > 256:
                kwargs["title"] = title_str[:253] + "..."
        super().__init__(*args, **kwargs)

    def add_field(self, *, name, value, inline=True):
        name_str = str(name).strip()
        value_str = str(value).strip()
        if len(name_str) > 256:
            name_str = name_str[:253] + "..."
        if len(value_str) > 1024:
            value_str = value_str[:1021] + "..."
        return super().add_field(name=name_str, value=value_str, inline=inline)

    def set_footer(self, *, text=None, icon_url=None):
        text_str = str(text).strip()
        if len(text_str) > 2048:
            text_str = text_str[:2045] + "..."
        return super().set_footer(text=text_str, icon_url=icon_url)

    def set_author(self, *, name=None, icon_url=None, url=None):
        name_str = str(name).strip()
        if len(name_str) > 256:
            name_str = name_str[:253] + "..."
        return super().set_author(name=name_str, icon_url=icon_url, url=url)
