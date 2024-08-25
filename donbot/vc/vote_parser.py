from lxml import html
from lxml.html import HtmlElement
from editdistance import eval as dist
from typing import Iterable
from .english_divides import split_into_english_words
import re

reglower = re.compile('[^a-z]') # any character that IS NOT a-z

tag_paths = [
    "//span[contains(@class, '{}') and not(ancestor::blockquote)]",
    "//div[contains(@style, '{}') and not(ancestor::blockquote)]",
]


def find_noboldsig_elements(post_html: HtmlElement):
    "Identify post content enclosed in noboldsig HTML tags"
    elements = []
    for path in tag_paths:
        elements.extend(post_html.xpath(path.format("noboldsig")))
    return elements


def find_style_bold_elements(post_html: HtmlElement):
    "Identify post content enclosed in style bold HTML tags"
    elements = []
    for path in tag_paths:
        elements.extend(post_html.xpath(path.format("font-weight:bold")))
    return elements


def find_bbvote_elements(post_html: HtmlElement):
    "Identify post content enclosed in vote HTML tags"
    elements = []
    for path in tag_paths:
        elements.extend(post_html.xpath(path.format("bbvote")))
    return elements


def find_broken_tag_elements(post_html: HtmlElement):
    "Identify post content enclosed in broken noboldsig or bbvote tags"
    return []


def find_votes(post_html: HtmlElement) -> Iterable[str]:
    """
    Detects possible votes in post content and retrieves their text content.

    Args:
        post_html: HTML element containing post content

    Returns:
        Iterable of strings that may identify the players voted for in the post
    """
    matched_elements = (
        find_noboldsig_elements(post_html)
        + find_style_bold_elements(post_html)
        + find_broken_tag_elements(post_html)
        + find_bbvote_elements(post_html)
    )
    for element in matched_elements:
        v = element.text_content().lstrip()

        # the latest vote or unvote is the only one that counts
        vote_location = v.lower().rfind("vote")
        unvote_location = v.lower().rfind("unvote")
        if unvote_location > -1 and unvote_location == vote_location - 2:
            yield "UNVOTE"
        elif vote_location > -1:
            yield v[vote_location + 4 :].replace(":", " ").rstrip().lstrip()


def includes_vote(post_html: HtmlElement) -> bool:
    "Determine if post content includes a vote"
    return len(list(find_votes(post_html))) > 0


def generate_contiguous_combinations(vote_string: str) -> list[str]:
    "Generate all contiguous combinations of words in a vote string"
    words = vote_string.split()
    combinations = []
    for i in range(len(words)):
        for j in range(i + 1, len(words) + 1):
            combination = ' '.join(words[i:j])
            combinations.append(combination)
    return combinations

def find_matching_substrings(searched_string: str, query_string: str, threshold: int):
    target_len = len(query_string)
    len_margin = threshold
    min_len = max(1, target_len - len_margin)
    max_len = target_len + len_margin
    
    for start in range(len(searched_string)):
        for end in range(start + min_len, min(start + max_len + 1, len(searched_string) + 1)):
            substring = searched_string[start:end]
            if dist(substring, query_string) <= threshold:
                return True
    return False


class VoteParser:

    def __init__(self, players: Iterable[str], flag_unmatched_votes: bool = False):
        self.flag_unmatched_votes = flag_unmatched_votes
        self.players = ["NO LYNCH"] + list(players)
        self.lower_players = [p.lower() for p in self.players]
        self.english_divides = {p: split_into_english_words(p) for p in self.lower_players}
        self.player_abbreviations = {}
        for p in self.lower_players:

            self.player_abbreviations[p] = ''.join([each[0] for each in self.english_divides[p][0]])

    def from_post(self, post_content: str) -> Iterable[str]:
        "Extract votes from post content"
        post_html = html.fromstring(f"<html><body>{post_content}</body></html>")
        for vote in find_votes(post_html):
            if voted_player := self.find_voted(vote):
                yield voted_player

    def find_voted(self, vote: str) -> str:
        "Match a vote to a player name"
        if vote == "UNVOTE":
            return "UNVOTE"
        lower_vote = vote.lower()

        if matched_player := self.match_by_distance(lower_vote, 0):
            return matched_player
        if matched_player := self.match_by_playername_contains_vote(lower_vote, 0):
            return matched_player
        if matched_player := self.match_by_playername_contains_vote(lower_vote, 1):
            return matched_player
        if matched_player := self.match_by_distance(lower_vote, 1):
            return matched_player
        if matched_player := self.match_by_distance(lower_vote, 2):
            return matched_player
        if matched_player := self.match_by_vote_contains_playername(lower_vote, 0):
            return matched_player
        if matched_player := self.match_by_vote_contains_playername(lower_vote, 1):
            return matched_player
        if matched_player := self.match_by_vote_contains_playername(lower_vote, 2):
            return matched_player
        if matched_player := self.match_by_inferred_acronym(lower_vote, 1):
            return matched_player
        if self.flag_unmatched_votes and vote[:5].lower() != "count" and dist(vote.lower(), 'deadline extension') > 2:
            raise ValueError(f"Vote {vote} could not be resolved to a player")
        return ""

    def match_by_distance(self, lower_vote: str, threshold: int) -> str:
        "Matches based on edit distance, unless there is a tie or min distance is too large"
        distances = [dist(p, lower_vote) for p in self.lower_players]
        minimum_distance = min(distances)
        if minimum_distance <= threshold and distances.count(minimum_distance) == 1:
            return self.players[distances.index(minimum_distance)]
        return ""

    def match_by_playername_contains_vote(self, lower_vote: str, threshold: int) -> str:
        "Matches based on if a unique player name contains a substring similar enough to vote."
        substring_matches = [""]
        for i, p in enumerate(self.lower_players):
            if find_matching_substrings(p, lower_vote, threshold):
                substring_matches.append(self.players[i])
            if len(substring_matches) > 2:
                return ""
        return substring_matches[-1]
    
    def match_by_vote_contains_playername(self, lower_vote: str, threshold: int) -> str:
        "Matches based on if vote contains a substring similar enough to a unique player name."
        vote_parts = generate_contiguous_combinations(lower_vote)
        substring_matches = [""]
        for vote_part in vote_parts:
            if distance_matching := self.match_by_distance(vote_part, threshold):
                substring_matches.append(distance_matching)
            if len(set(substring_matches)) > 2:
                return ""
        return substring_matches[-1]

    def match_by_inferred_acronym(self, lower_vote: str, threshold: int) -> str:
        "Matches based on if vote is an acronym for a player name"
        acronym_matches = [""]
        for i, p in enumerate(self.lower_players):
            if dist(self.player_abbreviations[p], lower_vote) <= threshold:
                acronym_matches.append(self.players[i])
            if len(acronym_matches) > 2:
                return ""
        return acronym_matches[-1]
