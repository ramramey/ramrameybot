from ..apis.twitch import User, Member

from dataclasses import dataclass
from typing import Any, Optional, Union


@dataclass()
class Context:
    bot: Any  # This must be RamrameyBot
    type: str

    # Chatting data
    channel: Optional[Union[str, User]]
    chatter: Optional[Union[str, User, Member]]
    message: str

    async def reply(self, data: str):
        await self.bot.send_msg(self.channel, data)
