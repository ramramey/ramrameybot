from ramrameybot import Bot
import json


extensions = [
    "cogs.basic_commands",
    "cogs.minecraft",
    "cogs.debug"
]

client = Bot(
    **json.load(open("config.json", "r", encoding="UTF-8"))
)

for cog in extensions:
    client.load_extension(cog)

print(" > Extensions", [*client.extensions.keys()])
print(" > Cogs", [*client.cogs.keys()])
print(" > Commands", [*client.commands.keys()])
print(" > Listeners", client.callbacks)

client.run()
