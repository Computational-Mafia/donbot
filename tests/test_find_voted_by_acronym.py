from donbot.vc.vote_parser import VoteParser

def test_match_TMHS_by_acronym():
    """
    Tests that a vote for a player by acronym is counted.

    Relevant phases:
    1098, D1: https://forum.mafiascum.net/viewtopic.php?p=2695031#p2695031
    """
    players = [
        "EmpTyger",
        "Nul",
        "Substrike22",
        "Llamarble",
        "Pinewolf",
        "Amor",
        "Scott Brosius",
        "Internet Stranger",
        "themanhimself",
        "Guderian",
        "RobCapone",
        "Shattered Viewpoint",
        "chkflip",
        "WeirdRa",
        "brokenscraps",
        "Kingcheese",
    ]
    voted = VoteParser(players, flag_unmatched_votes=True).find_voted("TMHS")
    assert voted == "themanhimself"

def test_match_SB_by_acronym():
    """
    Tests that a vote for a player by acronym is counted.

    Relevant phases:
    1098, D1: https://forum.mafiascum.net/viewtopic.php?p=2695031#p2695031
    """
    players = ['EmpTyger', 'Nul', 'Substrike22', 'Amor', 'Scott Brosius', 'Internet Stranger', 'Guderian', 'RobCapone', 'Shattered Viewpoint', 'brokenscraps', 'Kingcheese']
    voted = VoteParser(players, flag_unmatched_votes=True).find_voted("SB")
    assert voted ==  'Scott Brosius'