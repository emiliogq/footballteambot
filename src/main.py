from FootballTeamBot import FootballTeamBot
from sys import argv

if __name__ == "__main__":
    token = argv[1] if (len(argv) >= 2) else ""
    FootballTeamBot(token)
