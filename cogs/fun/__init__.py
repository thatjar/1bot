from __future__ import annotations

from typing import TYPE_CHECKING

from .fun import Fun

if TYPE_CHECKING:
    from main import OneBot


async def setup(bot: OneBot) -> None:
    await bot.add_cog(Fun(bot))
