
from datetime import datetime

from Location import Location

class Match:
    def __init__(self, team: 'Team', match_id, date: datetime.datetime, location: Location, opponent: str, home_or_away="home"):
        self.team = team 
        self.match_id = match_id
        self.date: datetime.datetime = date  # datetime object
        self.location: Location = location  # Location object
        self.opponent: str = opponent  # string
        self.home_or_away: str = home_or_away  # "home" or "away"

    def __str__(self):
        s = ""
        s += f"📅 {self.date.strftime('%d-%m-%Y')}\n"
        s += f"🕘 {self.date.strftime('%H:%M')}\n"
        s += f"{self.location}"
        s += f"👕 {self.team.equipments[self.home_or_away].color_name})"
        return s
