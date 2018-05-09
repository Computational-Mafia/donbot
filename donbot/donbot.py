
# coding: utf-8

# # Donbot
# The donbot module is a simple module w/ a class that makes it super easy to automate interactions with mafiascum.net.
# Create an instance of the Donbot class with your username and password 
# (and potentially other parameters), and you'll be able to:
# - Collect a range of posts from a thread
# - Make posts in a specified thread with specified content
# - Send pms to a user with a specified subject and body
# - Collect the number of posts in a specified thread
# - Collect id matching a specified scummer's username
# - And, eventually, more!
# 
# `donbot.py` is produced by converting the front-facing notebook `donbot.ipynb` using the jupyter command `jupyter nbconvert --to script donbot.ipynb`. Consult `donbotdemo.ipynb` for a tutorial on how to use the module.
# 
# **Please** don't use these functions haphazardly, especially those that make posts or send pms, as misuse thereof can be against Site Rules, get you banned, and most importantly cause trouble for a lot of decent people.

# ## Setup

# ### Dependencies

# In[1]:


from datetime import datetime as dt # to parse timestamps
from datetime import timedelta # parsing hours/minutes
from math import ceil          # to get page# from post
from lxml import html          # to help parse website content
import requests                # for interacting with website
import time                    # need delays before post requests
import gevent                  # async/concurrency
from gevent import monkey
# patches stdlib (including socket and ssl modules) to cooperate with other greenlets
monkey.patch_all()


# ### Urls donbot will construct requests with

# In[2]:


# generic site url; will start other urls
siteurl = 'https://forum.mafiascum.net/'

# where bot logs into mafiascum.net
loginurl = siteurl + 'ucp.php?mode=login'

# format w/ username and get to obtain page w/ their userid on it
userurl = siteurl + 'search.php?keywords=&terms=all&author={}'

# make post request here w/ right format to make a post to thread
posturl = siteurl + 'posting.php?mode=reply&{}'

# post request here w/ form to send a pm
pmurl = siteurl + 'ucp.php?i=pm&mode=compose'


# ### Paths to elements donbot will grab info from

# In[3]:


# number of posts in thread assoc'd w/ page
postcountpath = "//div[@class='pagination']/text()"

# every post on current page
postspath = '//div[@class="post bg2" or @class="post bg1"]'

# post# of a post
numberpath = ".//p[@class='author']/a/strong/text()"

# username assoc'd w/ a post
userpath = ".//dl[@class='postprofile']/dt/a/text()"

# content of a post
contentpath = ".//div[@class='content']"

# timestamp of a post
datetimepath = ".//p[@class='author']/text()"

# path to value of all input elements on page with specified name
postformpath = "//input[@name='{}']/@value"

# at userurl, path to link that has their userid
userlinkpath = "//dt[@class='author']/a/@href"

# at activityoverview page, path to cells of page's main table
activitypath = "//table//table//div"


# ### Other static variables used across instances

# In[4]:


postsperpage = 25 # number of posts per thread page
poststamp = '%a %b %d, %Y %I:%M %p' # post timestamp structure
#overviewstamp = '%b %d, %I:%M%p' # activity overview timestamps


# ## The Donbot Class

# In[5]:


