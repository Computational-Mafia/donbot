from lxml import html
import requests
import json
import time
from math import floor
from datetime import datetime as dt

__all__ = [
    "load_credentials",
    "login",
    "count_posts",
    "get_user_id",
    "get_activity_overview",
]


def load_credentials(credentials_path: str = "credentials.json") -> tuple[str, str]:
    "Loads mafiascum credentials from a JSON file"
    with open(credentials_path) as file:
        data = json.load(file)
        username = data.get("username")
        password = data.get("password")
    return username, password


def login(username: str, password: str, post_delay: float = 1.0) -> requests.Session:
    """
    Generates a session object and logs into mafiascum.net.

    Parameters
    ----------
    username : str
        The username of the user.
    password : str
        The password of the user.
    request_delay : float, optional
        The delay between requests, in seconds. Default is 1.0.

    Returns
    -------
    tuple
        The session object and the login result.

    Raises
    ------
    ValueError: If the username or password is incorrect.
    """

    start_url = "https://forum.mafiascum.net/index.php"
    session = requests.Session()
    login_page = session.get(start_url).content
    time.sleep(post_delay)
    creation_time = html.fromstring(login_page).xpath(
        "//input[@name='creation_time']/@value"
    )[0]
    form_token = html.fromstring(login_page).xpath(
        "//input[@name='form_token']/@value"
    )[0]
    form_data = [
        ("username", username),
        ("password", password),
        ("login", "Login"),
        ("redirect", "./index.php?"),
        ("creation_time", creation_time),
        ("form_token", form_token),
    ]

    login_url = "https://forum.mafiascum.net/ucp.php?mode=login"
    session.post(login_url, data=form_data, headers={"Referer": start_url})
    return session


def count_posts(session: requests.Session, thread: str) -> int:
    """
    Counts the number of posts in the specified thread.

    Parameters
    ----------
    session : requests.Session
        The session object used for making HTTP requests.
    thread : str
        The thread to count posts in.

    Returns
    -------
    int
        The number of posts in the specified thread.
    """
    page = session.get(thread).content
    post_count_path = "(//div[@class='pagination'])[2]/text()"
    numberOfPosts = html.fromstring(page).xpath(post_count_path)[0]
    return int(numberOfPosts[: numberOfPosts.find(" ")].strip())


def get_user_id(session: requests.Session, username: str) -> str:
    """
    Retrieve the numeric id that the site uses to identify a user.

    Parameters
    ----------
    session : requests.Session
        The session object used for making HTTP requests.
    username : str
        The username of the user.

    Returns
    -------
    str
        The numeric id that the site uses to identify a user.

    Notes
    -----
    Works by searching for posts made by the user and then extracting the id from first result.
    """
    user_url = "https://forum.mafiascum.net/search.php?keywords=&terms=all&author={}"
    user_link_path = "//dt[@class='author']/a/@href"
    username = username.replace(" ", "+")
    page = session.get(user_url.format(username)).content
    userposts = html.fromstring(page)
    user_link = userposts.xpath(user_link_path)[0]
    return user_link[user_link.rfind("=") + 1 :]


def get_activity_overview(session: requests.Session, thread: str) -> list[dict]:
    """
    Retrieve the activity overview of a thread.

    Parameters
    ----------
    session : requests.Session
        The session object used for making HTTP requests.
    thread : str
        The thread to retrieve the activity overview of.

    Returns
    -------
    list[dict]
        A list of dictionaries containing the activity overview of the thread across users.
    """
    activity_path = "//table/tbody//tr"
    thread_number = thread[thread.rfind("=") + 1 :]
    page = session.get(
        f"https://forum.mafiascum.net/app.php/activity_overview/{thread_number}"
    ).content
    userinfo = []
    for row in html.fromstring(page).xpath(activity_path):
        rowtext = row.xpath(".//text()")
        userinfo.append(
            {
                "user": rowtext[2],
                "firstpost": rowtext[5].strip(),
                "lastpost": rowtext[7].strip(),
                "sincelast": rowtext[9].strip(),
                "totalposts": rowtext[11],
            }
        )
    return userinfo


