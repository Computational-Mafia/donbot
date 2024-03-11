from donbot.get_votes import get_votes
from lxml import html


def test_get_votes_from_minimal_post():
    post = html.fromstring(
        """<div style=\"display:inline;font-weight:bold\">vote: Hinduragi</div>"""
    )
    votes = get_votes(post)
    assert votes == ["Hinduragi"]
