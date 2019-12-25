from ..apis.twitch import User, Member

from dataclasses import dataclass
from typing import Optional, Union


@dataclass()
class Message:
    channel: Optional[Union[str, User]]
    chatter: Optional[Union[str, User, Member]]
