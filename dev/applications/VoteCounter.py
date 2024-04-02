
# coding: utf-8

# # Votecounter
# Includes Psyche's version of a VoteExtracter class for extracting votes from posts, and a set of helper functions and variables used to pull that off. These are discussed in detail at their location in the notebook.
# 
# Rather than being very strict about what counts as a vote (ie looking for proper vote formatting and exact target naming), this function is intended to work like human moderators do, or at least have over the D1s of ~300 Mini Normal Games studied to produce the function. The VoteExtractor class has been found to accurately predict which player a moderator assigned a lynch to across nearly all of these studied games - all without relying on any explicit database of aliases.
# 
# If aliases are *totally* necessary to understand the target of a vote (for example, when someone uses a user's true first name instead of some nickname based on their username), though, VoteExtracter is a bit more likely to fail. In order to include aliases in VoteExtracter functioning, add any desired aliases to the list of players included when you initialize an instance of the class. A cleaner option, though, might be to ban votes that require such contextual knowledge to interpret their target.
# 
# `votecounter.py` is produced by converting the front-facing notebook `votecounter.ipynb` using the jupyter command `jupyter nbconvert --to script votecounter.ipynb`.
# 
# This notebook/script was developed in work described in `votecounterdev.ipnyb` based on Mini Normal Archive data listed in `archive.txt`. The associated archive of posts associated with the listed games is too large to be uploaded to GitHub, but may be obtainable by scraping the data or contacting Psyche.

# ## Setup

# ### Dependencies

# In[2]:


from scrapy.selector import Selector # to help parse website content
import editdistance as ed  # to detect slight misspellings
import enchant             # spellchecker to help identify english words
import re                  # unfortunately reliant on regular expressions


# In[3]:


# list of spellchecker dictionaries relied on
dEn = enchant.Dict("en")
dCA = enchant.Dict("en_CA")
dGB = enchant.Dict("en_GB")
dUS = enchant.Dict("en_US")

# regex filters
regall = re.compile('[^a-zA-Z]') # any character that IS NOT a-z OR A-Z
regup = re.compile('[^A-Z]') # any character that IS NOT A-Z


# ## Helper Functions

# ### English Divides
# The function `englishdivides()` returns a list of ways the input playername can be divided into strings considered legal words by one of the spellchecker dictionaries, with the list sorted from least to greatest by number of divisions. The spellchecker often accepts as legal many single character and two-character strings that I wouldn't recognize as actual words, so this sorting is important. The result is a data structure helpful for predicting how users might abbreviate or otherwise fail to totally specify a player's name in their vote (eg, "FB" for "Firebringer"). 
# 
# Strangely, the full list is often sufficient for predicting errors/abbreviations of usernames that aren't even straightforward compositions of 'legal' english words. Maybe our english-langauge vocabularies play a role in structuring mistaken spellings of non-english language strings.

# In[4]:


# returns ways the string can be split into english words or letters, 
# ordered from least to most number of divisions
def englishdivides(playername):
    string = regall.sub('', playername) # filter non-letters
    passes = [[['']]]
    fulldivides = []
    while len(passes[-1]) > 0:
        passes.append([])
        for p in passes[-2]:
            for i in range(len(''.join(p))+1, len(string)+1):
                substring = string[len(''.join(p)):i]
                if (dEn.check(substring) or
                    dCA.check(substring) or
                    dGB.check(substring) or
                    dUS.check(substring)):
                    passes[-1].append(p + [substring])

                    if len(''.join(p + [substring])) == len(string):
                        fulldivides.append(p + [substring])
    return fulldivides


# ### Find Votes
# The function `findVotes()` locates/returns the votes in a post w/o attempting to identify the player voted. The problem of just telling when/where someone is *trying* to make a vote is itself pretty substantive, as users have access to a variety of ways of specifying votes, can misspell "vote", accidentally use broken tags, or attempt fancy formatting of their votes besides simple `[b][/b]` or `[vote][/vote]` structures. Votes can also often be broken up into multiple lines or otherwise made remote from the naming of a vote's target.
# 
# This function handles all these issues in a way that mimics how actual moderators have almost always behaved across the 300 Mini Normal Games studied to develop this module.

# In[6]:


