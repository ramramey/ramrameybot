import asyncio
import inspect


class Command:
    def __init__(self, name, callback, **attrs):
        self.name = name
        self.callback = callback
        self.aliases = attrs.pop('aliases', [])
        self.pass_context = attrs.pop('pass_context', True)


def command(name=None, **attrs):
    def decorator(func):
        if isinstance(func, Command):
            raise TypeError('Callback is already a command')
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Callback must be a coroutine')

        return Command(name=name or func.__name__, callback=func, **attrs)

    return decorator


class Cog:
    @property
    def __cog_name__(self) -> str:
        return self.__class__.__name__

    @classmethod
    def listener(cls):
        def decorator(func):
            actual = func

            if isinstance(actual, staticmethod):
                actual = actual.__func__

            if not inspect.iscoroutinefunction(actual):
                raise TypeError("Listener function must be a coroutine")

            actual.__cog_listener__ = True

            return func
        return decorator
