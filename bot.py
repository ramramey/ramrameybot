from ramrameybot import Bot


extensions = [
    "cogs.basic_commands",
    "cogs.console_logger"
]

client = Bot(
    user="ramrameybot",
    client_id="8bz5vv13bu9w5kss68oflvzz3z3ge6",
    cogs=extensions
)

client.run()
