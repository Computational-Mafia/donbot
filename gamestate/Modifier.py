from Temporal import Temporal


class Modifier(Temporal):
    def __init__(self, name, start, value=None, end=None):
        Temporal.__init__(self, start, end)
        self.name = name
        self.value = value

    def __str__(self):
        return '<Modifier: (' + self.name + ': ' + str(self.value) + ')>'


class Modifiable:
    def __init__(self):
        self.modifiers = list()

    def active_modifiers(self, post):
        return [modifier for modifier in self.modifiers if modifier.active(post)]

    def get_modifier(self, post, modifier_name):
        for modifier in self.active_modifiers(post):
            if modifier.name == modifier_name:
                return modifier.value
        return None

    def end_modifier(self, post, modifier_name):
        for modifier in self.active_modifiers(post):
            if modifier.name == modifier_name:
                modifier.end = post
        return

    def set_modifier(self, post, modifier_name, value=None):
        if self.get_modifier(post, modifier_name) == value:
            return
        self.end_modifier(post, modifier_name)
        self.modifiers.append(Modifier(modifier_name, post, value=value))

    def set_modifiers(self, post, modifiers_dict):
        if modifiers_dict:
            for modifier in modifiers_dict.keys():
                self.set_modifier(post, modifier, modifiers_dict[modifier])

    def transfer_modifiers(self, post, source_object):
        for modifier in source_object.active_modifiers(post):
            self.set_modifier(post, modifier.name, modifier.value)
