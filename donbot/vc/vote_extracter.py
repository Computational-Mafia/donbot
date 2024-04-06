from lxml.html import HtmlElement
from typing import Generator


def get_vote_strings(post_html: HtmlElement) -> Generator[str, None, None]:
    """
    Extracts text of votes from a post without attempting further parsing or identification.
    
    Args:
        post_html: The HTML element of the post.

    Returns:
        A generator of the vote strings in the post.
    """

    for vote in post_html.xpath("//div[contains(text(), 'vote:')]"):
        yield vote.text_content().split(":")[1].strip()


def includes_vote(post_html: HtmlElement) -> bool:
    """
    Determines whether a post includes a vote.
    
    Args:
        post_html: The HTML element of the post.

    Returns:
        True if the post includes a vote, False otherwise.
    """
    
    return len(list(get_vote_strings(post_html))) > 0


class VoteExtracter:

    def __init__(self, players):
        self.players = players

    def from_post(self, post):
        yield from get_vote_strings(post)
        