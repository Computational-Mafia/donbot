
# coding: utf-8

# # Your Personal Modbot
# Your Personal Modbot is a client-side implementation of tools automating actions related to moderating games on mafiascum.net. Start the app and input your user information, and you'll have a bot of your own to complete any of an eventually wide variety of tasks.
# 
# A prototypical implementation of the client-side implementation of Modbot, this version starts a local server for the user where they can privately input their user info and initiate a pagetopping bot, a bot that automatically stalks a thread for opportunities to pagetop it using the user's account for as long as its associated browser window remains open and connected to the web.
# 
# To grow Modbot without extending its simple interface, just add an additional page function under the Page Functions heading below and link to the function's associated page in the html associated with Modbot index (and recompile as a python script and then an executable). 
# 
# Future implementations of Your Personal Modbot are intended to involve adding further options beyond Pagetopper to the Modbot Index for carrying out other automated modding activities, such as generating votecounts or sending Role PMs.
# 
# `personalmodbot.py` is produced by converting the front-facing notebook `personalmodbot.ipynb` using the jupyter command `jupyter nbconvert --to script personalmodbot.ipynb`. The executable file `personalmodbot.exe` is produced by calling `pyinstaller -F personalmodbot.py` within the appropriate OS environment.
# 
# **Please** don't use these functions haphazardly, especially those that make posts or send pms, as misuse thereof can be against Site Rules, get you banned, and most importantly cause trouble for a lot of decent people.
# 
# **Interested in making your instance of this application accessible over the web?  
# Consider Localtunnel: https://localtunnel.github.io/www/**  
# Once you install it with `npm install -g localtunnel`, entering `lt --port XXXX` where XXXX is the port of your currently active application server (eg 5000) should return a url you can use anywhere. Be careful sharing it!**
# 

# ## Setup

# ### Dependencies

# In[1]:


import os
os.chdir('C:\\Users\\jgunn\\Downloads\\modbot-master\\client')


# In[2]:


from flask import Flask, session, redirect, url_for, escape, request
from donbot import Donbot
import VoteCounter
from VoteCounter import includesVote
from os import urandom


# ### App HTML

# In[3]:


indexhtml = '''
<title>Modbot: Index</title>
<h1>Tool Index</h1>
Here's an index of all the tools currently available. 
Select an option below:
<br><br><a href={}>Pagetopper</a>
<br><a href={}>Votecounter Demo</a>
<br><br><br><a href={}>Log Out</a>
'''

loginhtml = '''
<title>Modbot: Login</title>
<h1>Login</h1>
Welcome to Modbot.
You haven't provided a username and password yet.<br>
Careful: if you input incorrect values, 
your tools probably won't work.
<form method="post">
    <p>Username: <input type=text name=username>
    <p>Password: <input type=text name=password>
    <p><input type=submit value=Login>
</form>
'''

pagetopperformhtml='''
<title>Modbot: Pagetopper</title>
<h1>Pagetopper</h1>
An app that stalks the input thread for opportunities to pagetop. 
Useful for reserving thread real estate for votecounts or other 
announcements. Just input the post you want the bot to make, the 
thread you want it made in, and how regularly you want the bot to 
check the thread (respecting the potential burden on the site!).
<form method="post">
    <p>Post Content: <textarea rows="7" cols="80" name=content>
    reserving this post with a pagetopping bot</textarea>
    <p>Thread URL: <input type=text name=thread>
    <p>Refresh Rate: 
    <input type=text name=interval value='60'> seconds.
    <p><input type=submit value=Submit>
    <br><br><br><a href={}>Modbot Index</a>
    <br><a href={}>Log Out</a>
</form>
'''

pagetopperoperatinghtml = '''
<title>Modbot: Pagetopper</title>
<h1>Pagetopper</h1>
Now operating using previously defined parameters. Thread will be 
checked again for an opportunity to pagetop every time the countdown 
drops to zero. Leave page or reset parameters to stop.
<p><strong>Post Content:</strong><br>{}
<p><strong>Thread URL:</strong><br>{}
<p><strong>Countdown:</strong><br><span id="counter">{}</span>
<br><br><br><a href={}>Reset Parameters</a>
<br><a href={} target="_blank">Modbot Index</a>
<br><a href={}>Log Out</a>
<script>
    setInterval(function() {{
        var div = document.querySelector("#counter");
        var count = div.textContent * 1 - 1;
        div.textContent = count;
        if (count <= 0) {{
            window.location.replace("{}");
        }}
    }}, 1000);
</script>
'''

