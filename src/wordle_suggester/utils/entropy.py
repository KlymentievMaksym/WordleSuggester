import numpy as np
from collections import defaultdict, Counter

alternatives = {"g": "green", "2": "green", "y": "yellow", "1": "yellow", "d": "gray", " ": "gray", "0": "gray"}
accessable = ["green", "yellow", "gray"]

def filter_words(word: str, colors: list[str], available_words: list[str]) -> list[str]:
    suitable_words = []
    for candidate in available_words:
        is_valid = True

        for i in range(5):
            guess_letter = word[i]
            candidate_letter = candidate[i]
            color = colors[i].lower()
            if color in alternatives:
                color = alternatives[color]
            if color not in accessable:
                raise ValueError(f"Not suitable color for '{color}'")

            if ((color == "green" and guess_letter != candidate_letter)
                or (color == "gray" and guess_letter in candidate)
                or (color == "yellow" and (guess_letter == candidate_letter or guess_letter not in candidate))
            ):
                is_valid = False
                break

        if is_valid:
            suitable_words.append(candidate)
    return suitable_words


def get_pattern(guess: str, secret: str) -> list[str]:
    pattern = ["gray" for _ in range(5)]
    available_letters = list(secret)

    for i in range(5):
        if guess[i] == secret[i]:
            pattern[i] = "green"
            available_letters.remove(secret[i])

    for i in range(5):
        if guess[i] in available_letters and pattern[i] != "green":
            pattern[i] = "yellow"
            available_letters.remove(guess[i])

    return pattern

def calculate_entropy(guess: str, available_words: list[str]) -> float:
    pattern_counts = defaultdict(int)
    total_count = len(available_words)

    for secret in available_words:
        pattern_list = get_pattern(guess, secret)
        pattern_str = ",".join(pattern_list)
        pattern_counts[pattern_str] += 1
        
    entropy = 0.0
    
    for pattern, count in pattern_counts.items():
        Pr = count/total_count
        entropy -= Pr * np.log2(Pr)
    
    return entropy

def calculate_best_word(word: str, colors: str, available_words: list[str], best_n: int = 1) -> list[str]:
    if len(colors.split(",")) == 1:
        colors_list = list(colors)
    else:
        colors_list = list(color.strip() for color in colors.split(","))
    # print(colors_list)
    available_words = filter_words(word, colors_list, available_words)

    guesses_entropy = defaultdict(float)
    for guess in available_words:
        guess_entropy = calculate_entropy(guess, available_words)
        guesses_entropy[guess] += guess_entropy

    sorted_items = sorted(guesses_entropy.items(), key=lambda item: item[1], reverse=True)
    sorted_best_guesses = [item[0] for item in sorted_items]
    return sorted_best_guesses[:best_n]