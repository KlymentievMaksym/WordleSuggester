import numpy as np
import numpy.typing as npt
from collections import defaultdict, Counter

alternatives = {"g": 2, "green": 2, "2": 2, "yellow": 1, "y": 1, "1": 1, "gray": 0, "d": 0, "0": 0}
accessable = [0, 1, 2]

def filter_words(word_numpy: npt.NDArray[np.int8], colors: tuple[int, ...], available_words_numpy: npt.NDArray[np.int8]) -> npt.NDArray[np.int8]:
    # print(colors, word)

    patterns = get_patterns_numpy(word_numpy, available_words_numpy)

    # (5)
    colors_numpy = np.array(colors, dtype=np.int8)
    # (N)
    suitable_word_indexes = (patterns == colors_numpy).all(axis=1)
    return available_words_numpy[suitable_word_indexes]

    # suitable_words = []
    # for candidate in available_words_numpy:
    #     candidate_pattern = get_pattern(word, candidate)

    #     if candidate_pattern == colors:
    #         suitable_words.append(candidate)

    # print(suitable_words)

def get_pattern(guess: str, secret: str) -> tuple[int, ...]:
    pattern = [0] * 5
    letter_counts = Counter(secret)

    for i in range(5):
        if guess[i] == secret[i]:
            pattern[i] = 2
            letter_counts[guess[i]] -= 1

    for i in range(5):
        if guess[i] in letter_counts and letter_counts[guess[i]] > 0 and pattern[i] != 2:
            pattern[i] = 1
            letter_counts[guess[i]] -= 1

    return tuple(pattern)

def get_patterns_numpy(word_numpy: npt.NDArray[np.int8], available_words_numpy: npt.NDArray[np.int8]) -> npt.NDArray[np.int8]:
    # (N, 5)
    green_matches = (available_words_numpy == word_numpy).astype(np.int8) * 2
    # (N, 5)
    possible_yellow_matches = np.where(green_matches == 2, -1, available_words_numpy)
    # (26)
    guess_counts = np.bincount(word_numpy, minlength=26)
    # (26)
    alphabet = np.arange(26)
    # (N, 5, 1) == (26) => (N, 26)
    words_counts = (possible_yellow_matches[:, :, np.newaxis] == alphabet).sum(axis=1)
    # (N, 5, 26) == (26) => (N, 26)
    match_counts = np.minimum(guess_counts, words_counts)
    # (N, 5)
    patterns = green_matches.copy()

    for i in range(5):
        letter = word_numpy[i]
        yellow_mask = (patterns[:, i] == 0) & (match_counts[:, letter] > 0)
        patterns[yellow_mask, i] = 1
        match_counts[yellow_mask, letter] -= 1

    return patterns

def calculate_entropy(guess_numpy: npt.NDArray[np.int8], available_words_numpy: npt.NDArray[np.int8]) -> float:

    total_count = available_words_numpy.shape[0]

    patterns = get_patterns_numpy(guess_numpy, available_words_numpy)
    unique_patterns, counts = np.unique(patterns, axis=0, return_counts=True)
        
    entropy = 0.0
    
    Pr = counts/total_count
    entropy -= np.sum(Pr * np.log2(Pr))
    
    return entropy

def create_colors_from_str(colors: str) -> tuple[int, ...]:
    colors = colors.strip()
    if len(colors.split(";")) == 1:
        colors_list = list(color.lower() for color in colors)
    else:
        colors_list = list(color.strip().lower() for color in colors.split(";"))

    if len(colors_list) != 5:
        raise ValueError(f"Expected colors length 5, received {len(colors_list)} ({colors_list})")

    colors_result = [0] * 5
    for color_index in range(len(colors_list)):
        color = colors_list[color_index]

        if color in alternatives:
            color = alternatives[color]

        if color not in accessable:
            raise ValueError(f"Not suitable color for '{color}'")

        colors_result[color_index] = color
    return tuple(colors_result)

def create_word_from_str(word: str) -> npt.NDArray[np.int8]:
    if not word.isalpha() or not word.isascii():
        raise ValueError(f"Please use English letters only, received {word}")
    if len(word) != 5:
        raise ValueError(f"Expected word length 5, received {len(word)}")
    return np.array(list(ord(letter) - 97 for letter in word.lower()), dtype=np.int8)

def color_word_using_colors(word: str, colors: tuple[int, ...]):
    formater = {
        2: "\033[2;32m",
        1: "\033[2;33m",
        0: "\033[2;30m",
        "reset": "\033[0m"
    }
    color_word = formater["reset"] + "".join([formater[colors[color_index]] + word[color_index] + formater["reset"] for color_index in range(len(colors))])
    # for color_index in range(len(colors)):
    #     color_word += formater[colors[color_index]] + word[color_index] + formater["reset"]
    return color_word

def format_with_emojis(colors: tuple[int, ...]) -> str:
    formater = {2: "🟩", 1: "🟨", 0: "⬛"}
    return "".join(formater[color] for color in colors)

# def calculate_best_word(word: str, colors: str, available_words_numpy: npt.NDArray[np.int8], best_n: int = 1) -> tuple[list[str], list[float]]:
def calculate_best_word(words_input: str, colors_input: str, available_words_numpy: npt.NDArray[np.int8], best_n: int = 1) -> tuple[list[str], list[float]]:
    
    words_list = words_input.replace(",", " ").split()
    colors_list_str = colors_input.replace(",", " ").split()

    if len(words_list) != len(colors_list_str):
        raise ValueError(f"Number of words does not match number of color patterns, received ({len(words_list)}) and ({len(colors_list_str)})")

    available_words = available_words_numpy
    for word, colors in zip(words_list, colors_list_str):
        word_numpy = create_word_from_str(word)
        colors_list = create_colors_from_str(colors)
        available_words = filter_words(word_numpy, colors_list, available_words)

    guesses_entropy = defaultdict(float)
    for guess in available_words:
        guess_entropy = calculate_entropy(guess, available_words)
        guesses_entropy["".join(chr(guess_letter + 97) for guess_letter in guess)] += guess_entropy

    sorted_items = sorted(guesses_entropy.items(), key=lambda item: item[1], reverse=True)
    sorted_best_guesses = [item[0] for item in sorted_items]
    sorted_best_entropies = [item[1] for item in sorted_items]
    return sorted_best_guesses[:best_n], sorted_best_entropies[:best_n]