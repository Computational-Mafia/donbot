from Temporal import Temporal


class Vote(Temporal):
    def __init__(self, voter, votee, start, end=None, power=1):
        Temporal.__init__(self, start, end)
        self.voter = voter
        self.votee = votee
        self.power = power

    def __str__(self):
        return '<Vote: ' + self.voter + ' -> ' + self.votee + ' (' + self.start + ')>'
