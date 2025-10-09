import Location
from Player import Player

import json
import datetime

from Match import Match
from Equipment import Equipment

class Team:
    def __init__(self, name, members = []):
        self.name = name
        self.members = members  # List of Player objects
        self.matchs = []  # List of Match objects
        self.equipments = {}  # Dictionary of Equipment objects

    def save(self):
        data = {
            "name": self.name,
            "members": [{"username": member.username, "full_name": member.full_name, "user_id": member.user_id} for member in self.members],
            "matchs": [{"match_id": match.match_id, "date": match.date.isoformat(), "location": {"name": match.location.name, "map_link": match.location.map_link}, "opponent": match.opponent} for match in self.matchs],
            # "equipments": [ "home": {"color" : self.home_color()  }, "away" : {"color" : self.away_color() } ] 
        }
        with open(f"team_{self.name}.json", "w") as f:
            json.dump(data, f)

    def load(self):
        with open(f"team_{self.name}.json", "r") as f:
            data = json.load(f)
            self.name = data["name"]
            self.members = [Player(**member_data) for member_data in data["members"]]
            self.matchs = [Match(**match_data) for match_data in data["matchs"]]

    def add_member(self, player: Player):
        self.members.append(player)

    def remove_member(self, player: Player):
        self.members.remove(player)

    def set_home_equipment(self, color_name: str):
        equipment = Equipment(color_name)
        self.equipments['home'] = equipment

    def home_color(self):
        return self.equipments['home'].color_name if 'home' in self.equipments else "No asignado"
    
    def away_color(self):
        return self.equipments['away'].color_name if 'away' in self.equipments else "No asignado"
    
    def set_away_equipment(self, color_name: str):
        equipment = Equipment(color_name)
        self.equipments['away'] = equipment

    def create_match(self, match_id, date: datetime.datetime, location: Location, opponent: str):
        match = Match(match_id, date, location, opponent)
        self.matchs.append(match)

    def create_poll(self):
        pass

    def create_topic(self):
        pass

    def save(self):
        pass

    def load(self):
        pass

    def __repr__(self):
        return f"Team(name={self.name}, members={self.members}, matchs={self.matchs})"