votedemoformhtml='''
<title>Modbot: Votecounter Demo</title>
<h1>Votecounter Demo</h1>
A demo of Psyche's votecounter, this bot tries to extract the votes 
from the range of input posts in the input thread based on an input 
playerlist and from this set of votes prints a simple votecount. 
Default values are an example taken from D1 of the recently completed 
Mini 1991. If the Votecounter makes a mistake counting votes in any 
actual game, once completed, please PM Psyche about it so that the
votecounter can be improved further.
<form method="post">
    <p>Playerlist (with each slot on its own line, usernames sharing slots split by ' replaced '): 
    <br><textarea rows="7" cols="80" name=players>
profii
Havo
Nero Cain
Chumba
Chickadee
Jodaxq
Joey_ replaced sheepsaysmeep replaced brassherald
Tchill13
eth0s
osuka
Not Known 15
schadd_
HeWhoSwims</textarea>
    <p>Thread URL:       <input type=text name=thread 
        value='https://forum.mafiascum.net/viewtopic.php?f=53&t=74913'>
    <p>Start Post Number: <input type=text name=start value='0'>
    <p>Last Post Number: <input type=text name=stop value='1125'>
    <p><input type=submit value=Submit>
    <br><br><br><a href={}>Modbot Index</a>
    <br><a href={}>Log Out</a>
</form>
'''

votedemooperatinghtml = '''
<title>Modbot: Votecounter Demo</title>
<h1>Votecounter Demo</h1>
<p>Here are results using previously defined parameters. If results are 
mistaken for any actual game, once completed, please PM Psyche about 
it so that the votecounter can be improved further.
<p>Rather than being very strict about what counts as a vote (ie 
looking for proper vote formatting and exact target naming), Psyche's 
votecounter is intended to work like human moderators do, or at least 
have over the D1s of ~300 Mini Normal Games studied to produce the 
counter. The votecounter has been found to accurately predict 
which player a moderator assigned a lynch to across nearly all of 
these studied games - all without relying on any explicit database of 
aliases.
<p>If aliases *are* totally necessary to understand the target of 
a vote (for example, when someone uses a user's true first name 
instead of some nickname based on their username), this vote counter 
is a bit more likely to fail since there's no context it can use to 
make the connection. In order to include aliases in this demo, treat 
aliases as player replacements when specifying your player list.
<p><strong>Vote Count:</strong><br>{}
<p><strong>Player List:</strong><br>{}
<p><strong>Thread URL:</strong><br>{}
<p><strong>Start Post Number:</strong><br>{}
<p><strong>Last Post Number:</strong><br>{}
<br><br><br><a href={}>Reset Parameters</a>
<br><a href={} target="_blank">Modbot Index</a>
<br><a href={}>Log Out</a>
'''


# ### Starter Variables

# In[4]:


postsPerPage = 25.0

app = Flask(__name__)
app.secret_key = urandom(16)


# ## Page Functions

# ### Modbot Index
# An index of all available Modbot functionality that can be selected from.

# In[5]:


@app.route('/')
def index():
    # if user isn't logged in, send them to login
    # otherwise return an index of available functions
    if not authenticated():
        return redirect(url_for('login'))
    return indexhtml.format(url_for('pagetopper'), 
                            url_for('votedemo'),
                            url_for('logout'))


# ### Modbot Login and Logout
# Collect or discard user information related to Modbot.

# In[6]:


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if a POST request, try to store user and pass
    # otherwise, return a form for these variables
    if request.method == 'POST':
        for each in ['username', 'password']:
            session[each] = request.form[each]
        return redirect(url_for('index'))
    return loginhtml

@app.route('/logout')
def logout():
    # clear session and redirect to login
    session = {}
    return redirect(url_for('login'))

def authenticated():
    # True if user has logged in; False if they've logged out
    return ('username' in session and 'password' in session)


# ### Pagetopper
# a bot that automatically stalks a thread for opportunities to pagetop it using the user's account for as long as its associated browser window remains open and connected to the web

# In[7]:


@app.route('/pagetopper', methods=['GET', 'POST'])
def pagetopper():
    # if user isn't logged in, send them to login
    if not authenticated():
        return redirect(url_for('login'))
    
    # if a POST request, store key variables in session
    if request.method == 'POST':
        for each in ['thread', 'content', 'interval']:
            session['pagetopper-{}'.format(each)] = request.form[each]
    
    # if pagetopper vars not in session, return pagetopper form
    if not ('pagetopper-thread' in session
            and 'pagetopper-content' in session
            and 'pagetopper-interval' in session):
        return pagetopperformhtml.format(
            url_for('index'), url_for('logout'))
    
    # if pagetopper vars are in session, 
    # check thread for opportunity to pagetop and do so if applicable
    thread = session['pagetopper-thread']
    interval = session['pagetopper-interval']
    content = session['pagetopper-content']
    bot = Donbot(username=session['username'],
                 password=session['password'], 
                 thread=thread)
    current = (session['pagetopper-current']
               if 'pagetopper-current' in session
               else ceil(bot.getNumberOfPosts()/postsPerPage))
    update = bot.getNumberOfPosts()
    if (current != ceil(update/postsPerPage) or update % 25 == 0):
        bot.makePost(content)
        current = ceil(bot.getNumberOfPosts()/postsPerPage)
        
    # return page reporting progress and including a countdown
    # until this function will be automatically be requested again
    return pagetopperoperatinghtml.format(
        content, thread, interval, url_for('pagetopper_reset'),
        url_for('index'), url_for('logout'), url_for('pagetopper'))

