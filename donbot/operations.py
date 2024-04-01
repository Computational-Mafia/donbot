from lxml import html
from lxml.html import HtmlElement
from math import floor
import json


__all__ = [
    "load_credentials",
    "get_login_form",
    "count_posts",
    "get_thread_page_urls",
    "get_user_id",
    "get_activity_overview",
    "get_posts",
    "get_make_post_form",
    "get_edit_post_form",
]


def load_credentials(credentials_path: str = "credentials.json") -> tuple[str, str]:
    """
    Loads mafiascum credentials from a JSON file.

    Parameters
    ----------
    credentials_path : str, optional
        The path to the JSON file containing the credentials.
        Defaults to "credentials.json" if not provided.

    Returns
    -------
    tuple[str, str]
        A tuple containing the username and password loaded from the JSON file.
    """
    with open(credentials_path) as file:
        data = json.load(file)
        username = data.get("username")
        password = data.get("password")
    return username, password


def get_login_form(
    login_page_html: HtmlElement, username: str, password: str
) -> dict[str, str]:
    """
    Extracts the login form data from the login page HTML

    Parameters
    ----------
    login_page_html : HtmlElement
        The HTML of the login page.
    username : str
        The username of the user.
    password : str
        The password of the user.

    Returns
    -------
    dict
        The login form data; if passed in a valid POST request, will log the user in.
    """
    creation_time = login_page_html.xpath("//input[@name='creation_time']/@value")[0]
    form_token = login_page_html.xpath("//input[@name='form_token']/@value")[0]
    return {
        "username": username,
        "password": password,
        "login": "Login",
        "redirect": "./index.php?",
        "creation_time": creation_time,
        "form_token": form_token,
    }


def count_posts(thread_html: HtmlElement) -> int:
    """
    Counts the number of posts in the specified thread.

    Parameters
    ----------
    thread_html : HtmlElement
        The HTML of a page from the thread to count posts in.

    Returns
    -------
    int
        The number of posts in the specified thread.
    """
    post_count_path = "(//div[@class='pagination'])/text()"
    numberOfPosts = thread_html.xpath(post_count_path)[0]
    return int(numberOfPosts[: numberOfPosts.find(" ")].strip())


def get_thread_page_urls(
    thread: str, thread_page_html: HtmlElement, start: int, end: int
) -> list[str]:
    """
    Get the URLs of the pages of a thread.

    Parameters
    ----------
    thread : str
        The URL of the thread.
    thread_page_html : HtmlElement
        The HTML of a page from the thread.
    end : int
        The number of pages to retrieve.

    Returns
    -------
    list[str]
        The URLs of the pages of the thread.
    """
    end = end if end != -1 else count_posts(thread_page_html)

    posts_per_page = 25
    start_page_id = floor(start / posts_per_page) * posts_per_page
    end_page_id = floor(end / posts_per_page) * posts_per_page
    
    return [
        f"{thread}&start={str(page_id)}"
        for page_id in range(start_page_id, end_page_id + 1, posts_per_page)
    ]


def get_user_id(user_posts_html: HtmlElement) -> str:
    """
    Retrieve the numeric id that the site uses to identify a user.

    Parameters
    ----------
    user_posts_html : HtmlElement
        The HTML of a page containing search results for a user's posts.

    Returns
    -------
    str
        The numeric id that the site uses to identify a user.

    Notes
    -----
    Works by extracting the id from first result.
    """
    user_link_path = "//dt[@class='author']/a/@href"
    user_link = user_posts_html.xpath(user_link_path)[0]
    return user_link[user_link.rfind("=") + 1 :]


def get_activity_overview(activity_overview_html: HtmlElement) -> list[dict]:
    """
    Retrieve the activity overview of a thread.

    Parameters
    ----------
    activity_overview_html : HtmlElement
        The HTML of a page containing the activity overview of a thread.

    Returns
    -------
    list[dict]
        A list of dictionaries containing the activity overview of the thread across users.
    """
    activity_path = "//table/tbody//tr"
    userinfo = []
    for row in activity_overview_html.xpath(activity_path):
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


