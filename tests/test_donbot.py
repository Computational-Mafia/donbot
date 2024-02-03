from donbot import Donbot
from donbot.operations import load_credentials
from datetime import datetime

single_page_thread = "https://forum.mafiascum.net/viewtopic.php?f=53&t=84030"

def test_credentials_exist():
    "Credentials should be loaded from 'credentials.json' file"

    username, password = load_credentials()
    assert username is not None
    assert password is not None
    assert len(username) > 0
    assert len(password) > 0


def test_count_posts():
    "Donbot should be able to count posts in a speakeasy thread if credentials are valid"

    username, password = load_credentials()
    donbot = Donbot(username, password)
    assert (
        donbot.count_posts(single_page_thread)
        == 15
    )


def test_get_user_id():
    "Donbot should be able to get a user's ID"

    username, password = load_credentials()
    donbot = Donbot(username, password)
    assert donbot.get_user_id("Psyche") == "15830"


def test_get_activity_overview():
    "Donbot should be able to get a thread's activity overview"

    username, password = load_credentials()
    donbot = Donbot(username, password)

    activity_overview = donbot.get_activity_overview(
        single_page_thread
    )

    assert len(activity_overview) == 6
    assert activity_overview[0]["user"] == "Ythan"
    assert activity_overview[0]["firstpost"] == "Sun Aug 23, 2020 4:04 pm"
    assert activity_overview[0]["lastpost"] == "Wed Aug 26, 2020 1:21 pm"
    assert int(activity_overview[0]["sincelast"][:4]) >= 1252
    assert activity_overview[0]["totalposts"] == "3"


def test_retrieve_all_posts():
    "Donbot should be able to retrieve all posts in a 1-page thread"

    username, password = load_credentials()
    donbot = Donbot(username, password)

    posts = donbot.get_posts(single_page_thread)
    assert len(posts) == donbot.count_posts(single_page_thread)
    assert posts[0]["user"] == "brighteningskies"
    assert posts[0]["time"] == datetime.strptime(
        "Sat Aug 22, 2020 7:08 pm", "%a %b %d, %Y %I:%M %p")
    assert posts[0]["number"] == 0
    assert "I'll start: it's 1am" in posts[0]["content"]

    assert posts[-1]["user"] == "Ythan"
    assert posts[-1]["time"] == datetime.strptime(
        "Wed Aug 26, 2020 1:21 pm", "%a %b %d, %Y %I:%M %p")
    assert posts[-1]["number"] == 14
    assert "Yul Brynner is cool as fuck." in posts[-1]["content"]