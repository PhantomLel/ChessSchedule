import uuid
from ..algos.elo import change_rating
from flask_socketio import emit, send


SKILL_DICT = {1: 100, 2: 250, 3: 500, 4: 700, 5: 900}


class Player:
    def __init__(self, name: str, skill: int, sid: str) -> None:
        self.name = name
        self.uuid = str(uuid.uuid1())
        self.rating = self.get_skill(int(skill))
        self.wins = 0
        self.losses = 0
        self.draws = 0
        self.players_played = dict()
        self.sid = sid
        self.sitout_num = 0

    def eval_score(self):
        "Calculates a win/draw/loss record as one float."
        return self.wins + self.draws / 2 - self.losses

    def get_skill(self, assessment: int):
        if assessment not in SKILL_DICT:
            raise Exception(
                f"Malformed Request: Skill level {assessment} not in range [1,5]"
            )
        return SKILL_DICT[assessment]

    def game_result(self, result: str, opponent_rating, opponent_uuid) -> None:
        "Updates nessesary player information after a game is played, based on the result."
        if result == "win":
            self.wins += 1
            result = 1
        elif result == "draw":
            self.draws += 1
            result = 0.5
        elif result == "loss":
            self.losses += 1
            result = 0
        else:
            raise Exception(
                f'Malformed Request: Invalid result string "{result}" - result must be "win", "draw", or "loss"'
            )

        # update elo
        self.rating = change_rating(self.rating, opponent_rating, result)
        # keep track of game as being played
        self.players_played[opponent_uuid] = (
            self.players_played.get(opponent_uuid, 0) + 1
        )
