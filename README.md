# Modbot
automating the more trivial activities a game moderator does on mafiascum.net, and other stuff sprouting from that effort

##  Organization
The repository should ultimately be divided into directories based on discrete problem domains. Work belongs in the same problem domain as other work if 1) they both address similar problems, 2) they address different problems in very similar ways, 3) it is impossible or impractical to separate the solution of one problem from the solution of another, etc. 

Examples of work in the same problem domain is work aimed at automating collecting posts from MS.net and work automating making posts to MS.net (both mostly involve sequencing HTTP requests). Examples of work in separate problem domains might be work aimed at automating making posts to MS.net and work aimed at automating deriving votecounts from posts (one mostly involves sequencing HTTP requests while the other mostly involves string processing).

Directories established in repository so far:
### Donbot
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

[Tutorial / Documentation](donbot/donbotdemo.ipynb)
[Details of Module](donbot/donbot.ipynb)
[Module](donbot/donbot.py)
