# Donbot
> automating the more trivial activities a game moderator does on mafiascum.net

## Description

The donbot module is a simple module w/ a class that makes it super easy to automate interactions with mafiascum.net.

Create an instance of the Donbot class with your username and password (and potentially other parameters), and you'll be able to:

- Collect a range of posts from a thread
- Make posts in a specified thread with specified content
- Send pms to a user with a specified subject and body
- Collect the number of posts in a specified thread
- Collect id matching a specified scummer's username
- And, eventually, more!

The target audience for this module is other developers. By having a pre-existing implementation of all the main ways to interact with the site, it should be easier for bot developers to focus on the logic of what they want their bot to do, rather than the minutiae of requesting and parsing the site's html.

**Please** don't use these functions haphazardly, especially those that make posts or send PMs, as misuse thereof can be against Site Rules, get you banned, and most importantly cause trouble for a lot of decent people.
