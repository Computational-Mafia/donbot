class Event:

    def __init__(self, post, **kwargs):
        self.post = post
        self.processed = False
        self.params = kwargs

    def __str__(self):
            return '<' + str(self.__class__) + '>'

    # Make from a JSON object
    @staticmethod
    def make_from_json(json):
        for event_type in EVENT_TYPES:
            if event_type.TYPE == json['type']:
                json.pop('type')
                return event_type(**json)
        raise TypeError

    def execute(self, game_state):
        game_state.post = self.post
        game_state.pristine = False


class VoteEvent(Event):
    """
    VoteEvent
    Represents an elector voting for another elector in an election;
    in most circumstances, this is a player voting to lynch another player (or No Lynch).

    Required Parameters:
        voter: the name of the elector casting the vote.
        votee: the name of the player being voted for.

    Optional Parameters:
        election_type: the type of the election the vote is intended for; useful when there are multiple elections.
        election_name: the name of the election the vote is intended for; also useful for multiple elections.
    """

    PRIORITY = 2.1
    TYPE = 'vote'

    def execute(self, game_state):
        super().execute(game_state)
        # Event requires voter and votee at minimum
        if 'voter' not in self.params or 'votee' not in self.params:
            raise ValueError
        elector_names = [self.params['voter'], self.params['votee']]
        election = game_state.resolve_election(game_state.post, elector_names=elector_names,
                                               election_type=self.params.get('election_type', None),
                                               election_name=self.params.get('election_name', None))
        if not election:
            # Failed to resolve election
            raise EventExecutionException
        election.vote(game_state.post, self.params['voter'], self.params['votee'])


class UnvoteEvent(Event):
    """
    UnvoteEvent
    Represents an elector rescinding their current vote in an election.

    Required Parameters:
        voter: the name of the player who is rescinding their vote.

    Optional Parameters:
        votee: the name of the player who is no longer being voted; handy if multiple simultaneous votes are allowed.
        election_type: the type of the election the vote is intended for; useful when there are multiple elections.
        election_name: the name of the election the vote is intended for; also useful for multiple elections.
    """

    PRIORITY = 2
    TYPE = 'unvote'

    def execute(self, game_state):
        super().execute(game_state)
        # Event requires voter at minimum
        if 'voter' not in self.params:
            raise ValueError
        elector_names = [self.params['voter']]
        # The votee is not required, but include in elector_names if it's present
        if 'votee' in self.params:
            elector_names.append(self.params['votee'])
        election = game_state.resolve_election(game_state.post, elector_names=elector_names,
                                               election_type=self.params.get('election_type', None),
                                               election_name=self.params.get('election_name', None))
        if not election:
            # Failed to resolve election
            raise EventExecutionException
        election.unvote(game_state.post, self.params['voter'], self.params.get('votee', None))


class EnterEvent(Event):

    PRIORITY = 1
    TYPE = 'add_player'

    def execute(self, game_state):
        raise NotImplementedError


class DeathEvent(Event):
    """
    DeathEvent
    Represents a player dying for whatever reason (night kill, modkill, lynch, etc.).

    Required Parameters:
        deceased: the name of the player kicking the bucket

    Optional Parameters:
        flavor: the death flavor, which should be written to replace the word 'died' in the player's flip
    """

    PRIORITY = 4
    TYPE = 'death'

    def execute(self, game_state):
        super().execute(game_state)
        # Event requires deceased at minimum
        if 'deceased' not in self.params:
            raise ValueError
        for election in game_state.active_elections():
            if election.get_elector(game_state.post, self.params['deceased']):
                election.remove_elector(game_state.post, self.params['deceased'])
        deceased = game_state.resolve_player(game_state.post, self.params['deceased'])
        if not deceased:
            # Failed to resolve player
            raise EventExecutionException
        if 'flavor' in self.params:
            deceased.set_modifier(game_state.post, 'death_flavor', self.params['flavor'])
        deceased.set_modifier(game_state.post, 'alive', False)


class DeadlineEvent(Event):
    """
    DeadlineEvent
    Represents a deadline being set or adjusted, for the active phase, election(s), or in general.
    The deadline is presumed to apply to active elections if any exist; otherwise, it will apply to the active phase.

    Required Parameters:
        deadline: the deadline being set, in ISO 8601 format.

    Optional Parameters:
        election: if supplied, the deadline will apply to this election only.
        phase: if set True, the deadline will apply to the active phase even if there are active elections.
    """

    PRIORITY = 10
    TYPE = 'deadline'

    def execute(self, game_state):
        super().execute(game_state)
        if 'deadline' not in self.params:
            raise ValueError
        if game_state.active_elections() and not self.params.get('phase', False):
            for election in game_state.active_elections():
                if 'election' in self.params:
                    if election.name == self.params['election']:
                        election.deadline = self.params['deadline']
                else:
                    election.deadline = self.params['deadline']
        else:
            game_state.active_phase().deadline = self.params['deadline']


class VoteCountEvent(Event):
    """
    VoteCountEvent
    Represents a vote count being generated and posted for an election.
    This is used to allow vote counts to link back to old vote counts, or for the OP to contain links to vote counts.

    Required Parameters:
        None

    Optional Parameters:
        election_type: the type of the election getting a vote count; useful when there are multiple elections.
        election_name: the name of the election getting a vote count; also useful for multiple elections.
    """

    PRIORITY = 8
    TYPE = 'vote_count'

    def execute(self, game_state):
        super().execute(game_state)
        election = game_state.resolve_election(game_state.post, election_type=self.params.get('election_type', None),
                                               election_name=self.params.get('election_name', None))
        if not election:
            # Failed to resolve election
            raise EventExecutionException
        election.vote_counts.append(game_state.post)


class PhaseChangeEvent(Event):
    """
    PhaseChangeEvent
    Represents the game advancing to a new phase, such as day transitioning to night or vice-versa

    Required Parameters:
        None

    Optional Parameters:
        phase: the name of the phase to advance to. If omitted, the game's phase_progression modifier will be consulted
            to determine the next phase.
    """

    PRIORITY = 9
    TYPE = 'phase_change'

    def execute(self, game_state):
        super().execute(game_state)
        game_state.advance_phase(self.params.get('phase', None))


class ReplacementEvent(Event):
    """
    ReplacementEvent
    Represents a player replacing another player.

    Required Parameters:
        replacee: the name of the player who is being replaced.
        replacement_name: the name of the player who is replacing in.

    Optional Parameters:
        aliases: the aliases of the player who is replacing in (such as hydra heads).
    """

    PRIORITY = 3
    TYPE = 'replacement'

    def execute(self, game_state):
        super().execute(game_state)
        # Event requires replacee and replacement_name at minimum
        if 'replacee' not in self.params or 'replacement_name' not in self.params:
            raise ValueError
        replacee = game_state.resolve_player(game_state.post, self.params['replacee'])
        if not replacee:
            # Failed to resolve player
            raise EventExecutionException
        replacee.replace(self.params['replacement_name'], game_state.post, self.params.get('aliases', list()))


EVENT_TYPES = (VoteEvent, UnvoteEvent, EnterEvent, DeathEvent, DeadlineEvent, VoteCountEvent, PhaseChangeEvent,
               ReplacementEvent)


class EventExecutionException(Exception):
    pass