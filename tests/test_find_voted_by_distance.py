from donbot.vc.vote_parser import VoteParser


def test_match_slightly_mispelled_voted():
    vote = VoteParser(["Mariyta", "moose200x"]).find_voted("Moos200x")
    assert vote == "moose200x"


def test_match_vote_with_equal_edit_distances_but_obvious_correct():
    "Post Reference: 15787, 349"
    vote = VoteParser(["Xtoxm", "moose200x"]).find_voted("Moose")
    assert vote == "moose200x"

def test_ignore_vote_for_deadline_extension():
    "Post Reference: 15783, 557"
    players = [
        "singersigner",
        "Nachomamma8",
        "ConfidAnon",
        "AGar",
        "Powerrox93",
        "Guderian",
        "Rhinox",
        "iamausername",
        "sims5487",
        "Seraphim",
        "mothrax",
        "Blood Queen",
        "Thor665",
        "Reckamonic",
        "Lateralus22",
        "Carrotcake",
    ]
    vote = VoteParser(players).find_voted("Deadline Extention")
    assert not vote


def test_ignore_request_for_votecount():
    'A request for a votecount is not counted, even if a hypothetical player "Count" exists.'
    vote = VoteParser(["moose200x"]).find_voted("count?")
    assert not vote