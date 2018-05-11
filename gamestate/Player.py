from Modifier import Modifiable
from Temporal import Temporal
from User import User


class Player(Temporal, Modifiable):
    def __init__(self, name, start, aliases=list(), end=None, role=None, alignment=None, modifiers=None):
        Temporal.__init__(self, start, end)
        Modifiable.__init__(self)
        self.original_name = name
        self.users = list()
        self.users.append(User(name, start, aliases))
        self.role = role
        self.alignment = alignment
        self.set_modifier(start, 'alive', True)
        if modifiers:
            self.set_modifiers(start, modifiers)

    def __str__(self):
        return '<Player O.K.A.: ' + self.original_name + '>'

    # Make from a JSON object
    @staticmethod
    def make_from_json(post, json):
        if isinstance(json, dict):
            return Player(start=post, **json)
        else:
            # Other types not supported
            raise TypeError

    def get_current_user(self, post):
        for user in self.users:
            if user.active(post):
                return user
        return None

    def replace(self, display_name, start, aliases=list()):
        self.get_current_user(start).end = start
        self.users.append(User(display_name, start, aliases))
