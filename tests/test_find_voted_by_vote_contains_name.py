from donbot.vc.vote_parser import VoteParser


def test_vote_contains_playername():
    "Tests that a vote containing a player's name but also a lot of other text is counted."

    players = [
        "Beefster",
        "werewolf555",
        "Hiraki",
        "Substrike22",
        "Antihero",
        "Lateralus22",
        "caelum",
        "boberz",
        "Mariyta",
        "brokenscraps",
        "LordChronos",
        "AntB",
        "pappums rat",
        "Mr Wright",
        "Ant_to_the_max",
        "Dekes",
        "Empking",
        "Xtoxm",
        "moose200x",
    ]
    vote = VoteParser(players, flag_unmatched_votes=True).find_voted(
        "Lateralus's replacement"
    )
    assert "Lateralus22" == vote


def test_vote_contains_abbreviated_playername_with_spaces():
    """
    Tests that a vote containing an abbreviation player's name is counted, but when the player's name is separated by spaces.
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
    vote = VoteParser(players, flag_unmatched_votes=True).find_voted(
        "Scott Brosius' Slot"
    )
    assert "Scott Brosius" == vote


def test_vote_():

    players = ['EmpTyger', 'Nul', 'Substrike22', 'Llamarble', 'Pinewolf', 'Amor', 'Scott Brosius', 'Internet Stranger', 'themanhimself', 'Guderian', 'RobCapone', 'Shattered Viewpoint', 'chkflip', 'WeirdRa', 'brokenscraps', 'Kingcheese']
    vote = VoteParser(players, flag_unmatched_votes=True).find_voted(
        'TheManHimself L - 1'
    )
    assert "themanhimself" == vote