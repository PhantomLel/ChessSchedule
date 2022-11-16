class Player:
    def __init__(self, name: str, uuid: str) -> None:
        self.name = name
        self.uuid = uuid
        self.rating = 1000
        self.wins = 0
        self.losses = 0
        self.draws = 0
        