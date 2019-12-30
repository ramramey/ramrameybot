from typing import Union

from ramrameybot import Bot
from ramrameybot.models.command import Cog


class Debugger(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.sessions = set()

    @property
    def logger(self):
        return self.bot.logger

    @Cog.listener()
    async def on_raw(self, data: Union[bytes, str]):
        if isinstance(data, bytes):
            data = data.decode()

        return self.logger.debug(" Received RAW > " + data)


def setup(bot: Bot):
    bot.add_cog(Debugger(bot))
