# Donbot: Automate Activities on Mafiascum.net 🤖🤵
Donbot is a Python library for automating activities on mafiascum.net. 

Forum-based mafia games are a popular form of social deduction game. Mafiascum.net is a popular forum for playing these games. Donbot is designed to make it easier to interact with the site programmatically. By having a pre-existing implementation of all the main ways to interact with the site, it should be easier for bot developers to focus on the logic of what they want done, rather than the minutiae of constructing valid requests and parsing the site's html.

For game moderators, the library can be used to automate the process of updating the game thread with votecounts, player lists, and other information. For players and researchers, the library can be used to automate the process of collecting and analyzing data from the site. Even outside of games, the tools can help manage complex threads or send mass PMs customized to each recipient.

**Please** don't use these functions haphazardly, especially those that make posts or send PMs, as misuse thereof can be against Site Rules, get you banned, and most importantly cause trouble for a lot of decent people.

## Usage 🍲

For most users, Donbot is most easily by importing the `Donbot` class and initializing it with your account credentials -- ideally in a more secure way than hardcoding them into your script. You can either specify the thread you want to interact with when you initialize the bot (ideal when it's just that one thread), or specify it later when you call a function that requires it.

```python
from donbot import Donbot

# instantiating the bot
bot = Donbot(
    username='myusername', 
    password='mypassword', 
    thread='https://forum.mafiascum.net/viewtopic.php?f=5&t=76109'
)

# collect and print basic information about a thread
post_count = bot.count_posts() # e.g., 24
activity_overview = bot.get_activity_overview()
print(post_count)
print(activity_overview)

# collect the first 5 posts in a thread
posts = bot.get_posts(0, 5)
for post in posts:
    print(post)

# make a post in the thread that replies to the first post 
post_content = f"[quote]{posts[0]['content']}[/quote] wow very interesting"
bot.make_post(post_content)

# then edit the post
new_content = f"{post_content} and also very cool"
bot.edit_post(post_count+1, new_content)
```

For more flexibility and control, power users can instead import functions from the `donbot.operations` submodule to operate on `request.Session` objects directly. Every operation supported by the Donbot class is implemented as a function in this submodule, and takes a `requests.Session` object as its first argument, and sometimes other arguments that the Donbot class normally handles for you. This allows for more fine-grained control over the requests being made, and can be useful for more complex workflows -- like if you were scraping lots of data from the site using a framework like `scrapy` or `beautifulsoup`. We de-emphasize this approach in our documentation, but will frequently prefer it in downstream projects.

## Implemented Workflows 🛠️

In addition to supporting the basic usage, the library also aims to support a range of more complex but particularly common workflows that are common across mafia games.

These will be listed here as they are implemented (and validated).

## Installation 📦

Donbot is available on PyPI, so you can install it with pip:

```bash
pip install donbot
```