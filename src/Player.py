

class Player:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        
    def __repr__(self):
        return f"Player(user_id={self.user_id}, username={self.username}, votes={self.votes})"