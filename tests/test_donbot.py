import donbot
from donbot.operations import count_posts

def test_credentials_exist():
    "Credentials should be loaded from 'credentials.json' file"

    username, password = donbot.load_credentials()

    assert username is not None
    assert password is not None
    assert len(username) > 0
    assert len(password) > 0


def test_count_posts():
    "Donbot should be able to count posts in a speakeasy thread if credentials are valid"

    username, password = donbot.load_credentials()
    session = donbot.login(username, password)
    assert(count_posts(session, 'https://forum.mafiascum.net/viewtopic.php?f=53&t=84030') == 15)


def test_get_user_id():
    "Donbot should be able to get a user's ID"

    username, password = donbot.load_credentials()
    session = donbot.login(username, password)
    assert(donbot.get_user_id(session, 'Psyche') == '15830')

def test_get_activity_overview():
    "Donbot should be able to get a thread's activity overview"

    username, password = donbot.load_credentials()
    session = donbot.login(username, password)

    activity_overview = donbot.get_activity_overview(session, 'https://forum.mafiascum.net/viewtopic.php?f=53&t=84030')

    assert(len(activity_overview) == 6)
    assert(activity_overview[0]['user'] == 'Ythan')
    assert(activity_overview[0]['firstpost'] == 'Sun Aug 23, 2020 4:04 pm')
    assert(activity_overview[0]['lastpost'] == 'Wed Aug 26, 2020 1:21 pm')
    assert(activity_overview[0]['sincelast'] == '1252 days 20 hours')
    assert(activity_overview[0]['totalposts'] == '3')