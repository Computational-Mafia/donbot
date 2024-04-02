thread = "https://forum.mafiascum.net/viewtopic.php?t=92345"  # @param {type:"string"}
target_user_post_number = 21  # @param {type:"integer"}
description_path = '//span[@class="bbvote"]' # @param {type:"string"}

import requests
from lxml import html
from lxml.html import HtmlElement
from math import floor


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
    post_count_path = "//div[@class='pagination']/text()"
    post_count_element = next(
        el for el in thread_html.xpath(post_count_path) if el.strip()
    )
    return int("".join([c for c in post_count_element if c.isdigit()]))


def get_thread_page_urls(
    thread: str, thread_page_html: HtmlElement, start: int = 0, end: int = -1
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
    thread_page_html: HtmlElement, start: int = 0, end: int | float = -1
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
    end = end if end != -1 else float("inf")
    for raw_post in thread_page_html.xpath("//div[@class='postbody']"):
        post = get_post(raw_post)
        if post["number"] >= start and post["number"] <= end:
            posts.append(post)
    return posts


if __name__ == "__main__":

    session = requests.Session()
    thread_page_html = html.fromstring(session.get(thread).content)

    # get id of user at target_user_post_number
    user_post_url = get_thread_page_urls(
        thread, thread_page_html, target_user_post_number, target_user_post_number
    )[0]
    user_post_html = html.fromstring(session.get(user_post_url).content)
    user_id = get_posts(
        user_post_html, target_user_post_number, target_user_post_number
    )[0]["user_id"]

    # get opening page html of user iso
    user_iso_url = f"{thread}&ppp=25&user_select%5B%5D={user_id}"
    base_html = html.fromstring(session.get(user_iso_url).content)

    # get all posts by user
    posts = []
    for thread_page_url in get_thread_page_urls(user_iso_url, base_html, 0, -1):
        thread_page_html = html.fromstring(session.get(thread_page_url).content)
        posts += get_posts(thread_page_html)

    # filter out posts when post["content"] does not contain query_path element
    posts = [post for post in posts if html.fromstring(post["content"]).xpath(description_path)]

    # generate labels for each post based on text inside query_path element
    lines = []
    for post in posts:
        label = html.fromstring(post["content"]).xpath(description_path)[0].text_content()
        post_url = f"https://forum.mafiascum.net/viewtopic.php?p={post['id']}#p{post['id']}"
        lines.append(f'[url={post_url}]{label}[/url]')

    print("\n".join(lines))