def get_post(post_html: HtmlElement) -> dict:  # sourcery skip: merge-dict-assign
    """
    Extracts the data of a post from the post HTML.

    Parameters
    ----------
    post_html : HtmlElement
        The HTML of a post.

    Returns
    -------
    dict
        The post's data, including post `id`, `number`, `user, `time`, and `content`.
    """
    post_number_path = ".//span[@class='post-number-bolded']//text()"
    post_user_path = ".//a[@class='username' or @class='username-coloured']/text()"
    post_user_id_path = ".//a[@class='username' or @class='username-coloured']/@href"
    post_content_path = ".//div[@class='content']"
    post_timestamp_path = ".//p[@class='author modified']/text()"
    post_id_path = ".//a/@href"

    post = {}
    post["number"] = int(post_html.xpath(post_number_path)[0][1:])
    post["id"] = post_html.xpath(post_id_path)[0]
    post["id"] = post["id"][post["id"].rfind("#") + 2 :]
    post["user"] = post_html.xpath(post_user_path)[0]
    post["user_id"] = post_html.xpath(post_user_id_path)[0]
    post["user_id"] = post["user_id"][post["user_id"].rfind("=") + 1 :]
    post["content"] = html.tostring(post_html.xpath(post_content_path)[0])
    post["content"] = post["content"].decode("UTF-8").strip()[21:-6]
    post["time"] = post_html.xpath(post_timestamp_path)[-1]
    post["time"] = post["time"][post["time"].find("» ") + 2 :].strip()
    return post


def get_posts(
    thread_page_html: HtmlElement, start: int = 0, end: int|float = -1
) -> list[dict]:
    """
    Retrieve posts from a thread.

    Parameters
    ----------
    thread_page_html : HtmlElement
        The HTML of a page from the thread to retrieve posts from.
    start : int
        Lowest post number to retrieve.
    end : int, optional
        Highest post number to retrieve.

    Returns
    -------
    list[dict]
        Each post's data, including post `id`, `number`, `user, `time`, and `content`.
    """
    posts = []
    end = end if end != -1 else float('inf')
    for raw_post in thread_page_html.xpath("//div[@class='postbody']"):
        post = get_post(raw_post)
        if post["number"] >= start and post["number"] <= end:
            posts.append(post)
    return posts


def get_make_post_form(
    make_post_page_html: HtmlElement, post_content: str
) -> dict[str, str]:
    """
    Extracts the form data for making a post from the make post page HTML.

    Parameters
    ----------
    make_post_page_html : HtmlElement
        The HTML of the make post page.
    post_content : str
        The content of the post to make.

    Returns
    -------
    dict
        The form data for making a post; if passed in a valid POST request, will make the post.
    """
    post_form_path = "//input[@name='{}']/@value"

    post_data = {
        "message": post_content,
        "post": "Submit",
        "addbbcode20": 100,
    }
    for name in ["topic_cur_post_id", "creation_time", "form_token"]:
        post_data[name] = make_post_page_html.xpath(post_form_path.format(name))[0]
    return post_data


def get_edit_post_form(
    edit_post_page_html: HtmlElement, post_content: str
) -> dict[str, str]:
    """
    Extracts the form data for editing a post from the edit post page HTML.

    Parameters
    ----------
    edit_post_page_html : HtmlElement
        The HTML of the edit post page.
    post_content : str
        The content of the post to make.

    Returns
    -------
    dict
        The form data for editing a post; if passed in a valid POST request, will edit the post.
    """
    post_data = {
        "message": post_content,
        "post": "Submit",
        "addbbcode20": 100,
    }
    for name in [
        "edit_post_message_checksum",
        "edit_post_subject_checksum",
        "creation_time",
        "form_token",
    ]:
        post_data[name] = edit_post_page_html.xpath(f"//input[@name='{name}']/@value")[
            0
        ]
    return post_data


def get_send_pm_form(
    send_pm_page_html: HtmlElement,
    recipient_uids: list[str],
    content: str,
    subject: str,
) -> dict[str, str]:
    """
    Extracts the form data for sending a private message from the send pm page HTML.

    Parameters
    ----------
    send_pm_page_html : HtmlElement
        The HTML of the send pm page.
    recipient_uids : list[str]
        User ids for recipient(s) of the private message.
    content : str
        The content of the private message.
    subject : str
        The subject of the private message.

    Returns
    -------
    dict
        The form data for sending a private message; if passed in a valid POST request, will send the private message.
    """

    post_data = {
        "username_list": "",
        "message": content,
        "post": "Submit",
        "icon": 0,
        "subject": subject,
        "addbbcode20": 100,
        "status_switch": 0,
        "disable_smilies": "on",
        "attach_sig": "on",
    }
    for user in recipient_uids:
        post_data[f"address_list[u][{user}]"] = "to"
    for name in ["creation_time", "form_token"]:
        post_data[name] = send_pm_page_html.xpath(f"//input[@name='{name}']/@value")[0]
    return post_data
