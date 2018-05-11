from Modifier import Modifiable
from Temporal import Temporal
from Player import Player


class Elector(Temporal, Modifiable):
    def __init__(self, start, player, end=None):
        Temporal.__init__(self, start, end)
        Modifiable.__init__(self)
        self._set_defaults(start)
        if isinstance(player, Player):
            # This is a player elector
            self.player = player
            self.name = None
            self.transfer_modifiers(start, player)
        else:
            # This is a non-player elector
            self.player = None
            self.name = player

    def __str__(self):
        if self.player:
            return '<Elector(Player): ' + str(self.player) + '>'

    def get_player(self):
        if self.player:
            return self.player
        else:
            return self.name

    def get_name(self, post):
        if self.player:
            return self.player.get_current_user(post).display_name
        else:
            return self.name

    def matches_name(self, post, name):
        if self.player:
            # This is a player elector
            for player_name in self.player.get_current_user(post).names():
                if player_name == name:
                    return True
            return False
        else:
            # This is a non-player elector
            if self.name == name:
                return True
            else:
                return False

    def _set_defaults(self, post):
        self.set_modifier(post, 'can_vote', True)
        self.set_modifier(post, 'can_be_voted', True)
        self.set_modifier(post, 'can_unvote', True)
        self.set_modifier(post, 'automatically_unvote', True)
        self.set_modifier(post, 'vote_power', 1)
        self.set_modifier(post, 'maximum_simultaneous_votes', 1)
        self.set_modifier(post, 'multiple_simultaneous_votes_on_one_player', False)
        self.set_modifier(post, 'threshold_modifier', 0)
