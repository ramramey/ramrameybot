from ..apis.twitch import User, Member
from .message import Message

from dataclasses import dataclass
from typing import Any, Optional, Union


@dataclass()
class Context:
    bot: Any  # This must be RamrameyBot
    type: str

    # Chatting data
    channel: Optional[Union[str, User]]
    chatter: Optional[Union[str, User, Member]]
    message: Message

    @property
    def user(self):
        return self.chatter

    @classmethod
    async def make_from_message(cls, bot: Any, message: Message, type: Optional[str] = None):
        return cls(
            bot=bot,
            type=type or message.type,
            channel=message.channel,
            chatter=message.chatter,
            message=message
        )

    async def reply(self, data: str):
        await self.bot.send_msg(self.channel, data)
