import os
import sys
import pkgutil
import logging
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8') # type: ignore

from wordle_suggester.utils.cleaner import cleanup_old_logs

logs_dirname = Path(__file__).parent / "logs" 
logs_dirname.mkdir(exist_ok=True)
cleanup_old_logs(logs_dirname, max_files=10)
curr_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

handlers = [
    logging.StreamHandler(sys.stdout),
    logging.FileHandler(filename=logs_dirname / (curr_time + ".log"), encoding="utf-8")
]
logging.basicConfig(handlers=handlers, level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s')


from dotenv import load_dotenv
import discord

import wordle_suggester.cogs as cogs_package


load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

bot = discord.Bot()

for module_info in pkgutil.iter_modules(cogs_package.__path__):
    bot.load_extension(f"{cogs_package.__name__}.{module_info.name}")

bot.run(TOKEN)