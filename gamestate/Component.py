from re import findall
import json


ERROR_STRING = '### ERROR: {0} ###'


def load_config_file(filename):
    try:
        with open(filename, mode='rt') as config_file:
            raw_json = config_file.read()
            result = json.loads(raw_json)
    except FileNotFoundError:
        return None
    return result


class Component:
    TYPE = None
    PREREQS = []
    BODY = None

    def __init__(self, **kwargs):
        self.params = kwargs
        # Pull parameters from the component's default configuration file
        filename = 'styles/_default/' + self.TYPE + '.component.configs.json'
        configs = load_config_file(filename)
        if configs:
            self.params.update(configs)
        # And from the style's configuration file, if present
        if 'style' in self.params:
            filename = 'styles/' + self.params['style'] + '/' + self.TYPE + '.component.configs.json'
            configs = load_config_file(filename)
            if configs:
                self.params.update(configs)
        self.parts = dict()

    def generate(self):
        try:
            self._validate()
            self._get_parts()
            output = self._body().format(**self.parts)
        except ComponentGenerationException as e:
            return ERROR_STRING.format(str(e))
        return output

    def _validate(self):
        # Makes sure that all prerequisite values are supplied
        for prerequisite in self.PREREQS:
            if prerequisite not in self.params:
                raise ComponentGenerationException('Attempted to generate component of type"' + self.TYPE
                                                   + '" without required component "' + prerequisite + '".')

    def _get_parts(self):
        # Find parts that match a subcomponent type, and generate the appropriate subcomponent
        labels = findall(r'{(\w+)}', self._body())
        for label in labels:
            if label in [component.TYPE for component in COMPONENT_TYPES] and label not in self.parts:
                # No infinite recursion
                if label != self.TYPE:
                    self.parts[label] = self._subcomponent(label).generate()

    def _body(self):
        # Attempt to get the body for the specified style first
        filename = 'styles/' + self.params.get('style', '_default') + '/' + self.TYPE + '.component.body'
        try:
            with open(filename, mode='rt') as body_file:
                result = body_file.read()
        except FileNotFoundError:
            # Fall back to the "_default" style
            filename = 'styles/_default/' + self.TYPE + '.component.body'
            try:
                with open(filename, mode='rt') as body_file:
                    result = body_file.read()
            except FileNotFoundError:
                # If we don't even have the default we're in trouble, but just return a blank
                return ''
        return result

    def _subcomponent(self, component_type, **kwargs):
        arguments = dict.copy(self.params)
        arguments.update(kwargs)
        return Component.create(component_type, **arguments)

    @staticmethod
    def create(component_type, **kwargs):
        for component_class in COMPONENT_TYPES:
            if component_class.TYPE == component_type:
                return component_class(**kwargs)


class VoteCountComponent(Component):

    TYPE = 'vote_count'
    PREREQS = ['election', 'post']

    def _get_parts(self):
        super()._get_parts()
        self.parts['title'] = self._subcomponent('vote_count_label', **self.params).generate()
        self.parts['flavor'] = 'placeholder'
        votees = list()
        if self.params.get('include_players_without_votes', False):
            # Include all players
            votees = self.params['election'].active_votees(self.params['post'])
        else:
            # Include only players with votes on them
            for votee in self.params['election'].active_votees(self.params['post']):
                if self.params['election'].num_votes_for_player(self.params['post'], votee) > 0:
                    votees.append(votee)
        votees = sorted(votees, key=lambda votee: votee.get_name(self.params['post']))
        votees = sorted(votees, key=lambda votee: self.params['election'].num_votes_for_player(self.params['post'],
                                                                                               votee), reverse=True)
        votees = [self._subcomponent('vote_count_votes', elector=votee) for votee in votees]
        self.parts['voters_list'] = self._subcomponent('list', list=votees, delimiter='\n').generate()
        self.parts['not_voting_list'] = self._subcomponent('vote_count_votes', elector=None).generate()
        self.parts['active_voters'] = len(self.params['election'].active_voters(self.params['post']))
        self.parts['active_votees'] = len(self.params['election'].active_votees(self.params['post']))
        self.parts['threshold'] = self.params['election'].threshold(self.params['post'])
        self.parts['deadline'] = '[countdown]' + self.params['election'].deadline + '[/countdown]'
        self.parts['phase_name'] = self.params['election'].phase.name
        past_vote_counts = [self._subcomponent('vote_count_label', post=vc) for vc
                            in self.params['election'].vote_counts if vc < self.params['post']]
        self.parts['past_vote_counts'] = self._subcomponent('list', list=past_vote_counts, delimiter=' - ').generate()


class VoteCountLabelComponent(Component):

    TYPE = 'vote_count_label'
    PREREQS = ['election', 'post']

    def _get_parts(self):
        super()._get_parts()
        self.parts['phase_number'] = self.params['election'].phase.number
        self.parts['vote_count_number'] = len([vc for vc in self.params['election'].vote_counts
                                          if vc < self.params['post']]) + 1