@app.route('/pagetopper_reset')
def pagetopper_reset():
    # remove from session all pagetopper parameters and redirect back
    for each in ['thread', 'content', 'interval']:
        session.pop('pagetopper-{}'.format(each))
    return redirect(url_for('pagetopper'))

# use this instead of math.ceil so that client app can be smaller
def ceil(number):
    rounded = round(number)
    return rounded if rounded >= number else rounded+1


# ### Votecounter Demo
# A demo of Psyche's votecounter, this bot tries to extract the votes from the range of input posts in the input thread based on an input playerlist and from this set of votes prints a simple votecount.

# In[ ]:


@app.route('/votedemo', methods=['GET', 'POST'])
def votedemo():
    # if user isn't logged in, send them to login
    if not authenticated():
        return redirect(url_for('login'))
    
    # if a POST request, store key variables in session
    if request.method == 'POST':
        for each in ['players', 'thread', 'start', 'stop']:
            session['votedemo-{}'.format(each)] = request.form[each]
    
    # if votedemo vars not in session, return votedemo form
    if not ('votedemo-players' in session
            and 'votedemo-thread' in session
            and 'votedemo-start' in session
            and 'votedemo-stop' in session):
        return votedemoformhtml.format(
            url_for('index'), url_for('logout'))
    
    # initialize votecounter
    thread, slots, players = session['votedemo-thread'], [], []
    for s in session['votedemo-players'].split('\n'):
        s = s.strip()
        slots.append(s.split(' replaced '))
        players += s.split(' replaced ')

    go, stop = session['votedemo-start'], session['votedemo-stop']
    bot = Donbot(username=session['username'],
                 password=session['password'],
                 thread=thread)
    extracter = VoteCounter.VoteExtracter(players)
    
    # use playerlist to initialize votecount
    votesByVoter = {}
    votesByVoted = {}
    for i in range(len(slots)):
        votesByVoter[i] = len(slots)
        votesByVoted[i] = []
    votesByVoted[len(slots)] = list(range(len(slots)))
    
    for post in bot.getPosts(start=int(go), end=int(stop), loggedin=False):
        # ignore posts not made by players
        if players.count(post['user']) == 0:
            continue
        
        # ignore posts that don't include a vote; otherwise get vote
        if not includesVote(post):
            continue
        
        # get target(s) of vote from post and update votecount
        votes = [vote for vote in extracter.fromPost(post)]
        for voted in votes:
            voterslot = [slots.index(s) for s in slots
                         if s.count(post['user']) > 0][0]
            votedslot = (len(slots) if voted == "UNVOTE"
                         else [slots.index(s) for s in slots
                               if s.count(voted) > 0][0])
        
            # update votesByVoter, temporarily track the old vote
            old = votesByVoter[voterslot]
            votesByVoter[voterslot] = votedslot

            # update votesByVoted
            del votesByVoted[old][votesByVoted[old].index(voterslot)]
            votesByVoted[votedslot].append(voterslot)
    
    # construct text-based representation of votecount
    votecount = ''
    for i in votesByVoted.keys():
        voted = 'Not Voting' if i == len(slots) else slots[i]
        voters = [slots[voter] for voter in votesByVoted[i]]
        votecount += '{} - {} votes:<br>'.format(voted, len(voters))
        for each in voters:
            votecount += str(each) + ', '
        votecount += '<br>' if len(voters) == 0 else '<br><br>'
    
    # return page rendering output
    return votedemooperatinghtml.format(
        votecount, '<br>'.join(players), thread, go, stop, 
        url_for('votedemo_reset'), url_for('index'), url_for('logout'))

@app.route('/votedemo_reset')
def votedemo_reset():
    # remove from session all pagetopper parameters and redirect back
    for each in ['players', 'thread', 'start', 'stop']:
        session.pop('votedemo-{}'.format(each))
    return redirect(url_for('votedemo'))


# ## Start the Flask App

# In[ ]:


if __name__ == "__main__":
    app.run()

