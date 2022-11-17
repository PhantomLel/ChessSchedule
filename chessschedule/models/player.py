import uuid
from ..algos.elo import change_rating

WIN = (1,0)
DRAW = (.5, .5)
LOSS = (0,1)

class Player:
    def __init__(self, name: str) -> None:
        self.name = name
        self.uuid = str(uuid.uuid1())
        self.rating = 1000
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.players_played = dict()
    
    def game_result(self, result:str, opponent) -> None:
        " Updates nessesary player information after a game is played, based on the result. "
        if result == "win":
            self.wins += 1
            result = WIN
        elif result == "draw":
            self.draws += 1
            result = DRAW
        elif result == "loss":
            self.losses += 1
            result = LOSS
        else:
            raise Exception(f"Invalid result string \"{result}\" - result must be \"win\", \"draw\", or \"loss\"")

        # update elo
        self.rating = change_rating(self.rating, opponent.rating, result)[0]
        # keep track of game as being played
        players_played[opponent.uuid] = players_played.get(opponent.uuid, 0) + 1