class VoteCountVotesComponent(Component):

    TYPE = 'vote_count_votes'
    PREREQS = ['election', 'elector', 'post']

    def _get_parts(self):
        super()._get_parts()
        voters = list()
        if self.params['elector']:
            # Get the votes for the elector
            votee = self.params['elector'].get_player()
            if not isinstance(votee, str):
                # It's a player, so create a subcomponent to represent it
                votee = self._subcomponent('player_label', player=votee).generate()
            num_votes = self.params['election'].num_votes_for_player(self.params['post'],
                                                                     self.params['elector'])
            # Generate the list of voters
            for vote in sorted(self.params['election'].active_votes_by_votee(self.params['post'],
                                                                             self.params['elector']),
                               key=lambda post: post.start):
                voters.append(self._subcomponent('vote', vote=vote))
        else:
            # Get the players who are not voting
            votee = self.params.get('not_voting_label', 'Not Voting')
            not_voting = self.params['election'].not_voting(self.params['post'])
            num_votes = len(not_voting)
            for elector in sorted(not_voting, key=lambda elector: elector.get_name(self.params['post'])):
                voters.append(elector.get_name(self.params['post']))
        self.parts['votee'] = votee
        self.parts['num_votes'] = num_votes
        self.parts['votes_list'] = self._subcomponent('list', list=voters, delimiter=', ').generate()


class VoteComponent(Component):

    TYPE = 'vote'
    PREREQS = ['vote', 'post']

    def _get_parts(self):
        super()._get_parts()
        # Get the voter's name
        voter = self.params['vote'].voter.get_player()
        if not isinstance(voter, str):
            # It's a Player, so create a subcomponent to represent it
            self.parts['voter'] = self._subcomponent('player_label', player=voter, post=self.params['post']).generate()
        else:
            self.parts['voter'] = voter
        # Get the votee's name
        votee = self.params['vote'].votee.get_player()
        if not isinstance(votee, str):
            # It's a Player, so create a subcomponent to represent it
            self.parts['votee'] = self._subcomponent('player_label', player=votee, post=self.params['post']).generate()
        else:
            self.parts['votee'] = votee
        # Get the vote power, if needed
        if self.params.get('min_power_to_show', 0) <= self.params['vote'].power:
            power = self.params.get('vote_power_header', '') + str(self.params['vote'].power) \
                    + self.params.get('vote_power_footer', '')
            self.parts['vote_power'] = power
        else:
            self.parts['vote_power'] = ''


class PlayersListComponent(Component):

    TYPE = 'players_list'
    PREREQS = ['game_state', 'post']

    def _get_parts(self):
        super()._get_parts()
        if self.params.get('filter', '') == 'living':
            source_list = self.params['game_state'].living_players(self.params['post'])
        elif self.params.get('filter', '') == 'dead':
            source_list = self.params['game_state'].living_players(self.params['post'], dead=True)
        elif self.params.get('filter', '') == 'modkilled':
            source_list = self.params['game_state'].living_players(self.params['post'], dead=True)
            new_list = list()
            for item in source_list:
                if item.get_modifier(self.params['post'], 'flavor') == 'modkilled':
                    new_list.append(item)
            source_list = new_list
        else:
            source_list = self.params['game_state'].active_players(self.params['post'])
        players_list = [self._subcomponent('player_label', player=player, post=self.params['post'])
                        for player in source_list]
        self.parts['players'] = self._subcomponent('list', list=players_list, delimiter='\n').generate()


class PlayerLabelComponent(Component):

    TYPE = 'player_label'
    PREREQS = ['player', 'post']

    def _get_parts(self):
        super()._get_parts()
        replacees = list()
        if self.params.get('include_replacements', False):
            for replacee in self.params['player'].users:
                if replacee.end is not None and replacee.end <= self.params['post']:
                    replacees.append(self._subcomponent('player_replacee', user=replacee))
            replacees.reverse()
        self.parts['replacees'] = self._subcomponent('list', list=replacees, delimiter='').generate()
        self.parts['player_name'] = self.params['player'].get_current_user(self.params['post']).display_name


class PlayerReplaceeComponent(Component):

    TYPE = 'player_replacee'
    PREREQS = ['user']

    def _get_parts(self):
        super()._get_parts()
        self.parts['replacee_name'] = self.params['user'].display_name
        self.parts['replace_post'] = self.params['user'].end

class ListComponent(Component):

    TYPE = 'list'
    PREREQS = ['list', 'delimiter']

    def _get_parts(self):
        super()._get_parts()
        num = 0
        for item in self.params['list']:
            # Check for the possibility that an item in the list is a subcomponent
            if isinstance(item, Component):
                item = item.generate()
            self.parts['key' + str(num)] = item
            num += 1


    def _label_generator(self):
        for x in range(len(self.params['list'])):
            yield '{key' + str(x) + '}'

    def _body(self):
        return self.params['delimiter'].join(self._label_generator())


COMPONENT_TYPES = (VoteCountComponent, VoteCountLabelComponent, VoteCountVotesComponent, VoteComponent,
                   PlayersListComponent, PlayerLabelComponent, PlayerReplaceeComponent, ListComponent)


class ComponentGenerationException(Exception):
    pass
