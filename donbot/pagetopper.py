from donbot import Donbot
from math import ceil
import schedule
import time

content = """ beep boop \n 
This space is reserved for a vote count! \n 
This post was made by a bot. Check [url=https://forum.mafiascum.net/viewtopic.php?f=5&t=76109]here[/url] for more info. \n
beep boop
"""

class PageTopper(Donbot):
    def __init__(self, username, password, thread=None, currPage=1, frequency=60):
        super().__init__(username, password, thread)
        self.frequency = frequency  # polling rate
        self.currPage = currPage    # most recent page that was page topped
        self.postPerPage = 25


    def pagetop(self):
        # get the current number of posts
        # figure out what page the NEXT post would be on
        # if it's on a different page, reserve the post

        print('pagetop called')
        currPosts = self.getNumberOfPosts()
        pageOfNextPost =  ceil((currPosts + 1) / 25)
        print(self.currPage)
        print(pageOfNextPost)

        if pageOfNextPost > self.currPage:
            self.makePost(content)
            self.currPage = pageOfNextPost


    def run(self):
        schedule.every(self.frequency).seconds.do(self.pagetop)

        while True:
            schedule.run_pending()
            time.sleep(1)