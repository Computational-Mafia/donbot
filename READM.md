
# Your Personal Modbot
Your Personal Modbot is a client-side implementation of tools automating actions related to moderating games on mafiascum.net. Start the app and input your user information, and you'll have a bot of your own to complete any of an eventually wide variety of tasks.

A prototypical implementation of the client-side implementation of Modbot, this version starts a local server for the user where they can privately input their user info and initiate a pagetopping bot, a bot that automatically stalks a thread for opportunities to pagetop it using the user's account for as long as its associated browser window remains open and connected to the web.

To grow Modbot without extending its simple interface, just add an additional page function under the Page Functions heading below and link to the function's associated page in the html associated with Modbot index (and recompile as a python script and then an executable). 

Future implementations of Your Personal Modbot are intended to involve adding further options beyond Pagetopper to the Modbot Index for carrying out other automated modding activities, such as generating votecounts or sending Role PMs.

`personalmodbot.py` is produced by converting the front-facing notebook `personalmodbot.ipynb` using the jupyter command `jupyter nbconvert --to script personalmodbot.ipynb`. The executable file `personalmodbot.exe` is produced by calling `pyinstaller -F personalmodbot.py` within the appropriate OS environment.

**Please** don't use these functions haphazardly, especially those that make posts or send pms, as misuse thereof can be against Site Rules, get you banned, and most importantly cause trouble for a lot of decent people.

## Setup

### Dependencies


```python
from flask import Flask, session, redirect, url_for, escape, request
from time import sleep
from donbot import Donbot
from math import ceil
from  os import urandom
```

### App HTML


```python
indexhtml = '''
<title>Modbot: Index</title>
<h1>Tool Index</h1>
Here's an index of all the tools currently available. Select an option below:
<br><br><a href={}>Pagetopper</a>
<br><br><br><a href={}>Log Out</a>
'''

loginhtml = '''
<title>Modbot: Login</title>
<h1>Login</h1>
Welcome to Modbot.
You haven't provided a username and password yet.<br>
Careful: if you input incorrect values, your tools probably won't work.
<form method="post">
    <p>Username: <input type=text name=username>
    <p>Password: <input type=text name=password>
    <p><input type=submit value=Login>
</form>
'''

pagetopperformhtml='''
<title>Modbot: Pagetopper</title>
<h1>Pagetopper</h1>
An app that stalks the input thread for opportunities to pagetop. Useful for reserving thread real estate for votecounts or other announcements. Just input the post you want the bot to make, the thread you want it made in, and how regularly you want the bot to check the thread (respecting the potential burden on the site!).
<form method="post">
    <p>Post Content: <textarea rows="7" cols="80" name=content>reserving this post with a pagetopping bot</textarea>
    <p>Thread URL: <input type=text name=thread>
    <p>Refresh Rate: <input type=text name=interval value='60'> seconds.
    <p><input type=submit value=Submit>
    <br><br><br><a href={}>Modbot Index</a>
    <br><a href={}>Log Out</a>
</form>
'''

pagetopperoperatinghtml = '''
<title>Modbot: Pagetopper</title>
<h1>Pagetopper</h1>
Now operating using previously defined parameters. 
Thread will be checked again for an opportunity to pagetop every time the countdown drops to zero. 
Leave page or reset parameters to stop.
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
```

### Starter Variables


```python
postsPerPage = 25.0

app = Flask(__name__)
app.secret_key = urandom(16)
```

## Page Functions

### Modbot Index
An index of all available Modbot functionality that can be selected from.


```python
@app.route('/')
def index():
    if not authenticated():
        return redirect(url_for('login'))
    return indexhtml.format(url_for('pagetopper'), url_for('logout'))
```

### Modbot Login and Logout
Collect or discard user information related to Modbot.


```python
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        for each in ['username', 'password']:
            session[each] = request.form[each]
        return redirect(url_for('index'))
    return loginhtml

@app.route('/logout')
def logout():
    session = {}
    return redirect(url_for('login'))

def authenticated():
    return ('username' in session and 'password' in session)
```

### Pagetopper
a bot that automatically stalks a thread for opportunities to pagetop it using the user's account for as long as its associated browser window remains open and connected to the web


```python
@app.route('/pagetopper', methods=['GET', 'POST'])
def pagetopper():
    if not authenticated():
        return redirect(url_for('login'))
    if request.method == 'POST':
        for each in ['thread', 'content', 'interval']:
            session['pagetopper-{}'.format(each)] = request.form[each]
    if not ('pagetopper-thread' in session
            and 'pagetopper-content' in session
            and 'pagetopper-interval' in session):
        return pagetopperformhtml.format(
            url_for('index'), url_for('logout'))
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
    return pagetopperoperatinghtml.format(
        content, thread, interval, url_for('pagetopper_reset'),
        url_for('index'), url_for('logout'), url_for('pagetopper'))

@app.route('/pagetopper_reset') # for resetting pagetopper parameters
def pagetopper_reset():
    for each in ['thread', 'content', 'interval']:
        session.pop('pagetopper-{}'.format(each))
    return redirect(url_for('pagetopper'))
```

## Start the Flask App


```python
if __name__ == "__main__":
    app.run()
```

     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    127.0.0.1 - - [11/May/2018 05:05:39] "POST /pagetopper HTTP/1.1" 302 -
    127.0.0.1 - - [11/May/2018 05:05:39] "GET /login HTTP/1.1" 200 -
    127.0.0.1 - - [11/May/2018 05:05:44] "POST /login HTTP/1.1" 302 -
    127.0.0.1 - - [11/May/2018 05:05:44] "GET / HTTP/1.1" 200 -
    127.0.0.1 - - [11/May/2018 05:05:45] "GET /pagetopper HTTP/1.1" 200 -
    127.0.0.1 - - [11/May/2018 05:05:49] "POST /pagetopper HTTP/1.1" 200 -
    127.0.0.1 - - [11/May/2018 05:06:33] "GET /pagetopper_reset HTTP/1.1" 302 -
    127.0.0.1 - - [11/May/2018 05:06:33] "GET /pagetopper HTTP/1.1" 200 -
    127.0.0.1 - - [11/May/2018 05:06:35] "GET / HTTP/1.1" 200 -
    