# locates/returns the votes in a post w/o identifying the player voted
def findVotes(post):
    "Returns list of votes present in the posts content"
    sel = Selector(text=post['content'])
    
    # pull out all relevant tags
    boldtags = (
        [each.extract() for each in 
         sel.xpath('/html/body/p/span[@class="noboldsig"]//text()')] +
        [each.extract() for each in 
         sel.xpath('/html/body/span[@class="noboldsig"]//text()')] +
        [each.extract() for each in 
         sel.xpath(
             '/html/body/p/span/span[@class="noboldsig"]//text()')] +
        [each.extract() for each in 
         sel.xpath('/html/body/span/span[@class="noboldsig"]//text()')] +
        [''.join(each.xpath('span//text()').extract()) for each in
         sel.xpath('/html/body/p/span[@class="noboldsig"]')] +
        [''.join(each.xpath('span//text()').extract()) for each in
         sel.xpath('/html/body/span[@class="noboldsig"]')])
    
    votetags = (
        [each.extract() for each in 
         sel.xpath('/html/body/p/span[@class="bbvote"]//text()')] +
        [each.extract() for each in
         sel.xpath('/html/body/span[@class="bbvote"]//text()')] + 
        [each.extract() for each in
         sel.xpath('/html/body/p/span/span[@class="bbvote"]//text()')] +
        [each.extract() for each in
         sel.xpath('/html/body/span/span[@class="bbvote"]//text()')] +
        [''.join(each.xpath('span//text()').extract()) for each in
         sel.xpath('/html/body/p/span[@class="bbvote"]')] +
        [''.join(each.xpath('span//text()').extract()) for each in
         sel.xpath('/html/body/span[@class="bbvote"]')])
    
    # first of all, though,
    # we handle broken bold tags similarly 
    # after some preprocessing, so let's add those
    for content in (sel.xpath('/html/body/text()').extract() +
                    sel.xpath('/html/body/p/text()').extract()):
        if content.count('[/b]') > 0:
            tagline = content[:content.find(
                '[/b]')].lstrip().rstrip() # up to broken tag
            boldtags.append(tagline)
        if content.count('[b]') > 0:
            tagline = content[content.find(
                '[b]')+3:].lstrip().rstrip() # starting at broken tag
            boldtags.append(tagline)
    
    # we want votetags to have priority, so add them to the pool here
    boldtags = boldtags + votetags 
    boldtags = [b.rstrip().lstrip() for b in boldtags]
    
    # they need to have 'vote' or 'veot' early in their string
    boldtags = [b for b in boldtags if b[:7].lower().count('vote')
                + b[:7].lower().count('veot') > 0]
    
    # rfind 'vote' and 'unvote' (and key mispellings) to locate vote
    for i, v in enumerate(boldtags):
        voteloc = max(v.lower().rfind('vote'), v.lower().rfind('veot'))
        unvoteloc = max(
            v.lower().rfind('unvote'), v.lower().rfind('unveot'))
        
        # if position of unvote is position of vote - 2, 
        # then the last vote is an unvote
        if unvoteloc > -1 and unvoteloc == voteloc - 2:
            boldtags[i] = 'UNVOTE'
            
        # otherwise vote is immediately after 'vote' text 
        # and perhaps some other stuff that must be stripped away
        else:
            boldtags[i] = (
                v[voteloc+4:].replace(': ', ' ').replace(
                    ':', ' ').replace('\n', ' ').rstrip().lstrip())

    votes = boldtags
    return votes

def includesVote(post):
    """Returns whether a vote is present in the post's content or not"""
    return len(findVotes(post)) > 0


# ## The VoteExtracter Class
# Initialized with a playerlist to avoid redundant processing, includes a function that uses a series of text processing tricks to match votes found with the findVotes() function to a member of said playerlist. Rather than being very strict about what counts as a vote (ie looking for proper vote formatting and exact target naming), this function is intended to work like human moderators do, or at least have over the D1s of ~300 Mini Normal Games studied to produce the function. The VoteExtractor class has been found to accurately predict which player a moderator assigned a lynch to across nearly all of these studied games.

# In[ ]:


