import asyncio


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

