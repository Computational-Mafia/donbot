from typing import Optional
from .operations import login, count_posts, get_user_id, get_activity_overview

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
    postdelay : float, optional
        The delay between posts, in seconds. Default is 3.0.
    """

    def __init__(
        self,
        username: str,
        password: str,
        thread: Optional[str] = None,
        postdelay: float = 3.0,
    ):
        self.postdelay = postdelay
        self.thread = thread or ""
        self.username = username
        self.session = login(username, password)


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