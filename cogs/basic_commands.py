import aiohttp
import sqlite3

from datetime import datetime, timedelta

from ramrameybot import Bot
from ramrameybot.models import command, Command, Context
from ramrameybot.models.command import Cog


class BasicCommands(Cog):
    def __init__(self, bot):
        self.bot: Bot = bot
        self.session = set()

        self.db = sqlite3.connect("")

    @command(['키'], pass_context=True)
    async def c_height(self, ctx: Context):
        await ctx.reply("156 / 람람피셜 179")

    @command(["몸무게"], pass_context=True)
    async def c_weight(self, ctx: Context):
        await ctx.reply("47g")

    @command(["학교"], pass_context=True)
    async def c_school(self, ctx: Context):
        await ctx.reply("대학교")

    @command(["대학교", '본명'], pass_context=True)
    async def c_seiled(self, ctx: Context):
        await ctx.reply("쉿")

    @command(["이름"], pass_context=True)
    async def c_name(self, ctx: Context):
        await ctx.reply("람람이")

    @command(["나이"], pass_context=True)
    async def c_age(self, ctx: Context):
        await ctx.reply("88년생 21세")

    @command(["즙", "즙즙백과"], pass_context=True)
    async def c_crying_ramram(self, ctx: Context):
        await ctx.reply("람람 또 우럭?")

    @command(["방바닥"], pass_context=True)
    async def c_ground(self, ctx: Context):
        await ctx.reply("쓰레기땜에 안보임")

    @command(["양심"], pass_context=True)
    async def c_mind(self, ctx: Context):
        await ctx.reply("마려워서 싸고옴ㅠ")

    @command(["남친", "남자친구"], pass_context=True)
    async def c_boyfriend(self, ctx: Context):
        await ctx.reply("난 트수가 있는데 어떡해,,,")

    # ----------------------------------- #
    # Update 2020.1.1.
    @command(["생일", "생신"], pass_context=True)
    async def c_birthday(self, ctx: Context):
        await ctx.reply("11.30")

    # ----------------------------------- #
    # Update 2020.1.20.
    @command(["사양", "컴퓨터", "스펙"], pass_context=True)
    async def c_pc(self, ctx: Context):
        await ctx.reply("@"+ctx.user.login + " AMD R5 3600 / 16GB / SSD 512G / 이엠텍 RTX2060 STORM / 자세한건 https://tgd.kr/35191322")

    # ----------------------------------- #
    # Global commands
    @command(['follow', '팔로우'], pass_context=True)
    async def c_follow(self, ctx: Context, *_):
        user = await self.bot.wrap_user(ctx.user.login)
        channel = await self.bot.wrap_user(ctx.channel.login)

        api = self.bot.api.GetUserFollows(client_id=self.bot.client_id)
        total, token, data = await api.perform(user.id, channel.id)

        if not data:  # 팔로우하지 않은 경우
            return await ctx.reply("@{} 팔로우 안해놓고 느낌표팔로우 흐지 므르,,,,".format(user.login))

        assert len(data), 1

        date = data[-1]["followed_at"] + timedelta(hours=9)
        return await ctx.reply("@{} 님이 팔로우: {}".format(user.display_name, date.strftime("%Y-%m-%d %T")))

    @command(['commands', '커맨드', '명령어'], pass_context=True)
    async def commands(self, ctx: Context, *_):
        commands = ctx.bot.commands

        await ctx.reply(" / ".join([ctx.bot.command_prefix + v for v in commands.keys()]))


def setup(bot: Bot):
    print("I was activated")
    bot.add_cog(BasicCommands(bot))
