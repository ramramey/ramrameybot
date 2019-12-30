import re

from .models.message import Message
from .exceptions import BotException

from typing import Union


class ParseError(BotException):
    def __init__(self, message: str, raw: Union[bytes, str]):
        self.message = message
        self.raw = raw

        super().__init__(message)


class Parser:
    handshake = re.compile(r"^:([\w.]+) (\d+) (\w+) :(.*)$")
    chatroom = re.compile(r"^:(\w+)!\w+@\w+\.tmi\.twitch\.tv (\w+) #(\w+)( :(.+))*$")
    pingpong = re.compile(r"^(PING|PONG) :(.+)$")

    @classmethod
    def parse_message(cls, data: str):
        if cls.chatroom.match(data):
            user, mode, channel, _, content = cls.chatroom.findall(data)[0]
            return mode, {"user": user, "channel": channel, "content": content}

        elif cls.pingpong.match(data):
            mode, host = cls.pingpong.findall(data)[0]
            return mode, {"host": host}

        elif cls.handshake.match(data):
            mode = "HANDSHAKE"
            host, pid, me, message = cls.handshake.findall(data)[0]
            return mode, {"host": host, "pid": pid, "me": me, "message": message}

        raise ParseError

