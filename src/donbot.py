from datetime import datetime as dt  # to parse timestamps
from math import floor  # to get page# from post
import requests  # for interacting with website
import time  # need delays before post requests
from lxml import html  # for parsing website content


class Donbot:
    """
    a collection of functions automating simple operations on mafiascum.net

    Donbot utilities are based on the Donbot class and are aimed at simplifying utility development and customization.
    It wraps a variety of powerful functions automating simple forum operations that can be flexibly sequenced to perform
    a wide variety of activities. Creating an instance of the Donbot class with specified credentials associates it with
    a particular user account; from there specified class operations can be performed in the user's name, leveraging their
    permissions.

    Please don't use these functions haphazardly, especially those that make posts or send PMs, as misuse thereof can be
    against Site Rules, get you banned, and most importantly cause trouble for a lot of decent people.

    Attributes:
        post_delay: seconds donbot will wait before making new POST requests
        thread: default thread that donbot will perform operations on
        username: username credential for current donbot
        session: authenticated session that donbot interacts with site through
    """

    "Urls that donbot will construct requests with"
    # generic site url; will start other urls
    site_url = 'https://forum.mafiascum.net/'

    # where bot logs into mafiascum.net
    login_url = site_url + 'ucp.php?mode=login'

    # format w/ username and get to obtain page w/ their userid on it
    user_url = site_url + 'search.php?keywords=&terms=all&author={}'

    # make post request here w/ right format to make a post to thread
    post_url = site_url + 'posting.php?mode=reply&{}'

    # post request here w/ form to send a pm
    pm_url = site_url + 'ucp.php?i=pm&mode=compose'

    "Xpaths to elements that Donbot will grab info from"""
    # number of posts in thread associated w/ page
    post_count_path = "//div[@class='pagination']/text()"
    post_count_path = "(//div[@class='pagination'])[2]/text()"

    # every post on current page
    posts_path = '//div[@class="post bg2" or @class="post bg1"]'

    # post# of a post
    number_path = ".//p[@class='author']/a/strong/text()"

    # username associated w/ a post
    user_path = ".//dl[@class='postprofile']/dt/a/text()"

    # content of a post
    content_path = ".//div[@class='content']"

    # timestamp of a post
    date_time_path = ".//p[@class='author']/text()"

    # path to value of all input elements on page with specified name
    post_form_path = "//input[@name='{}']/@value"

    # at user_url, path to link that has their userid
    user_link_path = "//dt[@class='author']/a/@href"

    # at activity overview page, path to cells of page's main table
    activity_path = "//table//table//div"

    "Other static variables that Donbot uses across instances"
    posts_per_page = 25  # number of posts per thread page
    post_stamp = '%a %b %d, %Y %I:%M %p'  # post timestamp structure

    def __init__(self, username, password, thread=None, post_delay=3.0):
        """Initializes Donbot using specified username and password as credentials and optionally constraining
        which thread can be operated on and a minimum delay between successive POST requests within a function.
        """
        self.post_delay = post_delay  # seconds to wait before post requests
        self.thread = thread
        self.username = username
        self.session = requests.Session()
        login_result = self.session.post(
            Donbot.login_url,
            {'username': username, 'password': password, 'redirect': 'index.php', 'login': 'Login'})

        # raise error if username or password is invalid
        if 'You have specified an incorrect password.' in login_result.text:
            raise ValueError('You have specified an incorrect password.')
        elif 'You have specified an incorrect username.' in login_result.text:
            raise ValueError('You have specified an incorrect username.')

    def user_id(self, username=None):
        """Search for posts by a specified user; the extracted userID is in the link in the first result."""
        username = username if username else self.username
        username = username.replace(' ', '+')
        page = self.session.get(Donbot.user_url.format(username)).content
        user_posts = html.fromstring(page)
        user_link = user_posts.xpath(Donbot.user_link_path)[0]
        return user_link[user_link.rfind('=')+1:]

    def number_of_posts(self, thread=None):
        """Count the number of posts in a thread."""
        thread = thread if thread else self.thread
        if len(thread) == 0:
            raise ValueError('No thread specified!')
        page = self.session.get(thread).content
        number_of_posts = html.fromstring(page).xpath(Donbot.post_count_path)[0]
        return int(number_of_posts[:number_of_posts.find(' ')].strip())

    def activity_overview(self, thread=None):
        """Get the activity overview information associated with a thread.

        Contains information about the timing of each user's first post and last post as well as
        the time since their last post and the number of posts they have made total.
        """
        thread = thread if thread else self.thread
        if len(thread) == 0:
            raise ValueError('No thread specified!')
        page = self.session.get(thread+'&activity_overview=1').content
        user_info = []
        for row in html.fromstring(page).xpath(Donbot.activity_path)[1:]:
            row_text = row.xpath(".//text()")
            user_info.append(
                {'user': row_text[5],
                 'first_post': row_text[8].strip(),
                 'last_post': row_text[10].strip(),
                 'since_last': row_text[12].strip(),
                 'total_posts': row_text[15]})
        return user_info

    def collect_posts(self, thread=None, start=0, end=float('infinity'), logged_in=True):
        """Collects the posts in a thread over an optionally specified start and end post range."""
        thread = self.thread if not thread else thread
        if len(thread) == 0:
            raise ValueError('No thread specified!')

        # check end or # of posts in thread to find pages we need to examine
        start_page = floor(start / Donbot.posts_per_page)
        end_page = (floor(end / Donbot.posts_per_page) if end != float('infinity')
                    else floor(self.number_of_posts(thread) / Donbot.posts_per_page))

        # collect on each page key content from posts after current post
        new_posts = []
        for i in range(start_page * 25, (end_page + 1) * 25, 25):
            if logged_in:
                page = self.session.get(thread + '&start=' + str(i)).content
            else:
                page = requests.get(thread + '&start=' + str(i)).content
            for post in html.fromstring(page).xpath(Donbot.posts_path):
                p = {'number': int(post.xpath(Donbot.number_path)[0][1:])}
                if start <= p['number'] <= end:
                    p['user'] = post.xpath(Donbot.user_path)[0]
                    p['content'] = html.tostring(post.xpath(Donbot.content_path)[0])
                    p['content'] = p['content'].decode('UTF-8').strip()[21:-6]

                    # requires some postprocessing to turn into a datetime
                    stamp = post.xpath(Donbot.date_time_path)[-1]
                    p['datetime'] = stamp[stamp.find('» ') + 2:].strip()
                    p['datetime'] = dt.strptime(p['datetime'], Donbot.post_stamp)
                    new_posts.append(p)
        return new_posts

    def make_post(self, content, thread=None, post_delay=None):
        """Make a post in a thread after a delay with the specified content."""
        post_delay = post_delay if post_delay else self.post_delay
        thread = thread if thread else self.thread
        if len(thread) == 0:
            raise ValueError('No thread specified!')

        # one request to get form info for post,
        thread_id = thread[thread.find('?') + 1:]
        page = html.fromstring(self.session.get(
            Donbot.post_url.format(thread[thread.find('?') + 1:])).content)

        # and another to make it
        form = {'message': content,
                'addbbcode20': 100,
                'post': 'Submit',
                'disable_smilies': 'on',
                'attach_sig': 'on',
                'icon': 0}
        for name in ['topic_cur_post_id', 'lastclick', 'creation_time', 'form_token']:
            form[name] = page.xpath(Donbot.post_form_path.format(name))[0]

        time.sleep(post_delay)
        return self.session.post(Donbot.post_url.format(thread[thread.find('?') + 1:]), form)

    def send_pm(self, send_to=None, subject='Donbot-Generated Filler', body='Donbot-Generated Filler', post_delay=None):
        """Send a pm with the specified subject and body to a user after an optionally specified delay."""

        # one request to get form info for pm, and another to send it
        # a third request gets userid matching user
        send_to = send_to if send_to else self.username
        send_to = [send_to] if isinstance(send_to, str) else send_to
        user_ids = [self.user_id(user) for user in send_to]
        post_delay = post_delay if post_delay else self.post_delay
        compose = html.fromstring(self.session.get(Donbot.pm_url).content)

        form = {'username_list': '', 'subject': subject, 'message': body,
                'addbbcode20': 100, 'message': body, 'status_switch': 0,
                'post': 'Submit', 'attach_sig': 'on',
                'disable_smilies': 'on'}
        for user in user_ids:
            form['address_list[u][{}]'.format(user)] = 'to'

        for name in ['lastclick', 'creation_time', 'form_token']:
            form[name] = compose.xpath(Donbot.post_form_path.format(name))[0]

        time.sleep(post_delay)
        self.session.post(Donbot.pm_url, form)

    def toggle_lock(self, thread=None, post_delay=None):
        post_delay = post_delay if post_delay else self.post_delay
        thread = thread if thread else self.thread
        if len(thread) == 0:
            raise ValueError('No thread specified!')

        # one request to get form info for lock

        # another request to get to confirmation page

        # a final request to confirm

#%%
bot = Donbot(username='myusername', password='mypassword')