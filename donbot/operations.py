from lxml import html
import requests
import json
import time

__all__ = ["load_credentials", "login", "count_posts", "get_user_id", "get_activity_overview"]


def load_credentials(credentials_path: str = "credentials.json") -> tuple[str, str]:
    "Loads mafiascum credentials from a JSON file"
    with open(credentials_path) as file:
        data = json.load(file)
        username = data.get("username")
        password = data.get("password")
    return username, password


def login(username: str, password: str, request_delay: float = 1) -> requests.Session:
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
    time.sleep(request_delay)
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
    session.cookies.values()
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
