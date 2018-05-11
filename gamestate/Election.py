from math import ceil

from Modifier import Modifiable
from Temporal import Temporal
from Player import Player
from Elector import Elector
from Vote import Vote


class ElectionType(Modifiable):
    def __init__(self, name, modifiers=None):
        Modifiable.__init__(self)
        self.name = name
        if modifiers:
            self.set_modifiers(0, modifiers)

    def __str__(self):
        return '<ElectionType: ' + self.name + '>'

    # Make from a JSON object
    @staticmethod
    def make_from_json(post, json):
        if isinstance(json, dict):
            return ElectionType(**json)
        else:
            # Other types not supported
            raise TypeError

    def new(self, post, phase=None):
        new_election = Election(self.name, post, election_type=self, phase=phase)
        new_election.transfer_modifiers(post, self)
        return new_election


class Election(Temporal, Modifiable):
    def __init__(self, name, start, deadline=None, end=None, election_type=None, phase=None):
        Temporal.__init__(self, start, end)
        Modifiable.__init__(self)
        self.name = name
        self.deadline = deadline
        self.phase = phase
        self.electors = list()
        self.votes = list()
        self.modifiers = list()
        self.type = election_type
        self.vote_counts = list()

    def __str__(self):
        return '<Election: ' + self.name + '>'

    def active_electors(self, post):
        return [elector for elector in self.electors if elector.active(post)]

    def active_voters(self, post):
        # Returns the list of players who can potentially vote
        return [voter for voter in self.active_electors(post) if voter.get_modifier(post, 'can_vote')]

    def active_votees(self, post):
        # Returns the list of players who can potentially be voted
        return [votee for votee in self.active_electors(post) if votee.get_modifier(post, 'can_be_voted')]

    def not_voting(self, post):
        return [elector for elector in self.active_electors(post) if elector not in
                [vote.voter for vote in self.active_votes_by_voter(post, elector)]]

    def get_elector(self, post, player):
        if isinstance(player, Player):
            for elector in self.active_electors(post):
                if elector.player == player:
                    return elector
        else:
            for elector in self.active_electors(post):
                if elector.matches_name(post, player):
                    return elector
        return None

    def add_elector(self, start, player, end=None):
        if self.get_elector(start, player):
            return
        else:
            self.electors.append(Elector(start, player, end))

    def remove_elector(self, post, player):
        elector = self.get_elector(post, player)
        if not elector:
            # Could not resolve elector; might implement something for this later
            raise NotImplementedError
        # End all votes associated with this elector
        for vote in self.active_votes_by_voter(post, elector):
            vote.set_end(post)
        for vote in self.active_votes_by_votee(post, elector):
            vote.set_end(post)
        # Set the end of the elector object
        elector.set_end(post)

    def active_votes(self, post):
        return [vote for vote in self.votes if vote.active(post)]

    def active_votes_by_voter(self, post, voter_elector):
        return [vote for vote in self.active_votes(post) if vote.voter == voter_elector]

    def active_votes_by_votee(self, post, votee_elector):
        return [vote for vote in self.active_votes(post) if vote.votee == votee_elector]

    def num_votes_for_player(self, post, votee_elector):
        total = 0
        for vote in self.active_votes_by_votee(post, votee_elector):
            total += vote.power
        return total

    def _is_voting_for(self, post, voter_elector, votee_elector):
        for vote in self.active_votes_by_voter(post, voter_elector):
            if vote.votee == votee_elector:
                return True
        return False

    def threshold(self, post):
        threshold = 0
        criterion = self.get_modifier(post, 'threshold_criterion')
        if not criterion or criterion == 'voters':
            # Lynch threshold is based on number of voters
            threshold = ceil((len(self.active_voters(post)) + 1) / 2)
        elif criterion == 'votes':
            # Lynch threshold is based on the number of votes in play
            raise NotImplementedError
        else:  # Unknown criterion
            raise NotImplementedError
        threshold_modifier = self.get_modifier(post, 'threshold_modifier')
        if threshold_modifier:
            threshold += threshold_modifier
        return threshold

    def vote(self, post, voter, votee, power=None):
        result = False
        voter_elector = self.get_elector(post, voter)
        votee_elector = self.get_elector(post, votee)
        if (not voter_elector) or (not votee_elector):
            # Couldn't resolve one of the two players; might implement something for this later
            raise NotImplementedError
        if (not voter_elector.get_modifier(post, 'can_vote')) or (not votee_elector.get_modifier(post, 'can_be_voted')):
            # Either the voter can't vote or the votee can't be voted; return
            return result
        if power is None:
            # Power wasn't specified, so use the voter's power
            power = voter_elector.get_modifier(post, 'vote_power')
        current_votes = self.active_votes_by_voter(post, voter_elector)
        if self._is_voting_for(post, voter_elector, votee_elector):
            if not voter_elector.get_modifier(post, 'multiple_simultaneous_votes_on_one_player'):
                # We can't vote the same target multiple times; return
                return result
        if len(current_votes) >= voter_elector.get_modifier(post, 'maximum_simultaneous_votes'):
            # We are at our vote cap; see if we can unvote
            if voter_elector.get_modifier(post, 'automatically_unvote'):
                unvote_result = self.unvote(post, voter, avoid_removing=votee_elector)
                if unvote_result:
                    # Place the vote if the unvote succeeded.
                    self.votes.append(Vote(voter_elector, votee_elector, post, power=power))
                    result = True
        else:
            # We are not at our vote cap; just place the vote
            self.votes.append(Vote(voter_elector, votee_elector, post, power=power))
            result = True
        return result

    def unvote(self, post, voter, votee=None, avoid_removing=None):
        result = False
        voter_elector = self.get_elector(post, voter)
        votee_elector = self.get_elector(post, votee)
        if (not voter_elector) or (votee and not votee_elector):
            # Couldn't resolve one of the two players; might implement something for this later
            raise NotImplementedError
        if not voter_elector.get_modifier(post, 'can_unvote'):
            # The voter is incapable of unvoting; return
            return False
        ordered_votes = sorted(self.active_votes_by_voter(post, voter_elector), key=lambda vote: vote.start)
        if votee_elector:
            # If a votee was specified, narrow down to only votes for that votee
            ordered_votes = [vote for vote in ordered_votes if vote.votee == votee_elector]
        if avoid_removing:
            # Don't unvote the 'avoid_removing' elector; this is used if we are voting for the same elector
            # 'avoid_removing' is only used internally and is guaranteed to be a valid elector
            ordered_votes = [vote for vote in ordered_votes if vote.votee != avoid_removing]
        if not ordered_votes:
            # There aren't any votes so we're done
            return False
        for vote in ordered_votes:
            vote.set_end(post)
            result = True
            if not voter_elector.get_modifier(post, 'unvote_removes_all_votes'):
                return result
        return result

    def check_for_lynch(self, post):
        threshold = self.threshold(post)
        for votee in self.active_votees(post):
            votee_threshold = threshold
            threshold_modifier = votee.get_modifier(post, 'threshold_modifier')
            if threshold_modifier:
                votee_threshold += threshold_modifier
            if self.num_votes_for_player(post, votee) >= votee_threshold:
                return True
        return False
