from pathlib import Path

import discord
import discord.ext.commands as cmnd

import numpy as np
import pandas as pd

from wordle_suggester.utils.entropy import calculate_best_word, create_colors_from_str, color_word_using_colors

class Wordle(cmnd.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot
        available_words = pd.read_csv(Path(__file__).parent.parent / "data" / "filtered-wordle-words.csv", header=None)
        # self.available_words_list = self.available_words[0].apply(lambda x: x.lower()).tolist()
        self.available_words_numpy = np.array(available_words[0].apply(lambda word: list(ord(letter) - 97 for letter in word.lower())).tolist(), dtype=np.int8)

    @discord.slash_command(name="suggest", description="Suggest next possible n words")
    async def suggest(
        self,
        ctx: discord.ApplicationContext,
        word: str = discord.Option(str, description="Enter words separated by space (e.g. 'crane apple', 'crane, apple')"), # type: ignore
        colors: str = discord.Option(str, description="Enter colors separated by space (e.g. '00201 11200', 'ddgdy, 11200', 'gray;gray;green;gray;yellow')"), # type: ignore
        best_n: int = discord.Option(int, description="Enter integer to receive that or smaller amount of answers", default=1), # type: ignore
        private: bool = discord.Option(bool, description="Enter True or False to choose whether share message with others or not share", default=True) # type: ignore
    ):
        try:
            word = word.lower()
            colors = colors.lower()
            best_words, best_entropies = calculate_best_word(word, colors, self.available_words_numpy, best_n)
            # text_to_respond = f"Best **{min(best_n, len(best_words))}** recommended words: **{' | '.join([word.upper() for word in best_words]) if best_words else 'There is no recommended word available'}**"

            words_list = word.replace(",", " ").split()
            colors_list_str = colors.replace(",", " ").split()

            base_words = []
            for _word, _color in zip(words_list, colors_list_str):
                colors_tuple = create_colors_from_str(_color)
                color_base_word = color_word_using_colors(_word.upper(), colors_tuple)
                base_words.append(color_base_word)

            text_to_respond = f"```ansi\n{", ".join(base_words)}```Best **{min(best_n, len(best_words))}** recommended next words:\n**```ansi\n{'{results}' if best_words else 'There is no recommended word available'}```**"

            colors_best_words = np.zeros((len(best_words), len(colors_tuple)), dtype=np.int8)
            for _word, _color in zip(words_list, colors_list_str):
                colors_tuple = create_colors_from_str(_color)
                colors_tuple = np.array(colors_tuple)
                colors_best_words = np.where(colors_tuple == 2, colors_tuple, colors_best_words)

            yellow_letters = []
            for _word, _color in zip(words_list, colors_list_str):
                colors_tuple = create_colors_from_str(_color)
                for letter, color in zip(_word, colors_tuple):
                    if color == 1:
                        yellow_letters.append(letter)
            for word_index, recommended_word in enumerate(best_words):
                for letter_index, letter in enumerate(recommended_word):
                    if letter in yellow_letters and colors_best_words[word_index][letter_index] != 2:
                        colors_best_words[word_index][letter_index] = 1

            results = f"{'\n'.join([f"{color_word_using_colors(recommended_word.upper(), tuple(colors_list))} | {entropy:.3f}" for recommended_word, colors_list, entropy in zip(best_words, colors_best_words, best_entropies)])}"
            text_to_respond = text_to_respond.format(results=results)

            await ctx.respond(text_to_respond, ephemeral=private)
        except ValueError as e:
            await ctx.respond(e, ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Wordle(bot))