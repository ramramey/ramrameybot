from typing import Union

from ramrameybot import Bot
from ramrameybot.models import Context
from ramrameybot.models.command import Cog


class Debugger(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.sessions = set()

    @property
    def logger(self):
        return self.bot.logger

    @Cog.listener()
    async def on_raw(self, data: Union[bytes, str], is_outgoing=False):
        if isinstance(data, bytes):
            data = data.decode()

        return self.logger.debug("{} RAW > {}".format("Outgoing" if is_outgoing else "Received", data))

    @Cog.listener()
    async def on_message(self, ctx: Context):
        return self.logger.info("CHAT #{} U:{}> {}".format(ctx.channel, ctx.user, ctx.message))


def setup(bot: Bot):
    bot.add_cog(Debugger(bot))
