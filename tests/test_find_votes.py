from donbot.vc.vote_parser import find_votes
from donbot.operations import string_to_html


def test_detect_vote_in_bold_font():
    "Post Reference: 15787, 14"
    post_content = '<div style="display:inline;font-weight:bold">Vote: Mariyta</div>'
    votes = list(find_votes(string_to_html(post_content)))
    assert votes == ["Mariyta"]


def test_detect_vote_without_colon():
    "Post Reference: 15787, 21"
    post_content = '<div style="display:inline;font-weight:bold">vote hiraki</div>'
    votes = list(find_votes(string_to_html(post_content)))
    assert votes == ["hiraki"]


def test_detect_vote_in_bbvote_tag():
    "Post Reference: 15787, 16"
    post_content = (
        '<span class="bbvote" title="This is an official vote.">VOTE: Mariyta</span>'
    )
    votes = list(find_votes(string_to_html(post_content)))
    assert votes == ["Mariyta"]


def test_ignore_nonvote_inside_bold():
    "Post Reference: 15787, 33"
    post_content = '<span class="noboldsig">Moose</span>'
    votes = list(find_votes(string_to_html(post_content)))
    assert not votes


def test_track_bbvote_unvote():
    "Post Reference: 15787, 51"
    post_content = '<span class="bbvote" title="This is an official unvote.">UNVOTE: Mr Wright</span>'
    votes = list(find_votes(string_to_html(post_content)))
    assert votes == ["UNVOTE"]


def test_track_multiline_multivote():
    post_content = '<span class="noboldsig">Unvote;<br>Vote: Substrike22</span>'
    votes = list(find_votes(string_to_html(post_content)))
    assert votes[-1] == "Substrike22"


def test_ignore_votes_inside_quotations():
    post_content = (
        '<blockquote><span class="noboldsig">vote hiraki</span></div></blockquote>'
    )
    votes = list(find_votes(string_to_html(post_content)))
    assert not votes


def test_ignore_bolded_directive_not_to_vote():
    post_content = (
        '<span class="noboldsig">Please, everyone! Do not vote hiraki</span></div>'
    )
    votes = list(find_votes(string_to_html(post_content)))
    assert not votes


def test_dont_ignore_bold_vote_inside_area_tags():
    post_content = '<fieldset style="border:3px outset grey;padding:5px 10px"><div style="display:inline;font-weight:bold">vote Psyche</div></fieldset>'
    votes = list(find_votes(string_to_html(post_content)))
    assert votes == ["Psyche"]


def test_dont_ignore_bbvote_inside_underline_tags():
    post_content = '<div style="display:inline;text-decoration:underline"><span class="bbvote" title="This is an official vote.">VOTE: vote Psyche</span></div><br>'
    votes = list(find_votes(string_to_html(post_content)))
    assert votes == ["Psyche"]


def test_dont_ignore_unvote_inside_size_tags():
    post_content = '<div style="font-size: 150%; line-height: normal; display: inline"><span class="bbvote" title="This is an official unvote.">UNVOTE: </span></div><br>'
    votes = list(find_votes(string_to_html(post_content)))
    assert votes == ["UNVOTE"]


def test_dont_ignore_bold_vote_inside_list_tags():
    post_content = '<ul><li><div style="display:inline;font-weight:bold">vote: Psyche</div></li></ul>'
    votes = list(find_votes(string_to_html(post_content)))
    assert votes == ["Psyche"]


def test_dont_ignore_bbvote_inside_ooc_tags():
    post_content = '<span class="bbvote" title="This is an official vote.">VOTE: <span style="color:darkred;font-size:smaller" title="This text is being given out-of-character.">Psyche</span></span></div>'
    votes = list(find_votes(string_to_html(post_content)))
    assert votes == ["Psyche"]


def test_dont_ignore_bbvote_that_nests_color_tags():
    post_content = '<span class="bbvote" title="This is an official vote.">VOTE: <div style="display:inline;color:white">Psyche</div></span></div>'
    votes = list(find_votes(string_to_html(post_content)))
    assert votes == ["Psyche"]
