from Modifier import Modifiable
from Temporal import Temporal


class PhaseType(Modifiable):
    def __init__(self, name, elections=list(), modifiers=None, deadline=None):
        Modifiable.__init__(self)
        self.name = name
        self.deadline = None
        self.elections = elections
        if modifiers:
            self.set_modifiers(0, modifiers)
        if self.get_modifier(0, 'start_with_zero'):
            self._current_number = -1
        else:
            self._current_number = 0

    def __str__(self):
        return '<PhaseType: ' + self.name + '>'

    # Make from a JSON object
    @staticmethod
    def make_from_json(post, json):
        if isinstance(json, dict):
            return PhaseType(**json)
        else:
            # Other types not supported
            raise TypeError

    def new(self, post):
        self._current_number += 1
        if self.get_modifier(0, 'use_plain_name'):
            name = self.name
        else:
            name = None
        new_phase = Phase(self, self._current_number, name, post)
        new_phase.transfer_modifiers(post, self)
        return new_phase


class Phase(Temporal, Modifiable):
    def __init__(self, phase_type, number, name=None, start=0, end=None):
        Temporal.__init__(self, start, end)
        Modifiable.__init__(self)
        self.phase_type = phase_type
        self.number = number
        if name:
            self.name = name
        else:
            self.name = self.phase_type.name + ' ' + str(self.number)
        self.start = start

    def __str__(self):
        return '<Phase: ' + self.name + '>'
