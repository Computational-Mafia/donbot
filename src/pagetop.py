from donbot import Donbot
from math import ceil
import schedule
import time


class PageTopper(Donbot):
    """A utility designed for periodically (or on command) pagetopping a thread if it can be pagetopped."""

    def __init__(self, username, password, thread=None, content="Pagetop!", current_page=1, frequency=60):
        super().__init__(username, password, thread)

        # most recent page that has started
        # can be left to default value if unknown as will be updated upon next check
        self.current_page = current_page

        # polling rate
        self.frequency = frequency

    def pagetop(self):
        """Check the current number of posts.
        Then figure out what page the NEXT post would be on.
        If it's on a different page, pagetop.
        """
        print('pagetop called')
        current_number_of_posts = self.number_of_posts()
        page_of_next_post =  ceil((current_number_of_posts + 1) / 25)
        print(self.current_page)
        print(page_of_next_post)

        if page_of_next_post > self.current_page:
            self.make_post(content)
            self.current_page = page_of_next_post

    def run(self):
        schedule.every(self.frequency).seconds.do(self.pagetop)

        while True:
            schedule.run_pending()
            time.sleep(1)