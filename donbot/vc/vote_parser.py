from lxml import html
from lxml.html import HtmlElement
from editdistance import eval as dist
from typing import Iterable
import re

reglower = re.compile('[^a-z]') # any character that IS NOT a-z

tag_paths = [
    "/html/body/span[contains(@class, '{}')]",
    "/html/body/div[contains(@style, '{}')]",
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
    "Extract text identifying the voted player from the content of a vote"
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
    # sourcery skip: for-append-to-extend, inline-variable
    words = vote_string.split()
    combinations = []
    for i in range(len(words)):
        for j in range(i + 1, len(words) + 1):
            combination = ' '.join(words[i:j])
            combinations.append(combination)
    return combinations


class VoteParser:
    def __init__(self, players: Iterable[str], flag_unmatched_votes: bool = False):
        self.players = ["NO LYNCH"] + list(players)
        self.lower_players = [p.lower() for p in self.players]
        self.flag_unmatched_votes = flag_unmatched_votes

    def from_post(self, post_content: str) -> Iterable[str]:
        post_html = html.fromstring(f"<html><body>{post_content}</body></html>")
        for vote in find_votes(post_html):
            if voted_player := self.find_voted(vote):
                yield voted_player

    def find_voted(self, vote: str) -> str:
        if vote == "UNVOTE":
            return "UNVOTE"
        lower_vote = vote.lower()

        if matched_player := self.match_by_playername_contains_vote(lower_vote, 3):
            return matched_player
        if matched_player := self.match_by_distance(lower_vote, 3):
            return matched_player
        if matched_player := self.match_by_vote_contains_playername(lower_vote, 3):
            return matched_player
        if self.flag_unmatched_votes:
            raise ValueError(f"Vote {vote} could not be resolved to a player")
        return ""

    def match_by_distance(self, lower_vote: str, threshold: int) -> str:
        "Matches based on edit distance, unless there is a tie or min distance is too large"
        distances = [dist(p, lower_vote) for p in self.lower_players]
        minimum_distance = min(distances)
        if minimum_distance < threshold and distances.count(minimum_distance) == 1:
            return self.players[distances.index(minimum_distance)]
        return ""

    def match_by_playername_contains_vote(self, lower_vote: str, threshold: int) -> str:
        "Matches based on if a unique player name contains a substring similar enough to vote."
        substring_matches = [""]
        for i, p in enumerate(self.lower_players):
            if lower_vote in p:
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
            if len(substring_matches) > 2:
                return ""
        return substring_matches[-1]
