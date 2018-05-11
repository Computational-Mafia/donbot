from Temporal import Temporal


class User(Temporal):
    def __init__(self, display_name, start, aliases=list(), end=None):
        Temporal.__init__(self, start, end)
        self.display_name = display_name
        self.aliases = aliases

    def __str__(self):
        return '<User: ' + self.display_name + '>'

    def names(self):
        output = list(self.aliases)
        output.append(self.display_name)
        return output
