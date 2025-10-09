
class TeamPoll:
    def __init__(self, team):
        self.team = team
        self.match_polls = []

    def create_poll(self, poll_id, created_at):
        poll = MatchPoll(poll_id, created_at)
        self.match_polls.append(poll)
        return poll

    def get_active_polls(self):
        return [poll for poll in self.match_polls if poll.is_active()]

    def get_poll_report(self, poll_id):
        poll = next((poll for poll in self.match_polls if poll.poll_id == poll_id), None)
        if poll:
            return poll.report(self.team.members)
        return "Poll not found."
