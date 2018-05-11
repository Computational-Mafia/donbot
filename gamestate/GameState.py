import json

from Modifier import Modifiable
from Player import Player
from User import User
from Election import Election, ElectionType
from Phase import Phase, PhaseType
from Event import Event
from Component import Component


def load_json_file(filename):
    try:
        with open(filename, mode='rt') as events_file:
            raw_json = events_file.read()
            result = json.loads(raw_json)
    except FileNotFoundError:
        print('File {0} not found.'.format(filename))
        return None
    return result


class GameState(Modifiable):
    def __init__(self, name):
        Modifiable.__init__(self)
        self.name = name
        self.type = None
        # This flag is True when no events have been processed against this game state
        self.pristine = True
        self.mods = list()
        self.post = 0
        self.players = list()
        self.log = list()
        self.phase_types = list()
        self.phases = list()
        self.election_types = list()
        self.elections = list()
        self.endgame = False
        self.load_setup(filename='_defaults.setup.json')
        self.load_setup()
        self.phases.append(self.get_phase_type('Pregame').new(self.post))

    def __str__(self):
        return '<GameState: ' + self.name + '>'

    def load_setup(self, filename=None):
        if not filename:
            filename = self.name + '.setup.json'
        setup = load_json_file('setups/' + filename)
        if not setup:
            return
        self.type = setup.get('type', 'Unknown')
        for mod in setup['mods']:
            self.add_mod(mod["name"], mod["aliases"])
        for player in setup['players']:
            self.add_player(Player.make_from_json(self.post, player))
        for phase_type in setup.get('phase_types', []):
            self.add_phase_type(PhaseType.make_from_json(self.post, phase_type))
        for election_type in setup.get('election_types', []):
            self.add_election_type(ElectionType.make_from_json(self.post, election_type))
        if 'modifiers' in setup:
            self.set_modifiers(self.post, setup['modifiers'])

    def add_mod(self, name, aliases=list()):
        for mod in self.mods:
            if mod.display_name == name:
                # Don't add a mod who is already in the list.
                return
        self.mods.append(User(name, self.post, aliases=aliases))

    def add_player(self, player):
        self.players.append(player)

    def add_phase_type(self, phase_type):
        for existing_phase_type in self.phase_types:
            if existing_phase_type.name == phase_type.name:
                # Phase type already exists, so just set modifiers and elections
                existing_phase_type.elections = phase_type.elections
                existing_phase_type.set_modifiers(0, phase_type.modifiers)
                return
        self.phase_types.append(phase_type)

    def add_election_type(self, election_type):
        for existing_election_type in self.election_types:
            if existing_election_type.name == election_type.name:
                # Election type already exists, so just set modifiers
                existing_election_type.set_modifiers(0, election_type.modifiers)
                return
        self.election_types.append(election_type)

    # TODO - find way to get rid of this redundancy

    def active_phase(self, post=None):
        if post is None:
            post = self.post
        for phase in self.phases:
            if phase.active(post):
                return phase
        return None

    def active_elections(self, post=None):
        if post is None:
            post = self.post
        output = list()
        for election in self.elections:
            if election.active(post):
                output.append(election)
        return output

    def active_players(self, post=None):
        if post is None:
            post = self.post
        output = list()
        for player in self.players:
            if player.active(post):
                output.append(player)
        return output

    def living_players(self, post=None, dead=False):
        if post is None:
            post = self.post
        output = list()
        for player in self.active_players(post):
            if (player.get_modifier(post, 'alive') and not dead) or (not player.get_modifier(post, 'alive') and dead):
                output.append(player)
        return output

    def get_phase_type(self, name):
        for phase_type in self.phase_types:
            if phase_type.name == name:
                return phase_type
        return None

    def get_election_type(self, name):
        for election_type in self.election_types:
            if election_type.name == name:
                return election_type
        return None

    def advance_phase(self, phase_type=None):
        if not phase_type:
            # Use the phase progression to determine which phase comes next
            # The modulo logic ignores phases not in the progression, to maintain a cycle of phases
            # unaffected by 'extra' phases sprinkled in, or the pregame phase, etc.
            phase_progression = self.get_modifier(self.post, 'phase_progression')
            num_past = [phase for phase in self.phases if phase.phase_type.name in phase_progression
                        and phase.past(self.post)]
            phase_type = self.get_phase_type(phase_progression[len(num_past) % len(phase_progression)])
        else:
            phase_type = self.get_phase_type(phase_type)
        self.active_phase().set_end(self.post)
        self.phases.append(phase_type.new(self.post))
        # End elections that need to end on phase change
        for election in self.active_elections():
            if election.get_modifier(self.post, 'end_on_phase_change'):
                election.set_end(self.post)
        for election_type in phase_type.elections:
            self.add_election(self.get_election_type(election_type))

    def add_election(self, election_type):
        new_election = election_type.new(self.post, phase=self.active_phase())
        self.elections.append(new_election)
        if new_election.get_modifier(self.post, 'include_all_players'):
            for player in self.players:
                if player.get_modifier(self.post, 'alive'):
                    new_election.add_elector(self.post, player)

    def resolve_election(self, post, elector_names=None, election_type=None, election_name=None):
        # If we're given the name, find that election directly
        if election_name:
            for election in self.active_elections(post):
                if election.name == election_name:
                    return election
            # Specifying a name that doesn't exist should be presumed an error
            raise ValueError
        # Otherwise, make a list of active elections and narrow down using available information
        elections_list = self.active_elections(post)
        # Remove elections not matching election_type
        if election_type:
            for election in elections_list:
                if election.type != election_type:
                    elections_list.remove(election)
        # Remove elections where any provided electors can't be resolved
        if elector_names:
            for elector_name in elector_names:
                value_to_pass = self.resolve_player(post, elector_name)
                if not value_to_pass:
                    # We didn't find a player; assume this name refers to a non-player elector
                    value_to_pass = elector_name
                for election in elections_list:
                    if not election.get_elector(post, value_to_pass):
                        elections_list.remove(election)
        # If we narrowed down to one result, return it.
        # If we narrowed down to zero results, no elections meet the criteria; return None
        # Otherwise, there is ambiguity and we must raise an error
        if len(elections_list) == 1:
            return elections_list[0]
        elif len(elections_list) == 0:
            return None
        else:
            raise ValueError

    def resolve_player(self, post, name):
        players_list = self.active_players(post)
        for player in players_list:
            this_user = player.get_current_user(post)
            if this_user:
                if name in this_user.names():
                    return player
        return None


