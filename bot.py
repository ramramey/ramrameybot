from ramrameybot import Bot
import json


extensions = [
    "cogs.basic_commands",
    "cogs.console_logger"
]

client = Bot(
    **json.load(open("config.json", "r", encoding="UTF-8")),
    cogs=extensions
)

client.run()
