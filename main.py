import os
import pkgutil

from dotenv import load_dotenv
import discord

import wordle_suggester.cogs as cogs_package


load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot = discord.Bot()

for module_info in pkgutil.iter_modules(cogs_package.__path__):
    bot.load_extension(f"{cogs_package.__name__}.{module_info.name}")

bot.run(TOKEN)