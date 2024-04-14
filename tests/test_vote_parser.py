from donbot.vc.vote_parser import VoteParser


def test_vote_in_bold_font():
    post_content = '<span class="noboldsig">Vote: Mariyta</span>'
    players = ['Beefster', 'werewolf555', 'Hiraki', 'Substrike22', 'Antihero', 'Lateralus22', 'caelum', 'boberz', 'Mariyta', 'brokenscraps', 'LordChronos', 'AntB', 'pappums rat', 'Mr Wright', 'Ant_to_the_max', 'Dekes', 'Empking', 'Xtoxm', 'moose200x']
    votes = list(VoteParser(players).from_post({'content': post_content}))
    assert votes == ['Mariyta']

def test_bold_vote_in_longer_post():
    post_content = 'And that\'s nine.<br><br>Ohai, Mariyta!<br><br><span class="noboldsig">Vote: Mariyta</span>'
    players = ['Beefster', 'werewolf555', 'Hiraki', 'Substrike22', 'Antihero', 'Lateralus22', 'caelum', 'boberz', 'Mariyta', 'brokenscraps', 'LordChronos', 'AntB', 'pappums rat', 'Mr Wright', 'Ant_to_the_max', 'Dekes', 'Empking', 'Xtoxm', 'moose200x']
    votes = list(VoteParser(players).from_post({'content': post_content}))
    assert votes == ['Mariyta']

def test_bold_vote_in_implied_nested_span():
    post_content = '<span class="noboldsig">Vote: Ant_to_the_max</span><br><br>There is not enough room in this town for both Ants!'
    players = ['Beefster', 'werewolf555', 'Hiraki', 'Substrike22', 'Antihero', 'Lateralus22', 'caelum', 'boberz', 'Mariyta', 'brokenscraps', 'LordChronos', 'AntB', 'pappums rat', 'Mr Wright', 'Ant_to_the_max', 'Dekes', 'Empking', 'Xtoxm', 'moose200x']
    votes = list(VoteParser(players).from_post({'content': post_content}))
    assert votes == ['Ant_to_the_max']

def test_vote_with_misspelled_name():
    players = ['Beefster', 'werewolf555', 'Hiraki', 'Substrike22', 'Antihero', 'Lateralus22', 'caelum', 'boberz', 'Mariyta', 'brokenscraps', 'LordChronos', 'AntB', 'pappums rat', 'Mr Wright', 'Ant_to_the_max', 'Dekes', 'Empking', 'Xtoxm', 'moose200x']
    post_content = '<span class="noboldsig"> Vote: Moos200x </span>'
    votes = list(VoteParser(players).from_post({'content': post_content}))
    assert votes == ['moose200x']


def test_vote_with_no_colon():
    players = ['Beefster', 'werewolf555', 'Hiraki', 'Substrike22', 'Antihero', 'Lateralus22', 'caelum', 'boberz', 'Mariyta', 'brokenscraps', 'LordChronos', 'AntB', 'pappums rat', 'Mr Wright', 'Ant_to_the_max', 'Dekes', 'Empking', 'Xtoxm', 'moose200x']
    post_content = '<span class="noboldsig">vote hiraki</span>'
    votes = list(VoteParser(players).from_post({'content': post_content}))
    assert votes == ['Hiraki']


def test_vote_with_bbvote():
    players = ['Beefster', 'werewolf555', 'Hiraki', 'Substrike22', 'Antihero', 'Lateralus22', 'caelum', 'boberz', 'Mariyta', 'brokenscraps', 'LordChronos', 'AntB', 'pappums rat', 'Mr Wright', 'Ant_to_the_max', 'Dekes', 'Empking', 'Xtoxm', 'moose200x']
    post_content = '<span class="bbvote" title="This is an official vote.">VOTE: Mr Wright</span>'
    votes = list(VoteParser(players).from_post({'content': post_content}))
    assert votes == ['Mr Wright']


def test_ignore_vote_inside_quote():
    players = ['Beefster', 'werewolf555', 'Hiraki', 'Substrike22', 'Antihero', 'Lateralus22', 'caelum', 'boberz', 'Mariyta', 'brokenscraps', 'LordChronos', 'AntB', 'pappums rat', 'Mr Wright', 'Ant_to_the_max', 'Dekes', 'Empking', 'Xtoxm', 'moose200x']
    post_content = '<blockquote><span class="noboldsig">vote hiraki</span></div></blockquote>'
    votes = list(VoteParser(players).from_post({'content': post_content}))
    assert not votes


def test_ignore_nonvote_inside_bold():
    players = ['Beefster', 'werewolf555', 'Hiraki', 'Substrike22', 'Antihero', 'Lateralus22', 'caelum', 'boberz', 'Mariyta', 'brokenscraps', 'LordChronos', 'AntB', 'pappums rat', 'Mr Wright', 'Ant_to_the_max', 'Dekes', 'Empking', 'Xtoxm', 'moose200x']
    post_content = '<span class="noboldsig">Moose</span>'
    votes = list(VoteParser(players).from_post({'content': post_content}))
    assert not votes


def test_match_vote_with_equal_edit_distances():
    players = ['Xtoxm', 'moose200x']
    post_content = '<span class="noboldsig">Vote: Moose</span>'
    votes = list(VoteParser(players).from_post({'content': post_content}))
    assert votes == ['moose200x']


def test_track_bbvote_unvote():
    players = ['Xtoxm', 'moose200x']
    post_content = '<span class="bbvote" title="This is an official unvote.">UNVOTE: Mr Wright</span>'
    votes = list(VoteParser(players).from_post({'content': post_content}))
    assert votes == ['UNVOTE']
