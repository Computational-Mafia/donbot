from email.mime import base
from typing import Optional
from .operations import (
    get_login_form,
    count_posts,
    get_user_id,
    get_activity_overview,
    get_posts,
    get_make_post_form,
    get_edit_post_form,
    get_send_pm_form,
    get_thread_page_urls,
)
from lxml import html
from requests import Session
import time

__all__ = ["Donbot"]


class Donbot:
    """
    Represents a Donbot instance.

    Parameters
    ----------
    username : str
        The username associated with the Donbot instance.
    password : str
        The password associated with the Donbot instance.
    thread : str, optional
        The thread associated with the Donbot instance, if specified.
    post_delay : float, optional
        Delay of request before POST request (seconds). Required to prevent rate limiting.
    """

    def __init__(
        self,
        username: str,
        password: str,
        thread: Optional[str] = None,
        post_delay: float = 3.0,
    ):
        self.postdelay = post_delay
        self.thread = thread or ""
        self.username = username
        self.session = Session()
        self.login(username, password, post_delay)

    def login(self, username: str, password: str, post_delay: float):
        """
        Authenticates the Donbot instance with the specified username and password.

        Parameters
        ----------
        username : str
            The username to authenticate with.
        password : str
            The password to authenticate with.
        post_delay : float
            Delay of request before POST request (seconds). Required to prevent rate limiting.
        """
        start_url = "https://forum.mafiascum.net/index.php"
        login_url = "https://forum.mafiascum.net/ucp.php?mode=login"
        login_page_html = html.fromstring(self.session.get(start_url).content)
        time.sleep(post_delay)
        login_form = get_login_form(login_page_html, username, password)
        self.session.post(login_url, data=login_form, headers={"Referer": start_url})

    def count_posts(self, thread: Optional[str] = None) -> int:
        """
        Counts the number of posts in the specified thread.

        Parameters
        ----------
        thread : str, optional
            The thread to count posts in.

        Returns
        -------
        int
            The number of posts in the specified thread.
        """
        thread = thread or self.thread
        if len(thread) == 0:
            raise ValueError("No thread specified!")
        thread_html = html.fromstring(self.session.get(thread).content)
        return count_posts(thread_html)

    def get_user_id(self, username: Optional[str]) -> str:
        """
        Gets the user ID of the specified username.

        Parameters
        ----------
        username : str, optional
            The username to get the ID of.

        Returns
        -------
        str
            The user ID of the specified username.
        """
        username = username or self.username
        if len(username) == 0:
            raise ValueError("No username specified!")

        username = username.replace(" ", "+")
        user_url = f"https://forum.mafiascum.net/search.php?keywords=&terms=all&author={username}"
        user_posts_html = html.fromstring(self.session.get(user_url).content)
        return get_user_id(user_posts_html)

    def get_activity_overview(self, thread: Optional[str] = None) -> list:
        """
        Gets the activity overview of the specified thread.

        Parameters
        ----------
        thread : str, optional
            The thread to get the activity overview of.

        Returns
        -------
        list
            The activity overview of the specified thread.
        """
        thread = thread or self.thread
        if len(thread) == 0:
            raise ValueError("No thread specified!")
        thread_number = thread[thread.rfind("=") + 1 :]
        activity_overview_html = html.fromstring(
            self.session.get(
                f"https://forum.mafiascum.net/app.php/activity_overview/{thread_number}"
            ).content
        )
        return get_activity_overview(activity_overview_html)

    def get_posts(
        self, thread: Optional[str] = None, start: int = 0, end: int = -1
    ) -> list[dict]:
        """
        Gets the posts in the specified thread.

        Parameters
        ----------
        thread : str, optional
            The thread to get posts from.
        start : int, optional
            The starting post number.
        end : int, optional
            The ending post number.

        Returns
        -------
        list
            The posts in the specified thread.
        """
        thread = thread or self.thread
        if len(thread) == 0:
            raise ValueError("No thread specified!")
        base_html = html.fromstring(self.session.get(thread).content)

        posts = []
        for thread_page_url in get_thread_page_urls(thread, base_html, start, end):
            thread_page_html = html.fromstring(
                self.session.get(thread_page_url).content
            )
            posts += get_posts(thread_page_html, start, end)

        return posts
    
    def get_user_posts(
            self, thread: Optional[str] = None, user: Optional[str] = None
    ):
        """
        Gets the posts of the specified user in the specified thread.

        Parameters
        ----------
        thread : str, optional
            The thread to get posts from.
        user : str, optional
            The user to get posts from.

        Returns
        -------
        list
            The posts of the specified user in the specified thread.
        """
        thread = thread or self.thread
        user = user or self.username
        if len(thread) == 0:
            raise ValueError("No thread specified!")
        user_id = self.get_user_id(user)
        user_iso_url = f"{thread}&user_select%5B%5D={user_id}"
        base_html = html.fromstring(self.session.get(user_iso_url).content)

        posts = []
        for user_iso_page_url in get_thread_page_urls(user_iso_url, base_html, 0, -1):
            user_iso_page_html = html.fromstring(
                self.session.get(user_iso_page_url).content
            )
            posts += get_posts(user_iso_page_html)

    def get_post(self, post_number: int = 0, thread: Optional[str] = None) -> dict:
        """
        Gets a post in the specified thread.

        Parameters
        ----------
        post_number : int, optional
            The post number to get.
        thread : str, optional
            The thread to get the post from.

        Returns
        -------
        dict
            The post in the specified thread.
        """
        thread = thread or self.thread
        if len(thread) == 0:
            raise ValueError("No thread specified!")
        return self.get_posts(thread, post_number, post_number + 1)[0]

    def make_post(
        self,
        content: str = ".",
        thread: Optional[str] = None,
        post_delay: Optional[float] = None,
    ):
        """
        Makes a post in the specified thread.

        Parameters
        ----------
        thread : str, optional
            The thread to make a post in.
        content : str
            The content of the post.
        post_delay : float, optional
            Delay after POST requests (3 seconds by default). Required to prevent rate limiting.
        """
        thread = thread or self.thread
        post_delay = post_delay or self.postdelay
        if len(thread) == 0:
            raise ValueError("No thread specified!")

        thread_id = thread[thread.find("t=") + 2 :]
        make_post_url = (
            f"https://forum.mafiascum.net/posting.php?mode=reply&t={thread_id}"
        )
        make_post_page_html = html.fromstring(self.session.get(make_post_url).content)
        make_post_form = get_make_post_form(make_post_page_html, content)
        time.sleep(post_delay)
        self.session.post(make_post_url, data=make_post_form)

    def edit_post(
        self,
        post_number: int,
        content: str,
        thread: Optional[str] = None,
        post_delay: Optional[float] = None,
    ):
        """
        Edits a post in the specified thread.

        Parameters
        ----------
        post_number : int
            The post number to edit.
        content : str
            The content of the post.
        thread : str, optional
            The thread to edit a post in.
        post_delay : float, optional
            Delay after POST requests (3 seconds by default). Required to prevent rate limiting.
        """
        thread = thread or self.thread
        post_delay = post_delay or self.postdelay
        if len(thread) == 0:
            raise ValueError("No thread specified!")

        post_id = self.get_post(post_number, thread)["id"]
        edit_post_url = f"https://forum.mafiascum.net/posting.php?mode=edit&p={post_id}"
        edit_post_page_html = html.fromstring(self.session.get(edit_post_url).content)
        edit_post_form = get_edit_post_form(edit_post_page_html, content)
        time.sleep(post_delay)
        self.session.post(edit_post_url, data=edit_post_form)

    def send_pm(
        self,
        recipients: str | list[str],
        subject: str = "Re: ",
        content: str = ".",
        post_delay: Optional[float] = None,
    ):
        """
        Sends a private message to the specified recipient.

        Parameters
        ----------
        recipient : str | list[str]
            The recipient(s) of the private message.
        subject : str
            The subject of the private message. Defaults to "Re: ".
        content : str
            The content of the private message. Defaults to a period.
        post_delay : float
            Delay after POST requests (3 seconds by default). Required to prevent rate limiting.
        """
        post_delay = post_delay or self.postdelay
        recipients = recipients if isinstance(recipients, list) else [recipients]
        recipient_uids = [self.get_user_id(recipient) for recipient in recipients]
        pm_url = "https://forum.mafiascum.net/ucp.php?i=pm&mode=compose"
        pm_page_html = html.fromstring(self.session.get(pm_url).content)
        send_pm_form = get_send_pm_form(pm_page_html, recipient_uids, content, subject)
        time.sleep(post_delay)
        self.session.post(pm_url, data=send_pm_form)
