import sys
import socket
import asyncio
import inspect
import traceback
import importlib

import colorlog
import logging

from datetime import datetime, timedelta

from .apis.twitch import helix
from .apis.twitch import User, Member
from .models import Context, Message
from .models.command import Cog, Command

from .exceptions import BotException
from .parser import Parser, ParseError

from typing import Dict, Union, Optional, Any, List


class RamrameyBot:
    update_interval: int = 60*10  # Seconds

    def __init__(self,
                 user: str,
                 client_id: str,
                 token: str,
                 joining_channels: List[str],
                 api_token: str = "",
                 host: str = "irc.twitch.tv",
                 port: int = 6667,
                 command_prefix: str = "!"):
        # Bot info
        self._user = user
        self.user: Optional[User] = None
        self.client_id = client_id
        self.token = token
        self.api_token = api_token
        self.command_prefix = command_prefix

        # Server info
        self.host = host
        self.port = port

        self.api = helix

        # Cached objects
        self._users: Dict[str, List[Union[User, datetime]]] = {}

        # Add parser
        self.parser = Parser()

        # Bot implements
        self.keep_running = True
        self.loop = asyncio.get_event_loop()

        self.logger = logging.getLogger(getattr(self.__class__, "__name__", "RamrameyBot"))
        self.logger.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(colorlog.ColoredFormatter(
            "%(log_color)s[%(asctime)s][%(levelname)s %(filename)s:%(lineno)d] %(message)s%(reset)s",
            log_colors={
                "INFO": "green",
                "WARN": "yellow",
                "EXCEPTION": "red",
                "ERROR": "red",
                "CRITICAL": "red",
                "NOTSET": "white",
                "DEBUG": "white"
            },
            style="%"
        ))
        self.logger.addHandler(console_handler)

        self.message_queue = []
        self.socket: Optional[socket.socket] = socket.socket()

        self.cogs: Dict[str, Any] = {}
        self.extensions: Dict[str, Any] = {}
        self.commands: Dict[str, List[Union[Command, Cog]]] = {}  # Dict<str> -> Val: List[async func, Cog]
        self.callbacks: Dict[str, List[Any]] = {}

        self.joining_channels = joining_channels
        self.joined_channels: List[Union[str, User]] = []

    async def test(self):
        data = await self.api.GetUsers(client_id=self.client_id, authorization=self.api_token)\
            .perform(logins=["eunhaklee", "return0927", "ramramey"])
        for user in data:
            print(user.id, user.login, user.display_name, user.offline_image_url)

    # -------------------------------------------------- #
    # Socket transaction
    async def send_raw(self, data: bytes):
        """Send raw packet via socket connection"""
        self.socket.send(data)
        return await self.call_listener("on_raw", data, is_outgoing=True)

    async def send_msg(self, channel: Union[str, User, Member], data: str):
        """Send message to a specific channel"""
        if hasattr(channel, 'login'):  # If User of Member
            channel: str = channel.login

        await self.send_raw("PRIVMSG #{} :{}\n".format(channel, data).encode())

    # -------------------------------------------------- #
    # Extension management
    def add_cog(self, cog: Cog):
        if not isinstance(cog, Cog):
            raise TypeError("A cog must be a Cog")

        members = inspect.getmembers(cog)
        for name, member in members:
            if isinstance(member, Command):
                self.add_command(member, cog)

            if hasattr(member, "__cog_listener__") and getattr(member, "__cog_listener__"):
                self.add_listener(member)

        self.cogs[cog.__cog_name__] = cog

    def get_cog(self, name: str) -> Cog:
        return self.cogs.get(name)

    def remove_cog(self, name: str):
        # TODO: Make this
        return

    def add_command(self, cmd, parent):
        """Register a command :class:`Command` into TwitchBot.

        Parameters
        -----------------
        cmd
            The command to add.
        parent
            The Cog containing the command

        Raises
        ---------
        Exception
            If the command is already registered
        TypeError
            If the passed command is not a subclass of :class:`Command`.

        Returns
        ---------
        None
        """
        if not isinstance(cmd, Command):
            raise TypeError("This object was not defined as a subclass of Command")

        for name in cmd.name:
            if name in self.commands.keys():
                raise Exception(f"Command {name} was already registered")

            self.commands[name] = [cmd, parent]

    def add_listener(self, func, name=None):
        """Register a listener event :class:`function`

        Parameters
        -----------------
        func
            The corutine function to process an event.
        name
            A specific name of function

        Raises
        ---------
        Exception
            If the command is not a coroutine functinon.

        Returns
        ---------
        None
        """
        name = func.__name__ if name is None else name

        if not asyncio.iscoroutinefunction(func):
            raise Exception("Listener must be coroutines")

        if name not in self.callbacks.keys():
            self.callbacks[name] = []

        self.callbacks[name].append(func)

    def load_extension(self, name):
        if name in self.extensions:
            return

        lib = importlib.import_module(name)
        if not hasattr(lib, 'setup'):
            del lib
            del sys.modules[name]

            raise Exception("This module has not to setup.")

        lib.setup(self)
        self.extensions[name] = lib

    async def call_listener(self, name: str, *args, **kwargs):
        listeners: list = self.callbacks.get(name, [])
        self.logger.debug("Calling Listener: Found {} listeners with name {}".format(len(listeners), name))

        for listener in listeners:
            await listener(*args, **kwargs)

    # -------------------------------------------------- #
    # Message management
    async def enqueue_message(self, data: bytes) -> None:
        """Enqueue bytes to messages queue"""
        data = data.decode().replace("\r\n", "\n").split("\n")[:-1]
        return self.message_queue.extend(data)

    async def dequeue_message(self) -> str:
        """Dequeue one message from messages queue"""
        if self.message_queue:
            return self.message_queue.pop(0)

        data = None
        while not data:
            data = self.socket.recv(2 ** 20)

        await self.enqueue_message(data)
        return await self.dequeue_message()

    # -------------------------------------------------- #
    # Users
    async def wrap_user(self, login: str, temp_wrap=False) -> User:
        if login in self._users:
            cached_user, updated_time = self._users.get(login)
            self.logger.debug("Cached User " + login + " with cached time " + str(updated_time))

            if datetime.now() - updated_time > timedelta(seconds=self.update_interval) and not temp_wrap:
                self.logger.debug("Refreshing cache of user " + login)
                user = await self.fetch_user(login)
                self._users[login] = [user, datetime.now()]

                return user

            return cached_user

        else:
            if temp_wrap:
                user = User(
                    id=0,
                    type="",
                    login=login,
                    description="",
                    display_name="",
                    broadcaster_type="",
                    profile_image_url="",
                    offline_image_url="",
                )
                self._users[login] = [user, datetime.utcfromtimestamp(0)]
            else:
                user = await self.fetch_user(login)
                self._users[login] = [user, datetime.now()]

            return user

    async def fetch_user(self, login: str) -> User:
        api = self.api.GetUsers(client_id=self.client_id, authorization=self.api_token)
        result = await api.perform(logins=login)

        user = result[0]

        return user

    # -------------------------------------------------- #
    # Process command
    async def process_command(self, ctx: Context):
        msg = ctx.message.content

        if not msg.startswith(self.command_prefix):
            return

        command, *args = msg[len(self.command_prefix):].split(" ")

        for cmd, v in self.commands.items():
            if cmd == command:
                func: Command = v[0]
                cog: Cog = v[1]

                if func.pass_context:
                    await func.callback(cog, ctx)
                else:
                    await func.callback(cog)

                time_taken = datetime.now() - ctx.message.enqueued_time
                self.logger.debug("Func `{}` took `{}`ms".format(func.name, time_taken))

    # -------------------------------------------------- #
    # Build & Run bot
    async def _prepare(self):
        self.socket.connect((self.host, self.port))

    async def _run(self):
        await self._prepare()
        await self.send_raw("PASS oauth:{}\n".format(self.token).encode())
        await self.send_raw("NICK {}\n".format(self.user).encode())

        for channel in self.joining_channels:
            await self.send_raw("JOIN #{}\n".format(channel).encode())

        while self.keep_running:
            try:
                data = await self.dequeue_message()
                start = datetime.now()

                await self.call_listener("on_raw", data)

                mode, meta = self.parser.parse_message(data)
                self.logger.debug("{} {} {}".format(datetime.now().strftime("%Y-%m-%d %T"), mode, meta))

                # -------------------- #
                #      PING / PONG     #
                # -------------------- #
                if mode == "PONG":  # If PONG response, which would not be created
                    pass
                elif mode == "PING":  # If PING request, make PONG response
                    host = meta.get("host", "tmi.twitch.tv")
                    await self.send_raw("PONG :{}\r\n".format(host).encode())

                # -------------------- #
                #        PRIVMSG       #
                # -------------------- #
                elif mode == "PRIVMSG":
                    # meta -> user, channel, content

                    user = await self.wrap_user(meta.get("user"), temp_wrap=True)
                    channel = await self.wrap_user(meta.get("channel"), temp_wrap=True)
                    content = meta.get("content")

                    message = Message(channel=channel, chatter=user,
                                      content=content, raw=data,
                                      type="chat", enqueued_time=datetime.now())
                    ctx = Context.make_from_message(bot=self, message=message, type="chat")

                    await self.call_listener("on_message", ctx)
                    await self.process_command(ctx)

                    self.logger.debug("Message `{}` took {} on process".format(mode, datetime.now() - start))

            except BotException as ex:
                self.logger.exception(" > Ignoring bot exception> " + str(ex))

            finally:
                await asyncio.sleep(.01)

        return

    def run(self):
        self.loop.run_until_complete(self.test())
        self.loop.run_until_complete(self._run())
