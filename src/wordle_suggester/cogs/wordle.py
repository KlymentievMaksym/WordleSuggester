from pathlib import Path

import discord
import discord.ext.commands as cmnd
import pandas as pd

from wordle_suggester.utils.entropy import calculate_best_word

class Wordle(cmnd.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="suggest", description="Suggest next possible n words")
    async def suggest(
        self,
        ctx: discord.ApplicationContext,
        word: str = discord.Option(str, description="Enter word to start from"), # type: ignore
        colors: str = discord.Option(str, description="Enter colors in format like '00201', 'ddgdy', '  g y' or 'gray, gray, green, gray, yellow"), # type: ignore
        best_n: int = discord.Option(int, description="Enter integer to receive that or smaller amount of answers", default=1), # type: ignore
        private: bool = discord.Option(bool, description="Enter True or False to choose whether share message with others or not share", default=True) # type: ignore
    ):
        available_words = pd.read_csv(Path(__file__).parent.parent / "data" / "filtered-wordle-words.csv", header=None)
        available_words = available_words[0].apply(lambda x: x.lower()).tolist()
        best_words = calculate_best_word(word.lower(), colors.lower(), available_words, best_n)
        await ctx.respond(f"Best **{min(best_n, len(best_words))}** recommended words: **{' | '.join([word.upper() for word in best_words]) if best_words else 'There is no recommended word available'}**", ephemeral=private)


def setup(bot: discord.Bot):
    bot.add_cog(Wordle(bot))