class Game:
    def __init__(self, name, style='_default'):
        self.name = name
        self.game_state = GameState(self.name)
        self.events = list()
        self.log = list()
        self.style = style

    def __str__(self):
        return '<Game: ' + self.name + '>'

    def load_events(self, filename=None):
        if not filename:
            filename = self.name + '.events.json'
        events = load_json_file('events/' + filename)
        if events:
            for event in events:
                self.events.append(Event.make_from_json(event))

    def load_event(self, event_json):
        self.events.append(Event.make_from_json(event_json))

    def process_events(self, force_reset=False):
        self._sort_events()
        unprocessed_events = [event for event in self.events if event.processed == False]
        if not unprocessed_events:
            return
        # Force a reset if:
        #   1) Processing an event before current game state post, assuming at least one event has been processed
        #   2) The optional flag is set
        #   (Is there a better way to handle the edge case of post 0 events than the pristine flag?)
        if force_reset or (unprocessed_events[1].post <= self.game_state.post and not self.game_state.pristine):
            # In this case, reset the game before processing
            self._reset()
            unprocessed_events = [event for event in self.events if event.processed is False]
        for event in unprocessed_events:
            self._process_event(event)

    def generate_vote_count(self, post=None, style=None):
        if post is None:
            post = self.game_state.post
        if style is None:
            style = self.style
        output = ''
        for election in self.game_state.active_elections(post):
            output += Component.create('vote_count', election=election, post=post, style=style).generate()
        return output

    def _reset(self):
        self.game_state = GameState(self.name)
        for event in self.events:
            event.processed = False

    def _process_event(self, event):
        event.execute(self.game_state)

    def _sort_events(self):
        self.events = sorted(self.events, key=lambda event: (event.post, event.PRIORITY))