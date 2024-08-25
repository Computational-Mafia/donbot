import re
from spellchecker import SpellChecker

spell = SpellChecker()


def normalize_input(input_string: str) -> str:
    """
    Returns the input_string with only its alphabetic characters.

    Args:
        input_string (str): The string to normalize.
    """
    return re.sub("[^a-zA-Z]", "", input_string)


def is_valid_word(substring: str) -> bool:
    """
    Returns True if the substring is a known word according to the spellchecker.

    Args:
        substring (str): The substring to check.
    """
    return not spell.unknown([substring])


def smallest_segment_length(segments: list[str]) -> int:
    """
    Returns length of the smallest segment in a list of segments

    Args:
        segments (List[str]): The list of segments to check.
    """
    if not segments:
        return 0  # Returns 0 if the list is empty, though this should not happen in your context
    return min(len(segment) for segment in segments)


def find_valid_substrings(
    start_index: int,
    current_combination: list[str],
    playername: str,
    results: list[list[str]],
) -> None:
    """
    Recursively find valid substrings starting from specified index.
    Update the results list with valid combinations.

    Args:
        start_index (int): The index from which to start the search in playername.
        current_combination (List[str]): The current combination of substrings found so far.
        playername (str): The full name being split into substrings.
        results (List[List[str]]): The list to which valid combinations of substrings are added.
    """
    for end_index in range(start_index + 1, len(playername) + 1):
        substring = playername[start_index:end_index]
        if is_valid_word(substring):
            new_combination = current_combination + [substring]
            if len("".join(new_combination)) == len(playername):
                results.append(new_combination)
            else:
                find_valid_substrings(end_index, new_combination, playername, results)


def split_into_english_words(playername: str) -> list[list[str]]:
    """
    Splits playername into all possible combos of substrings recognized as valid English words.
    Returns these combinations sorted based on:
      - the length of the smallest substring in descending order.
      - the number of substrings

    Args:
        playername (str): The name of the player to split.

    Returns:
        List[List[str]]: A sorted list of combinations, each combination being a list of valid English substrings.
    """
    playername = normalize_input(playername)
    results = []
    find_valid_substrings(0, [], playername, results)
    results.sort(key=lambda x: (-smallest_segment_length(x), len(x)))
    return results
