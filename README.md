# Donbot: Automate Activities on Mafiascum.net 🤖🤵

Donbot is a Python library for automating activities on mafiascum.net. 

Forum-based mafia games are a popular form of social deduction game. Mafiascum.net is a popular forum for playing these games. Donbot is designed to make it easier to interact with the site programmatically. By having a pre-existing implementation of all the main ways to interact with the site, it should be easier for bot developers to focus on the logic of what they want done, rather than the minutiae of constructing valid requests and parsing the site's html.

For game moderators, the library can be used to automate the process of updating the game thread with votecounts, player lists, and other information. For players and researchers, the library can be used to automate the process of collecting and analyzing data from the site. Even outside of games, the tools can help manage complex threads or send mass PMs customized to each recipient.

**Please** don't use these functions haphazardly, especially those that make posts or send PMs, as misuse thereof can be against Site Rules, get you banned, and most importantly cause trouble for a lot of decent people.

## Implemented Utilities 📋

Using donbot, we've already automated a number of common workflows on mafiascum.net and host them in Google Colaboratory notebooks. These can be executed in the cloud without any setup, making them accessible even to people who don't write code. Just click the "Open in Colab" button next to a utility to get srated. Here's a table of what we have so far:

| Utility | Description  | Open in Colab | Notes |
| --- | --- | --- | --- |
| Youtube Playlist Extractor | Extracts YouTube video links from a thread and compiles them into a playlist | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Computational-Mafia/donbot/blob/f288643e18552e6768d7c7b4b9cfc943cdce61a5/examples/youtube_playlist_extraction/Youtube_Playlist_Extractor.ipynb) | Tested for threads with ~50 videos |
| Thread Scraping | Uses scrapy to download a thread's posts into a structured JSONL file | | See full example for multi-thread scraping! |

## Using the Library 🍲

Donbot is available on PyPI, so you can install it with pip:

```bash
pip install donbot-python
```

For most developers, it's most easy to get started by importing the `Donbot` class and initializing it with your account credentials -- ideally in a more secure way than hardcoding them into your script. You can either specify the thread you want to interact with when you initialize the bot (ideal when it's just that one thread), or specify it later when you call a function that requires it.

Check out `donbot/donbot.py` for a full list of available functions and their docstrings. Here's a basic demo of some of the things you can do with the library:

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

## Advanced Usage 🛠️

The donbot library is divided into two main parts: the `Donbot` class and the `operations` submodule. The `Donbot` class uses the `requests` library to make HTTP requests to the site and calls functions from the `donbot.operations` submodule to extract data and prepare actions on the site.

Power users comfortable with other libraries for making HTTP requests such as `scrapy` or `beautifulsoup` can sidestep the `Donbot` class and use functions in the `operations` submodule directly to streamline interactions with the site. This can be useful for tasks such as large-scale data collection or analysis, where the `requests` library may not be the best tool for the job.

Check out our examples directory for scripts that demonstrate the library's interopability with other libraries and its use in more complex workflows.