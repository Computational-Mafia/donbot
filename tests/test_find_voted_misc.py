from donbot.vc.vote_parser import VoteParser


def test_match_to_no_lynch():
    "Post Reference: 15783, 586"
    vote = VoteParser(["singersigner", "AGar"]).find_voted("No Lynch")
    assert vote == "NO LYNCH"


def test_match_dramonerx_to_reckamonic():
    """
    Tests that a vote for a player by acronym is counted.

    Relevant phases:
    1094, D1, p10: 'https://forum.mafiascum.net/viewtopic.php?f=53&t=15783&start=0'
    """
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
    voted = VoteParser(players, flag_unmatched_votes=True).find_voted("Dramonerx")
    assert voted == "Reckamonic"