def get_posts(
    session: requests.Session, thread: str, start: int = 0, end: int = -1
) -> list[dict]:
    """
    Retrieve posts from a thread.

    Parameters
    ----------
    session : requests.Session
        The session object used for making HTTP requests.
    thread : str
        The thread to retrieve the posts of.
    start : int, optional
        The post number to start retrieving from. Default is 0.
    end : int, optional
        The post number to stop retrieving at. Default is infinity.

    Returns
    -------
    list[dict]
        Each post's data, including post `id`, `number`, `user, `time`, and `content`.
    """

    posts_per_page = 25
    post_body_path = "//div[@class='postbody']"
    post_number_path = ".//span[@class='post-number-bolded']//text()"
    post_user_path = ".//a[@class='username' or @class='username-coloured']/text()"
    post_content_path = ".//div[@class='content']"
    post_timestamp_path = ".//p[@class='author modified']/text()"
    post_id_path = ".//a/@href"
    end = end if end != -1 else count_posts(session, thread)

    # identify pages to visit
    start_page_id = floor(start / posts_per_page) * posts_per_page
    end_page_id = floor(end / posts_per_page) * posts_per_page

    # collect on each page key content from posts after current post
    posts = []
    for page_index in range(start_page_id, (end_page_id + 1), posts_per_page):
        page = session.get(f"{thread}&start={str(page_index)}").content
        for raw_post in html.fromstring(page).xpath(post_body_path):
            post_number = int(raw_post.xpath(post_number_path)[0][1:])
            if post_number < start or post_number > end:
                continue
            posts.append({"number": post_number})
            posts[-1]["id"] = raw_post.xpath(post_id_path)[0]
            posts[-1]["id"] = posts[-1]["id"][posts[-1]["id"].rfind("#") + 2 :]
            posts[-1]["user"] = raw_post.xpath(post_user_path)[0]
            posts[-1]["content"] = raw_post.xpath(post_content_path)[0]
            posts[-1]["content"] = html.tostring(raw_post.xpath(post_content_path)[0])
            posts[-1]["content"] = posts[-1]["content"].decode("UTF-8").strip()[21:-6]
            posts[-1]["time"] = raw_post.xpath(post_timestamp_path)[-1]
            posts[-1]["time"] = posts[-1]["time"][
                posts[-1]["time"].find("» ") + 2 :
            ].strip()
            posts[-1]["time"] = dt.strptime(posts[-1]["time"], "%a %b %d, %Y %I:%M %p")

    return posts


def get_post(session: requests.Session, thread: str, post_number: int) -> dict:
    """
    Retrieve a single post from a thread.

    Parameters
    ----------
    session : requests.Session
        The session object used for making HTTP requests.
    thread : str
        The thread to retrieve the post from.
    post_number : int
        The number of the post to retrieve.

    Returns
    -------
    dict
        The post's data, including `id`, `number`, `user, `time`, and `content`.
    """
    posts = get_posts(session, thread, post_number, post_number + 1)
    return posts[0]


def make_post(
    session: requests.Session, thread: str, content: str, post_delay: float = 1.0
):
    """
    Make a post in a thread.

    Parameters
    ----------
    session : requests.Session
        The session object used for making HTTP requests.
    thread : str
        The thread to retrieve the posts of.
    content : str
        The content of the post to make.
    post_delay : float, optional
        The delay between requests, in seconds. Default is 1.0.
    """
    post_url = "https://forum.mafiascum.net/posting.php?mode=reply&t={}"
    post_form_path = "//input[@name='{}']/@value"

    # one request to get form info for post
    thread_id = thread[thread.find("t=") + 2 :]
    post_url = post_url.format(thread_id)
    page = html.fromstring(session.get(post_url).content)

    # and another to make it
    post_data = {
        "message": content,
        "post": "Submit",
        "addbbcode20": 100,
    }
    for name in ["topic_cur_post_id", "creation_time", "form_token"]:
        post_data[name] = page.xpath(post_form_path.format(name))[0]
    time.sleep(post_delay)
    session.post(post_url, data=post_data)


def edit_post(
    session: requests.Session,
    thread: str,
    post_number: int,
    content: str,
    post_delay: float = 1.0,
):
    """
    Edit a post in a thread.

    Parameters
    ----------
    session : requests.Session
        The session object used for making HTTP requests.
    thread : str
        The thread to retrieve the posts of.
    post_number : int
        The number of the post to edit.
    content : str
        The content of the post to make.
    post_delay : float, optional
        The delay between requests, in seconds. Default is 1.0.
    """

    # one request to get post id
    post_id = get_post(session, thread, post_number)["id"]
    edit_url = f"https://forum.mafiascum.net/posting.php?mode=edit&p={post_id}"

    # and another to get form info for edit
    page = html.fromstring(session.get(edit_url).content)

    # and another to make it
    post_data = {
        "message": content,
        "post": "Submit",
        "addbbcode20": 100,
    }
    for name in [
        "edit_post_message_checksum",
        "edit_post_subject_checksum",
        "creation_time",
        "form_token",
    ]:
        post_data[name] = page.xpath(f"//input[@name='{name}']/@value")[0]

    time.sleep(post_delay)
    session.post(edit_url, data=post_data)
