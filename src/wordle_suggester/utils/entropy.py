import numpy as np
from collections import defaultdict, Counter

alternatives = {"g": 2, "green": 2, "2": 2, "yellow": 1, "y": 1, "1": 1, "gray": 0, "d": 0, " ": 0, "0": 0}
accessable = [0, 1, 2]

def filter_words(word: str, colors: tuple[int, ...], available_words: list[str]) -> list[str]:
    # print(colors, word)

    suitable_words = []
    for candidate in available_words:
        candidate_pattern = get_pattern(word, candidate)

        if candidate_pattern == colors:
            suitable_words.append(candidate)

    # print(suitable_words)
    return suitable_words


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

# def get_pattern_multiple(guesses: list[str], secrets: list[str]) -> :

def calculate_entropy(guess: str, available_words: list[str]) -> float:
    pattern_counts = defaultdict(int)
    total_count = len(available_words)

    for secret in available_words:
        patterns = get_pattern(guess, secret)
        # pattern_str = ",".join(pattern_list)
        pattern_counts[patterns] += 1
        
    entropy = 0.0
    
    for count in pattern_counts.values():
        Pr = count/total_count
        entropy -= Pr * np.log2(Pr)
    
    return entropy

def create_colors_from_str(colors: str) -> tuple[int, ...]:
    if len(colors.split(",")) == 1:
        colors_list = list(color.lower() for color in colors)
    else:
        colors_list = list(color.strip().lower() for color in colors.split(","))

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

def color_word_using_colors(word: str, colors: tuple[int, ...]):
    formater = {
        2: "\033[2;32m",
        1: "\033[2;33m",
        0: "\033[2;30m",
        "reset": "\033[0m"
    }
    color_word = formater["reset"]
    for color_index in range(len(colors)):
        color_word += formater[colors[color_index]] + word[color_index] + formater["reset"]
    return color_word

def calculate_best_word(word: str, colors: str, available_words: list[str], best_n: int = 1) -> tuple[list[str], list[float]]:
    if len(word) != 5:
        raise ValueError(f"Expected word length 5, received {len(word)}")

    colors_list = create_colors_from_str(colors)

    available_words = filter_words(word, colors_list, available_words)

    guesses_entropy = defaultdict(float)
    for guess in available_words:
        guess_entropy = calculate_entropy(guess, available_words)
        guesses_entropy[guess] += guess_entropy

    sorted_items = sorted(guesses_entropy.items(), key=lambda item: item[1], reverse=True)
    sorted_best_guesses = [item[0] for item in sorted_items]
    sorted_best_entropies = [item[1] for item in sorted_items]
    return sorted_best_guesses[:best_n], sorted_best_entropies[:best_n]