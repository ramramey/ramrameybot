import aiohttp
import sqlite3

from datetime import datetime, timedelta

from ramrameybot import Bot
from ramrameybot.models import command, Command, Context
from ramrameybot.models.command import Cog


class JoinMinecraft(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.session = set()

        self.db = sqlite3.connect("")

    @command(['시참'], pass_context=True)
    async def c_height(self, ctx: Context):
        nick = ctx.message.message.split(" ")[1:]

        if not nick or len(nick) != 1:
            return await ctx.reply(f"@{ctx.user.login} !시참 [마크닉네임]")

        try:
            nick = nick[0]

            user = await self.bot.wrap_user(ctx.user.login)
            channel = await self.bot.wrap_user(ctx.channel.login)
            total, token, data = await self.bot.api.GetUserFollows(client_id=self.bot.client_id).\
                perform(user.id, channel.id)

            if not data:
                return await ctx.reply(f"@{ctx.user.login} 5252 팔로우는 누르고 시참하라굿")

            async with aiohttp.ClientSession() as sess:
                async with sess.get(
                        f"http://localhost:8080/register?id={user.id}&nick={user.display_name}&minecraft={nick}"
                ) as resp:
                    data = await resp.json()
                    status = data.get('status')

                    if status:
                        return await ctx.reply(f"@{ctx.user.login} 등록처리 완료! 서버에 입장해주세요")
                    else:
                        return await ctx.reply(f"@{ctx.user.login} 요청 처리 중 오류가 발생했습니다.")
        except:
            return await ctx.reply(f"@{ctx.user.login} 요청 처리 중 오류가 발생했습니다.")


def setup(bot: Bot):
    print("I was activated")
    bot.add_cog(JoinMinecraft(bot))
