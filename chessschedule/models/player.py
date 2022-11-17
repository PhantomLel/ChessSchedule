import uuid
class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.uuid = str(uuid.uuid1())
        self.rating = 1000
        self.wins = 0
        self.losses = 0
        self.draws = 0
        