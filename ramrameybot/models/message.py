from ..apis.twitch import User, Member

from dataclasses import dataclass
from typing import Optional, Union


@dataclass()
class Message:
    channel: Optional[Union[str, User]]
    chatter: Optional[Union[str, User, Member]]

    content: str
    raw: Optional[Union[str, bytes]]

    type: str = "chat"

    def __str__(self):
        return self.content

    @property
    def message(self):
        return self.content
