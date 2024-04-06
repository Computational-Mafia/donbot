from donbot.vote_counting.vote_extracter import get_vote_strings
from lxml import html


def test_find_votes_in_minimal_post():
    post = html.fromstring(
        """<div style=\"display:inline;font-weight:bold\">vote: Hinduragi</div>"""
    )
    votes = list(get_vote_strings(post))
    assert votes == ["Hinduragi"]
