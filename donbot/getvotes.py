import gevent                  # async/concurrency
from gevent import monkey

# patches stdlib to cooperate w/ other greenlets
monkey.patch_all()

from donbot import Donbot
from lxml import html, cssselect

class GetVotes(Donbot):
    def __init__(self, username, password, thread=None, postdelay=1.5, start=1):
        super(GetVotes, self).__init__(username, password, thread)
        self.start = start


    def getPostNumberFromVote(self, vote):
        for parent in vote.iterancestors():
            if parent.get('class') is not None and "postbody" in parent.get('class'):
                return int(parent.cssselect(".author a")[1].text_content()[1:])

        raise Exception('failed to get post number')

    def getVotes(self, usernames):
        results = []
        uids = [gevent.spawn(self.getUserID, user) for user in usernames]
        gevent.wait(uids)

        for i, uid in enumerate(uids):
            link = self.thread + "&user_select[]=" + uid.value + "&sort=Go&st=0&sk=t&sd=d"
            page = self.session.get(link)
            content = html.fromstring(page.content)

            # remove quotes and spoilers
            for quote in content.cssselect(".postbody blockquote"): quote.drop_tree() 
            for spoiler in content.cssselect(".quotetitle,.quotecontent"): spoiler.drop_tree() 

            votes = content.cssselect(".postbody .bbvote")

            # no votes cast yet at all
            if len(votes) == 0:
                continue

            # get the post number of the most recent vote
            currVote = votes[0]
            currPn = self.getPostNumberFromVote(currVote)

            # no votes yet in the current game day
            if currPn < self.start:
                continue

            # handle multiple votes in a single post
            for vote in votes:
                pn = self.getPostNumberFromVote(vote)
                if pn != currPn:
                    break
                currVote = vote

            results.append(str(currPn) + ' ' + usernames[i] + ' ' + currVote.text_content())

        return results
