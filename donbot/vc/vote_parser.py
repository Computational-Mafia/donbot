from lxml import html
from lxml.html import HtmlElement
from editdistance import eval as dist

tag_paths = [
    "/html/body/span[contains(@class, '{}')]",
    # "/html/body/p/span[contains(@class, '{}')]",
    # "/html/span/span[contains(@class, '{}')]",
]


def find_noboldsig_elements(post_html: HtmlElement):
    "Identify post content enclosed in noboldsig HTML tags"
    elements = []
    for path in tag_paths:
        elements.extend(post_html.xpath(path.format("noboldsig")))
    return elements


def find_bbvote_elements(post_html: HtmlElement):
    "Identify post content enclosed in vote HTML tags"
    bbvote_tag_paths = [path.format("bbvote") for path in tag_paths]
    return sum((post_html.xpath(path) for path in bbvote_tag_paths), [])


def find_broken_tag_elements(post_html: HtmlElement):
    "Identify post content enclosed in broken noboldsig or bbvote tags"
    return []


def find_votes(post_html: HtmlElement):
    "Extract text identifying the voted player from the content of a vote"
    matched_elements = (
        find_noboldsig_elements(post_html)
        + find_broken_tag_elements(post_html)
        + find_bbvote_elements(post_html)
    )
    for element in matched_elements:
        v = element.text_content().lstrip()
        # if v[:7].lower().count("vote") + v[:7].lower().count("veot") > 0:
        if v[:4].lower() == "vote":
            yield v[4:].replace(':', ' ').rstrip().lstrip()


def includes_vote(post_html: HtmlElement) -> bool:
    "Determine if post content includes a vote"
    return len(list(find_votes(post_html))) > 0


def find_players_contain_vote(vote, players):
    "Find votes that contain player name"
    return [players[p] for p in players if vote in p]

class VoteParser:
    def __init__(self, players):
        self.players = {p.lower():p for p in players}

    def from_post(self, post):
        post_html = html.fromstring("<html><body>" + post["content"] + "</body></html>")
        for vote in find_votes(post_html):
            yield self.find_voted(vote)

    def find_voted(self, vote):
        lowvote = vote.lower()

        substring_matches = find_players_contain_vote(lowvote, self.players)
        if len(substring_matches) == 1:
            return substring_matches[0]

        distances = {self.players[p]: dist(p, lowvote) for p in self.players}
        return min(distances, key=lambda x: distances[x])