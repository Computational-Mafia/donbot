from typing import Optional
from .operations import (
    login,
    count_posts,
    get_user_id,
    get_activity_overview,
    get_posts,
    get_post,
    make_post,
    edit_post,
)

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
        Delay after POST requests (3 seconds by default). Required to prevent rate limiting.
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
        self.session = login(username, password, post_delay)

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
        return count_posts(self.session, thread)

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
        return get_user_id(self.session, username)

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
        return get_activity_overview(self.session, thread)

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
        return get_posts(self.session, thread, start, end)

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
        return get_post(self.session, thread, post_number)

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
        make_post(self.session, thread, content, post_delay)

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
        edit_post(self.session, thread, post_number, content, post_delay)
