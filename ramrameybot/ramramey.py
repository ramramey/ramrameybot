import asyncio

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
        self._user = ""
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

    def run(self):
        self.loop.run_until_complete(self.test())
        self.loop.run_until_complete(self._run())

    async def test(self):
        data = await self.api.GetUsers(client_id=self.client_id).perform(logins=["eunhaklee", "return0927", "ramramey"])
        for user in data:
            print(user.id, user.login, user.display_name, user.offline_image_url)

    async def _run(self):
        return
