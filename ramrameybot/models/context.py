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
    message: Union[str, Message]

    @classmethod
    async def make_from_message(cls, bot: Any, message: Message, type: str = "chat"):
        return cls(
            bot=bot,
            type=type,
            channel=message.channel,
            chatter=message.chatter,
            message=message
        )

    async def reply(self, data: str):
        await self.bot.send_msg(self.channel, data)
