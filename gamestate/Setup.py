import json

from User import User
from Modifier import Modifiable
from Phase import PhaseType
from Player import Player


class Setup(Modifiable):
    def __init__(self, filename=None, setup_name=None):
        self.post = 0
        pass

    def _load_from_file(self, filename=None, setup_name=None):
