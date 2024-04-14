from typing import Optional

class VoteCount:
    
    def __init__(self, slots: list[list[str]], meta=Optional[str], lessOneForMislynch: bool =False, doublevoters: Optional[list[str]]=None):
        if meta is None:
            meta = {}
        if doublevoters is None:
            doublevoters = []

        # each slot is assigned an index in range(len(slots)), 
        # with len(slots) equivalent to voting "UNVOTE", 
        # and len(slots)+1 equivalent to "NO LYNCH"
        # start votecount with everyone voting no one

        self.slots, self.votesByVoter, self.votesByVoted = slots.copy(), [], []
        for _ in slots:
            self.votesByVoter.append(len(slots))
            self.votesByVoted.append([])
        self.votesByVoted.append(list(range(len(slots)))) # non voters
        self.votesByVoted.append([]) # no lynch voters
        self.doublevoters = doublevoters
        self.lessOneForMislynch = lessOneForMislynch
        self.choice, self.votelog, self.meta = None, [], meta
        
    def __str__(self) -> str:
        string = ''
        for i in self.votesByVoted.keys():
            voters = [self.slots[voter] for voter in self.votesByVoted[i]]
            voted = ('Not Voting' if i == len(self.slots) else
                     ('No Lynch' if i > len(self.slots) else
                      self.slots[i]))
            string += f'{voted}-{len(voters)}' + 'votes:\n'
            for each in voters:
                string += each + '\n'
            string += '\n'
        return string[:-1]

    def todict(self) -> dict:
        output = {}
        for i in range(len(self.votesByVoted)):
            voters = []
            for voter in self.votesByVoted[i]:
                voters.append(self.slots[voter])
                if self.slots[voter] in self.doublevoters:
                    voters.append(self.slots[voter])
            voted = ('Not Voting' if i == len(self.slots) else
                     ('No Lynch' if i > len(self.slots) else
                      self.slots[i]))
            output[str(voted)] = voters
        return output

    def kill_player(self, killed: str, postnumber: Optional[int]=None):
        self.votelog.append(f'{killed} killed in post {str(postnumber)}')

        # get killedslot
        killedslot = next(self.slots.index(s) for s in self.slots if s.count(killed) > 0)

        # collect slots voting killed slot and reset their votes
        for voterslot in [i for i, s in enumerate(self.votesByVoter) if s == killedslot]:
            self.votesByVoter[voterslot] = len(self.slots)
            self.votesByVoted[len(self.slots)].append(voterslot)

        # remove killedslot
        killedtarget = self.votesByVoter[killedslot]
        del self.votesByVoted[killedtarget][self.votesByVoted[killedtarget].index(killedslot)]
        del self.slots[killedslot]
        del self.votesByVoter[killedslot]
        del self.votesByVoted[killedslot]

        # update slot indices
        self.votesByVoter = [v - (v > killedslot) for v in self.votesByVoter]
        for i in range(len(self.votesByVoted)):
            for j in range(len(self.votesByVoted[i])):
                v = self.votesByVoted[i][j]
                self.votesByVoted[i][j] = v - (v > killedslot)
        
    def update(self, voter: str, voted: str, postnumber: Optional[int]=None):
        self.votelog.append(f'{voter} voted {voted} in post {str(postnumber)}')

        # get voterslot and votedslot
        voterslot = next(self.slots.index(s) for s in self.slots
                         if s.count(voter) > 0)
        votedslot = (len(self.slots) if voted == 'UNVOTE' else
                     (len(self.slots)+1 if voted == 'NO LYNCH' else
                      next(self.slots.index(s) for s in self.slots
                           if s.count(voted) > 0)))

        oldvoted = self.votesByVoter[voterslot]
        self.votesByVoter[voterslot] = votedslot

        # update votesByVoted
        oldvoteindex = self.votesByVoted[oldvoted].index(voterslot)
        del self.votesByVoted[oldvoted][oldvoteindex]
        self.votesByVoted[votedslot].append(voterslot)

        # if voted has a majority of votes, mark as voters' choice
        self.check_choice(votedslot)
                
    def check_choice(self, votedslot: int):
        
        # only matters if votedslot is a player or NO LYNCH
        if votedslot < len(self.slots) or votedslot == len(self.slots)+1:
            
            # calculate a length, weighting for potential doublevoters
            total = 0
            for each in self.votesByVoted[votedslot]:
                total += 1
                if self.slots[each] in self.doublevoters:
                    total += 1

            if total > len(self.slots)/2.0 or (votedslot == len(self.slots)+1 and self.lessOneForMislynch and total == len(self.slots)/2.0):
                self.choice = (self.slots[votedslot]
                               if votedslot < len(self.slots)
                               else 'NO LYNCH')
