
# Donbot
The donbot module is a simple module w/ a class that makes it super easy to automate interactions with mafiascum.net.
Create an instance of the Donbot class with your username and password 
(and potentially other parameters), and you'll be able to:
- Collect a range of posts from a thread
- Make posts in a specified thread with specified content
- Send pms to a user with a specified subject and body
- Collect the number of posts in a specified thread
- Collect id matching a specified scummer's username
- And, eventually, more!

**Please** don't use these functions haphazardly, especially those that make posts or send PMs, as misuse thereof can be against Site Rules, get you banned, and most importantly cause trouble for a lot of decent people.

This is a quick tutorial on how to use Donbot so that even Python beginners can quickly begin using it. Please let someone know if it's wrong or unclear, because it'll always be a work in progress.

## File Organization
Module: `donbot/donbot.py`  
Module Details: `donbot/donbot.ipynb`  
Tutorial iPython Notebook: `donbot/donbotdemo.ipynb`

## Starting a Donbot Instance
Before we start, make sure you have the Python packages `lxml` and `requests`. They're pretty easy to get, I think; you probably only need to type "`pip install lxml`" and "`pip install requests`" into your command prompt. Check the websites for these packages for more details. I believe other dependencies of the donbot module come with Python.

Making donbot accessible to your script or notebook is as simple as placing `donbot.py` in your working directory and including the following before you start using it:


```python
from donbot import Donbot
```

Once you import the module, to use it you have to first initialize a Donbot instance. What you have to include in this first initialization depends on what you intend to do with the bot. There are 2 required and 2 optional parameters:
- `username` (required): the username your bot will use to log in

- `password` (required): the password your bot will use to log in

- `thread` (defaults to `None`): the url of the thread this instance of Donbot will assume you're talking about when you call a function like getPosts(); unnecessary if you aren't using Donbot to do anything in a particular thread or prefer to specify the thread url when you call a thread-processing function

- `postdelay` (defaults to `1.5`): the number of seconds you want Donbot to pause before it submits information to mafiascum.net; I've found that if successive POST requests are sent too quickly to site, errors can occur. Leave this alone if you don't know what I'm talking about.

Here are some examples of ways you might start a Donbot instance:


```python
# im going to do stuff across some threads
bot = Donbot(username='myusername', password='mypassword')

# im going to do stuff mainly in one thread, need to be logged in,
# and want 0 seconds of delay imposed between my POST requests
bot = Donbot(username='myusername', password='mypassword',
            thread='https://forum.mafiascum.net/viewtopic.php?f=5&t=76109',
            postdelay=0.0)
```

## Using a Donbot Instance
So you've started your Donbot instance and assigned it to the variable "bot". How do you use it to do stuff? Thanks to this module, it's pretty easy.

#### To get the userID associated with a username


```python
bot.getUserID('Psyche')
```




    '15830'



#### To count the number of posts in a thread


```python
# If you included the target thread as a parameter 
# when you started your Donbot instance:
bot.getNumberOfPosts()

# otherwise
targetthread = 'https://forum.mafiascum.net/viewtopic.php?f=5&t=76109'
bot.getNumberOfPosts(targetthread)
```




    22



#### To collect the activity overview of a thread.


```python
# If you included the target thread as a parameter 
# when you started your Donbot instance:
bot.getActivityOverview()

# otherwise
targetthread = 'https://forum.mafiascum.net/viewtopic.php?f=5&t=76109'
rows = bot.getActivityOverview(targetthread)

# let's see an element the output as an example:
rows[:3]
```




    [{'firstpost': 'Apr 30, 06:32pm',
      'lastpost': 'May 04, 08:56am',
      'sincelast': '0 days 0 hours',
      'totalposts': '16',
      'user': 'Psyche'},
     {'firstpost': 'May 01, 09:27am',
      'lastpost': 'May 04, 12:47am',
      'sincelast': '0 days 8 hours',
      'totalposts': '9',
      'user': 'Flubbernugget'},
     {'firstpost': 'May 03, 11:54am',
      'lastpost': 'May 03, 04:03pm',
      'sincelast': '0 days 17 hours',
      'totalposts': '2',
      'user': 'yessiree'}]



As you can see, getActivityOverview() returns a list of Python dictionaries, which each summarize the key information about a user's present on the thread's activity overview page, including info about when they made their first and latest post to the thread, their total number of posts in the thread, and the number of days and hours since their last post.

#### To collect a range of posts from a thread


```python
# you included the target thread as a parameter when you started bot 
# and want every post in that thread:
posts = bot.getPosts()

# you didnt include the target thread as an instantiation parameter
# and you want just posts 2 through 5, inclusive
targetthread = 'https://forum.mafiascum.net/viewtopic.php?f=5&t=76109'
posts = bot.getPosts(targetthread, start=2, end=5)

# you did include the target thread as an instantiation parameter
# and you want all the posts up through post #3 (that's 4 posts total!)
posts = bot.getPosts(end=3)

# example output
print(posts[-2:])
```

    {'number': 3, 'user': 'Psyche', 'content': '<div class="content">The main thing I want to talk about *right now* is the part where the data structure of voting data my votecounter makes is converted into a formatted votecount post for game mods to post. It doesn\'t seem very straightforward given the variety of ways mods like to format their votecounts.</div>\n\n\t\t\t', 'datetime': datetime.datetime(2018, 4, 30, 18, 44)}
    

As you can see, getPosts() returns a list of posts, which are each Python dictionaries with all the key information about the post, including its number, its timestamp, who posted it, and its content.

#### To make a post


```python
content = 'This is a test post. I made it with a bot.'

# if you included the target thread as a parameter when you started bot
bot.makePost(content)

# if you didnt
targetthread = 'https://forum.mafiascum.net/viewtopic.php?f=5&t=76109'
bot.makePost(content, thread=targetthread)
```

#### To send a pm


```python
subject = 'Re: Artfully Selected Movement Sequences of the Title Fairy'
body = 'you are the worst title fairy ever'
sendto = 'Psyche'

bot.sendPM(subject, body, sendto)
```

# Conclusion
To really get into the details about how Donbot works, check out its associated iPython Notebook, `donbot.ipynb`. It has the exact same content as `donbot.py`, but with formatting to make it easier to read. 