class Donbot:
    
    def __init__(self, username, password, thread=None, postdelay=1.5):
        self.postdelay = postdelay # seconds to wait before post requests
        self.thread = thread
        self.username = username
        self.session = requests.Session()
        self.session.post(loginurl, 
                          {'username': username, 'password': password,
                           'redirect': 'index.php', 'login': 'Login'})
        
    def getUserID(self, username):
        # Search for posts by user; userID is in link in first result.
        username = username.replace(' ', '+')
        page = self.session.get(userurl.format(username)).content
        userposts = html.fromstring(page)
        userlink = userposts.xpath(userlinkpath)[0]
        return userlink[userlink.rfind('=')+1:]
    
    def getNumberOfPosts(self, thread=None):
        thread = thread if thread else self.thread
        if len(thread) == 0:
            raise ValueError('No thread specified!')
        page = self.session.get(thread).content
        numberOfPosts = html.fromstring(page).xpath(postcountpath)[0]
        return int(numberOfPosts[:numberOfPosts.find(' ')].strip())
    
    def getActivityOverview(self, thread=None):
        thread = thread if thread else self.thread
        if len(thread) == 0:
            raise ValueError('No thread specified!')
        page = self.session.get(thread+'&activity_overview=1').content
        userinfo = []
        for row in html.fromstring(page).xpath(activitypath)[1:]:
            rowtext = row.xpath(".//text()")
            userinfo.append({'user': rowtext[5],
                             'firstpost': rowtext[8].strip(),
                             'lastpost': rowtext[10].strip(),
                             'sincelast': rowtext[12].strip(),
                             'totalposts': rowtext[15]})
        return userinfo
        
    def getPosts(self, thread=None, start=0, end=float('infinity')):
        thread = self.thread if not thread else thread
        if len(thread) == 0:
            raise ValueError('No thread specified!')
            
        # check end or # of posts in thread to find pages we need to examine
        startpage = ceil(start/postsperpage)
        endpage = (ceil(end/postsperpage) if end != float('infinity')
                   else ceil(self.getNumberOfPosts(thread)/postsperpage))
        
        # collect on each page key content from posts after currentpost
        newposts = []
        for i in range(startpage*25, endpage*25, 25):
            page = self.session.get(thread+'&start='+str(i)).content
            for post in html.fromstring(page).xpath(postspath):
                p = {}
                p['number'] = int(post.xpath(numberpath)[0][1:])
                if p['number'] >= start and p['number'] <= end:
                    p['user'] = post.xpath(userpath)[0]
                    p['content'] = html.tostring(post.xpath(contentpath)[0])
                    p['content'] = p['content'].decode('UTF-8')

                    # requires some postprocessing to turn into a datetime
                    stamp = post.xpath(datetimepath)[-1]
                    p['datetime'] = stamp[stamp.find('» ')+2:].strip()
                    p['datetime'] = dt.strptime(p['datetime'], posttimestamp)
                    newposts.append(p)
        return newposts
        
    def makePost(self, content, thread=None, postdelay=None):
        postdelay = postdelay if postdelay else self.postdelay
        thread = thread if thread else self.thread
        if len(thread) == 0:
            raise ValueError('No thread specified!')
        
        # one request to get form info for post, and another to make it
        threadid = thread[thread.find('?')+1:]
        page = html.fromstring(self.session.get(
            posturl.format(thread[thread.find('?')+1:])).content)
        form = {'message': content, 'addbbcode20': 100,
                'post': 'Submit', 'disable_smilies': 'on',
                'attach_sig': 'on', 'icon': 0}
        for name in ['topic_cur_post_id', 'lastclick',
                     'creation_time','form_token']:
            form[name] = page.xpath(postformpath.format(name))[0]

        time.sleep(postdelay)
        self.session.post(posturl.format(
            thread[thread.find('?')+1:]), form)
        
    def sendPM(self, subject, body, sendto, postdelay=None):
        # one request to get form info for pm, and another to send it
        # a third request gets userid matching user
        if len(sendto) == 0:
            raise ValueError('sendTo field missing')

        if isinstance(sendto, str):
            sendto = [sendto]

        uids = [gevent.spawn(self.getUserID, user) for user in sendto]
        pminfo = gevent.spawn(self.session.get, pmurl)

        gevent.wait(uids)
        gevent.wait([pminfo])

        if(not pminfo.successful()):
            raise Exception('Failed to get pm info')

        postdelay = postdelay if postdelay else self.postdelay
        compose = html.fromstring(pminfo.value.content)

        form = {'username_list':'', 'subject':subject, 'addbbcode20':100,
                'message':body, 'status_switch':0, 'post':'Submit',
                'attach_sig':'on', 'disable_smilies':'on'}
        for user in uids:
            form['address_list[u][{}]'.format(user.value)] = 'to'

        for name in ['lastclick', 'creation_time', 'form_token']:
            form[name] = compose.xpath(postformpath.format(name))[0]

        time.sleep(postdelay)
        self.session.post(pmurl, form)
