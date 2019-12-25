import socket
import asyncio

from datetime import datetime

from .apis.twitch import helix
from .apis.twitch import User, Member

from typing import Dict, Union, Optional


class RamrameyBot:
    def __init__(self,
                 cogs,
                 user: str,
                 client_id: str,
                 token: str = "",
                 host: str = "irc.twitch.tv",
                 port: int = 6667,
                 command_prefix: str = "!"):
        # Bot info
        self._user = user
        self.user: Optional[User] = None
        self.client_id = client_id
        self.token = token
        self.command_prefix = command_prefix

        # Server info
        self.host = host
        self.port = port

        self.api = helix

        # Cached objects
        self._users: Dict[int, Union[User, Member]] = {}

        self.loop = asyncio.get_event_loop()
        self.queue = []
        self.keep_running = True

        self.socket: Optional[socket.socket] = socket.socket()

    def run(self):
        self.loop.run_until_complete(self.test())
        self.loop.run_until_complete(self._run())

    async def test(self):
        data = await self.api.GetUsers(client_id=self.client_id).perform(logins=["eunhaklee", "return0927", "ramramey"])
        for user in data:
            print(user.id, user.login, user.display_name, user.offline_image_url)

    async def send_raw(self, data: bytes):
        """Send raw packet via socket connection"""
        return self.socket.send(data)

    async def send_msg(self, channel: Union[str, User, Member], data: str):
        """Send message to a specific channel"""
        if hasattr(channel, 'login'):  # If User of Member
            channel: str = channel.login

        await self.send_raw("PRIVMSG #{} :{}\n".format(channel, data).encode())

    async def enqueue_message(self, data: bytes):
        data = data.decode().replace("\r\n", "\n").split("\n")[:-1]
        self.queue.extend(data)

    async def fetch_queue(self):
        if self.queue:
            return self.queue.pop(0)

        await self.enqueue_message(self.socket.recv(2 ** 20))
        return await self.fetch_queue()

    async def _prepare(self):
        self.socket.connect((self.host, self.port))

    async def _run(self):
        await self._prepare()

        while self.keep_running:
            for line in await self.fetch_queue():
                print(datetime.now().strftime("%Y-%m-%d %T"), line)

            await asyncio.sleep(.01)

        return
