import aiohttp
from ramrameybot import Bot
from ramrameybot.models import command, Command


class BasicCommands:
    def __init__(self, bot):
        self.bot = bot
        self.session = set()

    @command(['uptime', '업타임'], pass_context=True)
    async def uptime(self, ctx, *_):
        bot = ctx.bot
        API = bot.APIHandler

        user = await API.get_user_by_name(ctx.channel.name)
        uptime = await API.get_uptime(user.tid)
        await ctx.reply(f"업타임: {uptime}")

    @command(['title', '방제'], pass_context=True)
    async def title(self, ctx, *_):
        API = ctx.bot.APIHandler

        user = await API.get_user_by_name(ctx.channel.name)
        stream = await API.get_stream(user.tid)
        if stream:
            await ctx.reply(f"방제: {stream['title']}")
        else:
            await ctx.reply("방송중이 아닙니다.")

    @command(['game', '게임'], pass_context=True)
    async def game(self, ctx, *_):
        API = ctx.bot.APIHandler

        user = await API.get_user_by_name(ctx.channel.name)
        stream = await API.get_stream(user.tid)
        if stream:
            await ctx.reply(f"게임: {stream['game']}")
        else:
            await ctx.reply("방송중이 아닙니다.")

    # @command(['enak', 'enakbot'], pass_context=True)
    async def enak_eng(self, ctx, *_):
        await ctx.reply(f"{ctx.user.name} EnakBot is Twitch-Discord crossplatform chatbot operated & developed by @return0927 (Eunhak Lee).")


    # @command(['으낙', '으낙봇'], pass_context=True)
    async def enakbot(self, ctx, *_):
        await ctx.reply(f"@{ctx.user.name} 으낙봇은 트수 @return0927 (이은학)이 개발/운영하는 트위치-디스코드 크로스플랫폼 챗봇입니다.")

    @command(['follow', '팔로우'], pass_context=True)
    async def information(self, ctx, *_):
        API = ctx.bot.APIHandler

        user = await API.get_user_by_name(ctx.user.name)
        channel = await API.get_user_by_name(ctx.channel.name)

        _data = await API.get_is_channel_followed(channel, user)
        is_follower = "팔로우한 지 " + API.humanizeTimeDiff(_data) if _data else "아직 팔로우를 안 하셨군요 ㅠ,,"

        await ctx.reply(f"@{ctx.user.name}, {is_follower}")

    @command(['commands', '커맨드'], pass_context=True)
    async def commands(self, ctx, *_):
        commands = ctx.bot.commands

        await ctx.reply(", ".join([ctx.bot.command_prefix + v for v in commands.keys()]))

    async def on_open(self, sock):
        print(" [BC] Bot is ready")

    async def on_data(self, ctx):
        return print(ctx.user.name, ctx.channel.name, ctx.message.type, ctx.message.message, ctx.message.raw)

    async def on_error(self, e):
        return print(f"\n\n\n    {repr(e)}\n\n\n")


def setup(bot):
    print("I was activated")
    bot.add_cog(BasicCommands(bot))
