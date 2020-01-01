import aiohttp
import sqlite3

from datetime import datetime

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

    @command(['uptime', '업타임'], pass_context=True)
    async def uptime(self, ctx: Context, *_):
        user = await self.bot.wrap_user(ctx.channel.login)
        print(user.display_name, user.login, user.id)

        api = self.bot.api.GetStreams(client_id=self.bot.client_id)
        result = await api.perform(ids=user.id)
        self.bot.logger.critical(result)
        stream = result[0]
        delta = datetime.now() - stream.started_at
        await ctx.reply(f"업타임: {delta}")

    @command(['title', '방제'], pass_context=True)
    async def title(self, ctx: Context, *_):
        API = ctx.bot.APIHandler

        user = await API.get_user_by_name(ctx.channel.name)
        stream = await API.get_stream(user.tid)
        if stream:
            await ctx.reply(f"방제: {stream['title']}")
        else:
            await ctx.reply("방송중이 아닙니다.")

    @command(['game', '게임'], pass_context=True)
    async def game(self, ctx: Context, *_):
        API = ctx.bot.APIHandler

        user = await API.get_user_by_name(ctx.channel.name)
        stream = await API.get_stream(user.tid)
        if stream:
            await ctx.reply(f"게임: {stream['game']}")
        else:
            await ctx.reply("방송중이 아닙니다.")

    @command(['follow', '팔로우'], pass_context=True)
    async def information(self, ctx, *_):
        API = ctx.bot.APIHandler

        user = await API.get_user_by_name(ctx.user.name)
        channel = await API.get_user_by_name(ctx.channel.name)

        _data = await API.get_is_channel_followed(channel, user)
        is_follower = "팔로우한 지 " + API.humanizeTimeDiff(_data) if _data else "아직 팔로우를 안 하셨군요 ㅠ,,"

        await ctx.reply(f"@{ctx.user.name}, {is_follower}")

    @command(['commands', '커맨드'], pass_context=True)
    async def commands(self, ctx: Context, *_):
        commands = ctx.bot.commands

        await ctx.reply(", ".join([ctx.bot.command_prefix + v for v in commands.keys()]))

    @Cog.listener()
    async def on_open(self, sock):
        print(" [BC] Bot is ready")

    @Cog.listener()
    async def on_data(self, ctx: Context):
        return print(ctx.user.name, ctx.channel.name, ctx.message.type, ctx.message.message, ctx.message.raw)

    @Cog.listener()
    async def on_error(self, e):
        return print(f"\n\n\n    {repr(e)}\n\n\n")


def setup(bot: Bot):
    print("I was activated")
    bot.add_cog(BasicCommands(bot))
