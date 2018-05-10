from donbot import Donbot
from lxml import html, cssselect

class GetVotes(Donbot):
    def __init__(self, username, password, thread=None, postdelay=1.5):
        super(GetVotes, self).__init__(username, password, thread)


    def getISOs(self, usernames):
        uids = [super(GetVotes, self).getUserID(user) for user in usernames]

        for i, uid in enumerate(uids):
            link = self.thread + "&user_select[]=" + uid + "&sort=Go&st=0&sk=t&sd=d"
            page = self.session.get(link)
            content = html.fromstring(page.content)
            vote = content.cssselect(".postbody .bbvote")[0].text_content()
            print usernames[i] + '\t' + vote