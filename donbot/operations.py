from lxml import html
from lxml.html import HtmlElement
from math import floor
from dataclasses import dataclass, asdict
import json


__all__ = [
    "load_credentials",
    "make_login_form",
    "count_posts",
    "get_thread_page_urls",
    "get_user_id",
    "get_activity_overview",
    "get_posts",
    "make_submit_post_form",
    "get_edit_post_form",
]

@dataclass
class Post:
    """Dataclass representing a post on the MafiaScum forum.

    Attributes:
        number: The post number based on its index within the thread.
        id: The unique id associated by the forum with the post.
        user: The name of the user who made the post.
        user_id: The id number associated by the forum with the user.
        content: The content of the post (html string)
        time: The time the post was made (unparsed string)
        page: The url of the page of the thread containing the post.
        forum: The id of the forum the post was made in.
        thread: The url of the thread the post was made in.
    """
    number: int
    id: str
    user: str
    user_id: str
    content: str
    time: str
    page: str
    forum: str
    thread: str

    def to_dict(self):
        """Returns the post as a dictionary.
        """
        return asdict(self)


def load_credentials(credentials_path: str = "credentials.json") -> tuple[str, str]:
    """
    Returns the username and password at the specified JSON filepath.

    Args:
        credentials_path:
            Path to the JSON file containing the credentials; defaults to "credentials.json"
    """
    with open(credentials_path) as file:
        data = json.load(file)
        username = data.get("username")
        password = data.get("password")
    return username, password


def make_login_form(
    login_page_html: HtmlElement, username: str, password: str
) -> dict[str, str]:
    """Returns a valid form for a POST request to log in the user.

    Args:
        login_page_html: HTML of the login page.
        username: username of the user.
        password: password of the user.
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


def get_user_id(user_posts_html: HtmlElement) -> str:
    """Returns the numeric id that the site uses to identify a user.

    Works by extracting the id from the first result of a search for the user's posts.

    Args:
        user_posts_html: HTML of a page containing search results for a user's posts.
    -----
    
    """
    user_link_path = "//dt[@class='author']/a/@href"
    user_link = user_posts_html.xpath(user_link_path)[0]
    return user_link[user_link.rfind("=") + 1 :]


def get_activity_overview(activity_overview_html: HtmlElement) -> list[dict]:
    """Returns the activity overview of a thread across users.

    Args:
        activity_overview_html: The HTML of a page containing the activity overview of a thread.
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


def count_posts(thread_html: HtmlElement) -> int:
    """Returns the number of posts in a specified thread.

    Args:
        thread_html: HTML of a page from the thread to count posts in.
    """
    post_count_path = "//div[@class='pagination']/text()"
    post_count_element = next(
        el for el in thread_html.xpath(post_count_path) if el.strip()
    )
    return int("".join([c for c in post_count_element if c.isdigit()]))


def get_thread_page_urls(
    thread: str, thread_page_html: HtmlElement, start: int = 0, end: int = -1
) -> list[str]:
    """Returns the URLs of the pages of a thread.

    Args:
        thread: URL of the thread.
        thread_page_html: HTML of a page from the thread.
        end: number of pages to retrieve.
    """
    end = end if end != -1 else count_posts(thread_page_html)

    posts_per_page = 25
    start_page_id = floor(start / posts_per_page) * posts_per_page
    end_page_id = floor(end / posts_per_page) * posts_per_page

    return [
        f"{thread}&start={str(page_id)}"
        for page_id in range(start_page_id, end_page_id + 1, posts_per_page)
    ]


def get_post(post_html: HtmlElement, page_url: str = '') -> Post:  # sourcery skip: merge-dict-assign
    """Returns the data of a post from the post HTML.

    Args:
        post_html: The HTML of a post.
        page_url: The URL of the page containing the post.
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
    post["page"] = page_url
    post["forum"] = page_url[page_url.find("f=") + 2 : page_url.find("&t=")]
    post["thread"] = page_url[page_url.find("&t=") + 3 : page_url.find("&start")]
    return Post(**post)


def get_posts(
    thread_page_html: HtmlElement, start: int = 0, end: int | float = -1, page_url: str = ''
) -> list[Post]:
    """
    Returns a sequence of posts from a thread.

    Args:
        thread_page_html: HTML of a page from the thread to retrieve posts from.
        page_url: URL of the page containing the posts.
        start: Lowest post number to retrieve.
        end: Highest post number to retrieve.
    """
    posts = []
    end = end if end != -1 else float("inf")
    for raw_post in thread_page_html.xpath("//div[@class='postbody']"):
        post = get_post(raw_post, page_url)
        if post.number >= start and post.number <= end:
            posts.append(post)
    return posts


def make_submit_post_form(
    make_post_page_html: HtmlElement, post_content: str
) -> dict[str, str]:
    """Returns a valid form for a POST request to submit a new post to a thread.

    Args:
        make_post_page_html: HTML of the post submission page.
        post_content: The content of the post.
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
    """Returns a valid form for a POST request to edit a post.
    
    Args:
        edit_post_page_html: HTML of the edit post page.
        post_content: The content of the post.
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
    """Returns a valid form for a POST request to send a private message.

    Args:
        send_pm_page_html: HTML of the send private message page.
        recipient_uids: The user ids of the recipients.
        content: The content of the private message.
        subject: The subject of the private message.
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
