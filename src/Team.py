
import json
import datetime


class Team:
    def __init__(self, name, members = []):
        self.name = name

    def save(self):
        data = {
            "name": self.name
        }
        with open(f"team_{self.name}.json", "w") as f:
            json.dump(data, f)

    def load(self):
        with open(f"team_{self.name}.json", "r") as f:
            data = json.load(f)
            self.name = data["name"]

    def save(self):
        pass

    def load(self):
        pass

    def __repr__(self):
        return f"Team(name={self.name})"