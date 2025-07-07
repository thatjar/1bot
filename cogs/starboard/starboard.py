from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from utils.views import Confirm

if TYPE_CHECKING:
    from main import OneBot


class Starboard(commands.Cog):
    def __init__(self, bot: OneBot):
        self.bot = bot

    async def cog_load(self):
        for cmd in self.walk_app_commands():
            cmd.allowed_installs = app_commands.AppInstallationType(
                guild=True, user=False
            )
            cmd.allowed_contexts = app_commands.AppCommandContext(
                guild=True, dm_channel=False, private_channel=False
            )

        if hasattr(self.bot, "pool"):
            await self.bot.pool.execute(
                """
                CREATE TABLE IF NOT EXISTS starboard (
                    guild_id BIGINT PRIMARY KEY,
                    channel_id BIGINT NOT NULL,
                    star_count INT DEFAULT 5
                )
                """
            )

            # table for starred messages to prevent duplicates
            await self.bot.pool.execute(
                """
                    CREATE TABLE IF NOT EXISTS starred_messages (
                        message_id BIGINT PRIMARY KEY,
                        guild_id BIGINT NOT NULL,
                        channel_id BIGINT NOT NULL,
                        author_id BIGINT NOT NULL,
                        starboard_message_id BIGINT,
                        starboard_message_url TEXT,
                        star_count INT DEFAULT 0
                    )
                    """
            )

    # set starboard
    @app_commands.command(
        description="Setup/edit starboard configuration for this server"
    )
    @app_commands.describe(
        channel="The channel to use as starboard",
        min_stars="Minimum number of stars required (default: 5)",
    )
    @app_commands.default_permissions(manage_guild=True)
    async def starboard_set(
        self,
        i: discord.Interaction,
        channel: discord.TextChannel,
        min_stars: app_commands.Range[int, 2, 20] = 5,
    ):
        await i.response.defer(ephemeral=True)
        channel_perms = channel.permissions_for(i.guild.me)
        if not channel_perms.send_messages:
            # try to set permissions if bot can't send messages
            if not channel_perms.manage_roles:
                raise RuntimeError(
                    "Couldn't give myself permission to send messages in that channel, please set it manually."
                )
            overwrite = channel.overwrites_for(i.guild.me)
            overwrite.send_messages = True
            await channel.set_permissions(
                i.guild.me, overwrite=overwrite, reason="Setting up starboard"
            )

        await self.bot.pool.execute(
            """
                INSERT INTO starboard (guild_id, channel_id, star_count) 
                VALUES ($1, $2, $3)
                ON CONFLICT (guild_id) 
                DO UPDATE SET channel_id = $2, star_count = $3
                """,
            i.guild.id,
            channel.id,
            min_stars,
        )

        await i.followup.send(
            f"✅ Starboard has been set to {channel.mention} with a threshold of {min_stars} stars.\n"
        )

    # disable starboard
    @app_commands.command(description="Disable the starboard for this server")
    @app_commands.default_permissions(manage_guild=True)
    async def starboard_disable(self, i: discord.Interaction):
        # check if starboard is configured
        configuration = await self.bot.pool.fetchrow(
            "SELECT channel_id FROM starboard WHERE guild_id = $1", i.guild.id
        )
        if not configuration:
            raise RuntimeError("No starboard configuration found to disable.")

        view = Confirm(i.user, timeout=180)
        await i.response.send_message(
            "Are you sure you want to disable the starboard? This will delete the configuration and the starboard functionality for this server.",
            view=view,
            ephemeral=True,
        )
        await view.wait()
        if view.accepted is None:
            return await i.edit_original_response(
                content="⌛ Timed out waiting for a response.", view=None
            )
        if not view.accepted:
            return await i.edit_original_response(content="Cancelled.", view=None)

        await self.bot.pool.execute(
            "DELETE FROM starboard WHERE guild_id = $1", i.guild.id
        )
        await self.bot.pool.execute(
            "DELETE FROM starred_messages WHERE guild_id = $1",
            i.guild.id,
        )

        await i.edit_original_response(
            content="✅ Starboard and starred message data for this server have been removed."
        )

    starboard_group = app_commands.Group(
        name="starboard", description="Starboard configuration and management"
    )

    @starboard_group.command(description="View the current starboard configuration")
    async def view_config(self, i: discord.Interaction):
        await i.response.defer(ephemeral=True)
        configuration = await self.bot.pool.fetchrow(
            "SELECT channel_id, star_count FROM starboard WHERE guild_id = $1",
            i.guild.id,
        )

        if not configuration:
            raise RuntimeError(
                "No starboard configuration found. Use `/starboard setup` to configure it."
            )

        channel = i.guild.get_channel(configuration["channel_id"])
        channel_mention = (
            channel.mention
            if channel
            else f"<#{configuration['channel_id']}> (Channel not found)"
        )

        embed = discord.Embed(title="Starboard Configuration", color=self.bot.colour)
        embed.add_field(name="Channel", value=channel_mention)
        embed.add_field(name="Minimum Stars", value=str(configuration["star_count"]))

        await i.followup.send(embed=embed)

    @starboard_group.command(description="View starboard statistics for this server")
    async def server_stats(self, i: discord.Interaction):
        stats = await self.bot.pool.fetchrow(
            """
                SELECT COUNT(*) as total_starred, 
                       AVG(star_count) as avg_stars,
                       MAX(star_count) as max_stars,
                       SUM(star_count) as total_stars
                FROM starred_messages 
                WHERE guild_id = $1
                """,
            i.guild.id,
        )

        if not stats or stats["total_starred"] == 0:
            await i.response.send_message(
                "❌ No starred messages found for this server.", ephemeral=True
            )
            return

        most_starred_msg_url = (
            await self.bot.pool.fetchrow(
                """
                SELECT starboard_message_url as url
                FROM starred_messages 
                WHERE guild_id = $1 AND star_count = $2
            """,
                i.guild.id,
                stats["max_stars"],
            )
        )["url"]

        embed = discord.Embed(title="Starboard Statistics", color=self.bot.colour)
        embed.add_field(
            name="Total Starred Messages", value=str(stats["total_starred"])
        )
        embed.add_field(name="Average Stars", value=f"⭐ {stats['avg_stars']:.1f}")
        embed.add_field(
            name="Most Starred Message",
            value=f"🌟 {stats['max_stars']} ({most_starred_msg_url})",
        )
        embed.add_field(name="Total Stars", value=f"✨ {stats['total_stars']}")

        await i.response.send_message(embed=embed)

    @starboard_group.command(description="View a user's starboard statistics")
    @app_commands.describe(user="The user to view stats for (default: yourself)")
    async def user_stats(self, i: discord.Interaction, user: discord.User = None):
        if not user:
            user = i.user

        await i.response.defer()

        stats = await self.bot.pool.fetchrow(
            """
                SELECT COUNT(*) as total_starred, 
                       AVG(star_count) as avg_stars,
                       MAX(star_count) as max_stars,
                       SUM(star_count) as total_stars
                FROM starred_messages 
                WHERE guild_id = $1 AND author_id = $2
                """,
            i.guild.id,
            user.id,
        )

        if not stats or stats["total_starred"] == 0:
            await i.followup.send(
                f"❌ No starred messages found for {user.mention}.",
                allowed_mentions=discord.AllowedMentions.none(),
            )
            return

        most_starred_msg_url = (
            await self.bot.pool.fetchrow(
                """
                SELECT starboard_message_url as url
                FROM starred_messages 
                WHERE guild_id = $1 AND author_id = $2 AND star_count = $3
            """,
                i.guild.id,
                user.id,
                stats["max_stars"],
            )
        )["url"]

        embed = discord.Embed(
            title=f"{user.name}'s Starboard Statistics", color=self.bot.colour
        )
        embed.add_field(
            name="Total Starred Messages", value=str(stats["total_starred"])
        )
        embed.add_field(name="Average Stars", value=f"⭐ {stats['avg_stars']:.1f}")
        embed.add_field(
            name="Most Starred Message",
            value=f"🌟 {stats['max_stars']} ({most_starred_msg_url})",
        )
        embed.add_field(name="Total Stars", value=f"✨ {stats['total_stars']}")

        await i.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        """Remove starboard configuration if the starboard channel is deleted"""

        if not isinstance(channel, discord.TextChannel):
            return

        # Check if this channel was a starboard channel
        configuration = await self.bot.pool.fetchrow(
            "SELECT guild_id FROM starboard WHERE channel_id = $1", channel.id
        )

        if configuration:
            await self.bot.pool.execute(
                "DELETE FROM starboard WHERE guild_id = $1", configuration["guild_id"]
            )
            await self.bot.pool.execute(
                "DELETE FROM starred_messages WHERE guild_id = $1",
                configuration["guild_id"],
            )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Handle reaction changes for starboard functionality"""
        if not payload.guild_id:
            return
        if str(payload.emoji) != "⭐":
            return
        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        # Get starboard config for this guild
        configuration = await self.bot.pool.fetchrow(
            "SELECT channel_id, star_count FROM starboard WHERE guild_id = $1",
            payload.guild_id,
        )
        if not configuration:
            return

        channel = guild.get_channel(payload.channel_id)
        if not channel or channel.id == configuration["channel_id"]:
            return  # don't star messages in the starboard channel itself

        try:
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return

        for reaction in message.reactions:
            if str(reaction.emoji) == "⭐":
                star_count = reaction.count
                async for u in reaction.users():
                    if u.id == message.author.id:
                        star_count -= 1  # don't count the author's own reaction
                        break
                break
        if star_count < configuration["star_count"]:
            return

        # check if message is already in starboard
        starred_message = await self.bot.pool.fetchrow(
            "SELECT starboard_message_id, star_count FROM starred_messages WHERE message_id = $1",
            payload.message_id,
        )

        starboard_channel = guild.get_channel(configuration["channel_id"])
        if not starboard_channel:
            return

        if not starred_message:
            # create new starboard entry
            if not starboard_channel.permissions_for(guild.me).send_messages:
                try:
                    overwrite = starboard_channel.overwrites_for(guild.me)
                    overwrite.send_messages = True
                    await starboard_channel.set_permissions(
                        guild.me, overwrite=overwrite, reason="Starboard setup"
                    )
                except discord.Forbidden:
                    return
            starboard_msg = await message.forward(starboard_channel)
            await starboard_channel.send(
                rf"*\- {message.author.mention}, <t:{message.created_at.timestamp():.0f}:f>*"
            )

            await self.bot.pool.execute(
                """
                INSERT INTO starred_messages 
                (message_id, starboard_message_url, guild_id, channel_id, author_id, starboard_message_id, star_count)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                message.id,
                starboard_msg.jump_url,
                guild.id,
                channel.id,
                message.author.id,
                starboard_msg.id,
                star_count,
            )
        else:
            # update existing starboard entry
            if starred_message["star_count"] != star_count:
                try:
                    starboard_msg = await starboard_channel.fetch_message(
                        starred_message["starboard_message_id"]
                    )
                    await self.bot.pool.execute(
                        "UPDATE starred_messages SET star_count = $1 WHERE message_id = $2",
                        star_count,
                        message.id,
                    )
                except discord.NotFound:
                    await self.bot.pool.execute(
                        "DELETE FROM starred_messages WHERE message_id = $1",
                        message.id,
                    )
