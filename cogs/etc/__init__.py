from __future__ import annotations

from typing import TYPE_CHECKING

from .etc import Etc

if TYPE_CHECKING:
    from main import OneBot


async def setup(bot: OneBot) -> None:
    await bot.add_cog(Etc(bot))
