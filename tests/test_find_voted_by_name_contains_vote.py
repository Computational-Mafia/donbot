from donbot.vc.vote_parser import VoteParser

def test_match_vote_is_misspelled_substring_of_player():
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
    voted = VoteParser(players, flag_unmatched_votes=True).find_voted("ScottBro")
    assert voted == "Scott Brosius"
