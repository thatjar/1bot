from __future__ import annotations

from typing import TYPE_CHECKING

from .starboard import Starboard

if TYPE_CHECKING:
    from main import OneBot


async def setup(bot: OneBot) -> None:
    if hasattr(bot, "pool"):
        await bot.add_cog(Starboard(bot))
    else:
        bot.logger.warning("No database, not loading Starboard")
