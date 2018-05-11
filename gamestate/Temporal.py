class Temporal:
    def __init__(self, start, end=None):
        self.start = start
        self.end = end

    def set_end(self, post):
        if post <= self.start:
            raise ValueError
        self.end = post

    def active(self, post):
        if self.end is None:
            if self.start <= post:
                return True
        elif self.start <= post < self.end:
            return True
        return False

    def past(self, post):
        return self.start <= post

    def future(self, post):
        return self.start > post