class VoteExtracter:
    def __init__(self, players):
        
        # make an acronym dictionary for each player
        self.playerabbrevs, self.players = {}, players
        self.lowplayers = {p.lower():p for p in players}
        for p in players:
            self.playerabbrevs[p] =             ''.join([each[0] for each in englishdivides(p)[0][1:]])

    def fromPost(self, post):
        """tries to identify vote's target from the post"""

        votes = findVotes(post)

        # yield a list of votes in a post and process them all 'in order'
        # with the exception of same-line unvote-then-vote happenings
        for vote in votes:
            
            # pre-computation of values i'll need repeatedly
            lowvote = vote.lower()
            distances = {self.lowplayers[p]:ed.eval(p, lowvote)
                         for p in self.lowplayers}

            if vote == 'UNVOTE':
                yield 'UNVOTE'
                continue

            # make sure player isn't asking for a votecount
            if (lowvote[:5] == 'count' and
                len([p for p in self.lowplayers if p[:5]=='count'])==0):
                    continue

            # first check if vote is a 0char misspelling of a playername
            nearspellings = [d for d in distances if distances[d] <= 0]
            if len(nearspellings) == 1:
                yield nearspellings[0]
                continue

            # second check if vote is a 1char misspelling of a playername
            nearspellings = [d for d in distances if distances[d] <= 1]
            if len(nearspellings) == 1:
                yield nearspellings[0]
                continue

            # third check if the acronym from the capitalizations in 
            # the vote match the same in a playername
            capmatches = [p for p in self.players if
                          ed.eval(regup.sub('', p).lower(),
                                  regall.sub('', lowvote)) <= 0]
            if len(capmatches) == 1:
                yield capmatches[0]
                continue

            # fourth try to directly infer acronym from english divides
            acromatches = [p for p in self.players if 
                           ed.eval(self.playerabbrevs[p].lower(),
                                   regall.sub('', vote).lower()) <= 0]
            if len(acromatches) == 1:
                yield acromatches[0]
                continue

            # fifth check if vote w/ len >=3 is substring of a playername
            suboccurrences = [p for p in self.lowplayers
                              if p.count(lowvote) > 0 and len(vote) >= 3]
            if len(suboccurrences) == 1:
                yield self.lowplayers[suboccurrences[0]]
                continue

            # 6th check if vote's shortest english-word acronym of a name
            # with levenshtein distance threshold ranging up to 1;
            acromatches = [p for p in self.players if ed.eval(
                self.playerabbrevs[p].lower(),lowvote) <= 1]
            if len(acromatches) == 1:
                yield acromatches[0]
                continue

            # 7th check if vote is at all a substring of a playername
            suboccurrences = [p for p in self.lowplayers
                              if p.count(lowvote) > 0]
            if len(suboccurrences) == 1:
                yield self.lowplayers[suboccurrences[0]]
                continue

            # 8th check if vote is two char misspelling of a playername
            nearspellings = [d for d in distances if distances[d] <= 2]
            if len(nearspellings) == 1:
                yield nearspellings[0]
                continue

            # 9th check if vote has same capital letters as a playername
            # not caring about order
            capmatches = [p for p in self.players
                          if sorted(regup.sub('', p).lower())
                          == sorted(lowvote)]
            if len(capmatches) == 1:
                yield capmatches[0]
                continue

            # 10 check if vote's shortest english-word acronym of a name
            # with levenshtein distance threshold ranging up to 2
            acromatches = [p for p in self.players if ed.eval(
                self.playerabbrevs[p].lower(),lowvote) <= 2]
            if len(acromatches) == 1:
                yield acromatches[0]
                continue

            # 11 check if a player's name is a substring of the vote
            suboccurrences = [p for p in self.lowplayers
                              if lowvote.count(p) > 0]
            if len(suboccurrences) == 1:
                yield self.lowplayers[suboccurrences[0]]
                continue

            # 12 if any splitted part of a playername are vote substring
            suboccurrences = [p for p in self.lowplayers if
                              len([s for s in p.split(' ')
                                   if lowvote.count(s)> 0]) > 0]
            if len(suboccurrences) == 1:
                yield self.lowplayers[suboccurrences[0]]
                continue

            # 13 if any length>3 english-divided parts of a player's name
            # are a vote substring
            suboccurrences = [p for p in self.players
                              if len([s for s in englishdivides(p)[0]
                                      if (lowvote.count(s.lower())
                                          > 0 and len(s) > 3)]) > 0]
            if len(suboccurrences) == 1:
                yield suboccurrences[0]
                continue

            # 14 if vote is a two letter abbreviation of a playername
            # that includes partial english
            acromatches = [p for p in self.players
                           if ed.eval(''.join([each[0] for each in
                                englishdivides(p)[0][1:3]]).lower(),
                                      lowvote) <= 0]
            if len(acromatches) == 1:
                yield acromatches[0]
                continue

            # 15 if vote is slightly misspelled substring of a playername
            threshold = 1
            suboccurrences = []
            for p in self.lowplayers:
                if len(vote) < len(p):
                    for i in range(len(p)):
                        if (ed.eval(lowvote,
                                    p[i:min(i+len(vote)+1, len(p))])
                            <= threshold):
                            suboccurrences.append(p)
                            break
                    for i in range(1, len(vote)+1):
                        if (ed.eval(lowvote, p[:i]) <= threshold):
                            suboccurrences.append(p)
                            break
            if len(suboccurrences) == 1:
                yield self.lowplayers[suboccurrences[0]]
                continue

            # 16 retry 15 with higher threshold
            threshold = 2
            suboccurrences = []
            for p in self.lowplayers:
                if len(vote) < len(p):
                    for i in range(len(p)):
                        if (ed.eval(lowvote,
                                    p[i:min(i+len(vote)+1, len(p))])
                            <= threshold):
                            suboccurrences.append(p)
                            break
                    for i in range(1, len(vote)+1):
                        if (ed.eval(lowvote, p[:i]) <= threshold):
                            suboccurrences.append(p)
                            break
            if len(suboccurrences) == 1:
                yield self.lowplayers[suboccurrences[0]]
                continue

            # 17 if vote is mix of abbreviations/spaced playername parts
            suboccurrences = []
            for p in self.players:
                broke = p.split(' ')
                for i in range(len(broke)):
                    cand = ''.join([broke[j][0] if j != i else broke[j]
                                    for j in range(len(broke))])
                    if ed.eval(cand.lower(), lowvote) < 2:
                        suboccurrences.append(p)
            if len(suboccurrences) == 1:
                yield suboccurrences[0]
                continue

            # 18 if every char in vote is char in just one playername
            matches = [p for p in self.lowplayers 
                       if set(lowvote) <= set(p)]
            if len(matches) == 1:
                yield self.lowplayers[matches[0]]
                continue

            # 19 the last resort, the playername closest to the vote
            yield min(distances, key=distances.get)