
from MatchPoll import MatchPoll
from Player import Player

class SquadList:
    def __init__(self, match_poll: MatchPoll):
        self.players = match_poll.available_players()

   
    
    def __repr__(self):
        return f"SquadList(players={self.players})"