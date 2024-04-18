from donbot.vc.vote_parser import VoteParser


def test_vote_with_misspelled_name_in_bold_font():
    "Make sure we correctly match slightly misspelled names in bold font."
    players = ["Mariyta", "moose200x"]
    post_content = 'And that\'s nine.<br><br>Hi, Mariyta!<br><br><span class="noboldsig"> Vote: Moos200x </span>'
    votes = list(VoteParser(players).from_post(post_content))
    assert votes == ["moose200x"]


def test_vote_with_no_colon_in_bold_font():
    "Make sure we correctly parse votes missing a colon after the word 'vote' in bold font."
    players = ["Hiraki"]
    post_content = 'And that\'s nine.<br><br>Hi, Mariyta!<br><br><span class="noboldsig">vote hiraki</span>'
    votes = list(VoteParser(players).from_post(post_content))
    assert votes == ["Hiraki"]


def test_vote_in_bbvote_tag():
    "Make sure we correctly parse votes in bbvote tags."
    players = ["Mr Wright"]
    post_content = 'And that\'s nine.<br><br>Hi, Mariyta!<br><br><span class="bbvote" title="This is an official vote.">VOTE: Mr Wright</span>'
    votes = list(VoteParser(players).from_post(post_content))
    assert votes == ["Mr Wright"]


def test_ignore_nonvote_inside_bold():
    players = ["moose200x"]
    post_content = '<span class="noboldsig">Moose</span>'
    votes = list(VoteParser(players, flag_unmatched_votes=True).from_post(post_content))
    assert not votes


def test_track_bbvote_unvote():
    players = ["Xtoxm", "moose200x"]
    post_content = '<span class="bbvote" title="This is an official unvote.">UNVOTE: Mr Wright</span>'
    votes = list(VoteParser(players).from_post(post_content))
    assert votes == ["UNVOTE"]


def test_count_vote_for_no_lynch():
    """
    Tests that a vote for No lynch is counted.

    Relevant phases:
    1094, D3: https://forum.mafiascum.net/viewtopic.php?p=2722607#p2722607
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
    post_content = '<span class="noboldsig">Vote: No Lynch</span>'
    votes = list(VoteParser(players).from_post(post_content))
    assert votes == ["NO LYNCH"]


def test_multiline_multivote():
    players = ["Substrike22"]
    post_content = '<span class="noboldsig">Unvote;<br>Vote: Substrike22</span>'
    votes = list(VoteParser(players).from_post(post_content))
    assert votes[-1] == "Substrike22"


def test_ignore_vote_inside_quote():
    "Make sure we ignore votes inside blockquote tags."
    players = ["Hiraki"]
    post_content = (
        '<blockquote><span class="noboldsig">vote hiraki</span></div></blockquote>'
    )
    votes = list(VoteParser(players, flag_unmatched_votes=True).from_post(post_content))
    assert not votes


def test_ignore_bolded_directive_not_to_vote():
    "Make sure we ignore votes inside blockquote tags."
    players = ["Hiraki"]
    post_content = (
        '<span class="noboldsig">Please, everyone! Do vote hiraki</span></div>'
    )
    votes = list(VoteParser(players, flag_unmatched_votes=True).from_post(post_content))
    assert not votes


def test_do_not_ignore_votes_inside_nonquote_tags():
    "Make sure we do not ignore votes nested inside other tags that are not blockquote."
    players = ["Psyche"]
    post_content = """<fieldset style="border:3px outset grey;padding:5px 10px"><div style="display:inline;font-weight:bold">vote Psyche</div></fieldset><br>
<br>
<div style="display:inline;text-decoration:underline"><span class="bbvote" title="This is an official vote.">VOTE: vote Psyche</span></div><br>
<br>
<div style="font-size: 150%; line-height: normal; display: inline"><span class="bbvote" title="This is an official unvote.">UNVOTE: </span></div><br>
<span class="noboldsig">Please, everyone! Do vote hiraki</span></div>
<ul><li><div style="display:inline;font-weight:bold">vote: Psyche</div></li></ul>

<span class="bbvote" title="This is an official vote.">VOTE: <span style="color:darkred;font-size:smaller" title="This text is being given out-of-character.">Psyche</span></span></div>"""
    votes = list(VoteParser(players, flag_unmatched_votes=True).from_post(post_content))
    assert votes == ["Psyche", "Psyche", "UNVOTE", "Psyche", "Psyche"]


def test_match_vote_with_equal_edit_distances_but_obvious_correct():
    players = ["Xtoxm", "moose200x"]
    post_content = '<span class="noboldsig">Vote: Moose</span>'
    votes = list(VoteParser(players, flag_unmatched_votes=True).from_post(post_content))
    assert votes == ["moose200x"]


def test_ignore_vote_for_deadline_extension():
    """
    Tests that a vote for a deadline extension is not counted.

    In general, votes easily recognizable as not being for any applicable player should be ignored according to a principle of least surprise.

    Relevant phases:
    1094, Day 2: https://forum.mafiascum.net/viewtopic.php?p=2714062#p2714062

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
    post_content = '<span class="noboldsig">Vote: Deadline Extention</span>'
    votes = list(VoteParser(players).from_post(post_content))
    assert not votes


def test_ignore_request_for_votecount():
    'A request for a votecount is not counted, even if a hypothetical player "Count" exists.'
    players = ["moose200x"] #, "Count"]
    post_content = '<span class="noboldsig">Mod: Could we have a vote count?</span>'
    votes = list(VoteParser(players).from_post(post_content))
    assert not votes


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
    post_content = '<span class="noboldsig">unvote vote Lateralus\'s replacement</span>'
    votes = list(VoteParser(players, flag_unmatched_votes=True).from_post(post_content))
    assert "Lateralus22" in votes


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
    post_content = '<span class="bbvote" title="This is an official vote.">VOTE: Scott Brosius\' Slot</span>'
    votes = list(VoteParser(players, flag_unmatched_votes=True).from_post(post_content))
    assert "Scott Brosius" in votes


def test_match_vote_by_acronym():
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
    post_content = (
        '<span class="bbvote" title="This is an official vote.">VOTE: TMHS</span>'
    )
    votes = list(VoteParser(players, flag_unmatched_votes=True).from_post(post_content))
    assert "themanhimself" in votes


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
    post_content = '<span class="noboldsig">Vote Dramonerx</span>'
    votes = list(VoteParser(players, flag_unmatched_votes=True).from_post(post_content))
    assert "Reckamonic" in votes


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
    post_content = '<span class="noboldsig">unvote<br><br>Vote: ScottBro</span>'
    votes = list(VoteParser(players, flag_unmatched_votes=True).from_post(post_content))
    assert "Scott Brosius" in votes
