from .vote_count import VoteCount
from .vote_parser import VoteParser


def get_players(slots: list[str]) -> list[str]:
    players = []
    for slot in slots:
        players.extend(slot)
    return players


class VoteCounter:
    def __init__(
        self,
        slots: list,
        events=None,
        lessOneForMislynch=False,
        doublevoters=None,
        flag_unmatched_votes=False,
    ):
        self.events = events or {}
        self.doublevoters = doublevoters or []
        self.slots = slots
        self.players = get_players(slots)

        self.vote_parser = VoteParser(self.players, flag_unmatched_votes)
        self.votecount = VoteCount(
            slots, lessOneForMislynch=lessOneForMislynch, doublevoters=doublevoters
        )

    @property
    def choice(self) -> str | list[str] | None:
        return self.votecount.choice

    def process_post(self, post_user: str, post_content: str, post_number: int):
        "Parse and update from events and any votes from a post."
        self.process_events(post_number)
        self.process_votes(post_user, post_content, post_number)

    def process_votes(self, post_user: str, post_content: str, post_number: int):
        "Parse and update from votes in a post."
        if not self.choice:
            if post_user not in self.players:
                return
            for voted in self.vote_parser.from_post(post_content):
                self.update_vote(post_user, voted, post_number)

    def process_events(self, post_number: int):
        "Parse and update from events tied to a post."
        if post_number not in self.events:
            return
        for event in self.events[post_number]:
            self.process_event(event, post_number)

    def process_event(self, event: str, post_number: int):
        "Parse and update from a single event tied to a post."
        if event.split(" ")[-1] == "killed":
            self.kill_player(event[: event.rfind(" ")], post_number)
        elif event.split(" ")[1] == "reset":
            if event.split(" ")[0].lower() == "votecount":
                self.reset_votecount(post_number)
            else:
                self.reset_player(event.split(" ")[0], post_number)
        elif " voted " in event:
            self.votecount.update(
                event.split(" voted ")[0], event.split(" voted ")[1], post_number
            )

    def kill_player(self, killed_player: str, post_number: int):
        "Kill a player relevant for the votecount"
        killed_slot = next(s for s in self.slots if s.count(killed_player) > 0)
        del self.slots[self.slots.index(killed_slot)]
        self.players = get_players(self.slots)
        self.votecount.kill_player(killed_player, post_number)
        self.vote_parser = VoteParser(self.players)

    def reset_player(self, reset_player: str, post_number: int):
        "Reset votes for a player"
        self.update_vote(reset_player, "UNVOTE", post_number)

    def reset_votecount(self, post_number: int):
        "Reset the votecount"
        for slot in self.slots:
            self.reset_player(slot[0], post_number)

    def update_vote(self, voter: str, voted: str, post_number: int):
        "Update a player's vote"
        self.votecount.update(voter, voted, post_number)
