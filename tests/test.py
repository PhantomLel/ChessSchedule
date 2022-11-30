from typing import Tuple, List

import uuid
from flask_socketio import emit, send
from typing import Tuple

ELO_COEFFICIENT = 400  # a player with a 400 point advantage over their opponent is ten times more likely to win than to lose; larger value = wider range of rankings
K_FACTOR = 40  # larger number creates a larger change in elo


def change_rating(player1_rating, player2_rating, game_result) -> Tuple[int, int]:
    """
    change_rating updates the player's rating
    :param player1_rating: the rating of the first player pre-match
    :param player2_rating: the rating of the opponent player pre-match
    :param game_result: tuple of game result represented as 1 for win, 0.5 for draw, and 0 for loss
    :return: tuple of new ratings

    Reference: https://www.omnicalculator.com/sports/elo#elo-calculator-in-practice-elo-rating-in-a-chess-tournament
    """

    # Calculate new rating
    # Player 1
    expected_score = 1 / (
        1 + 10 ** ((player2_rating - player1_rating) / ELO_COEFFICIENT)
    )
    new_rating1 = round(player1_rating + K_FACTOR * (game_result[0] - expected_score))
    # Player 2
    expected_score = 1 / (
        1 + 10 ** ((player1_rating - player2_rating) / ELO_COEFFICIENT)
    )
    new_rating2 = round(player2_rating + K_FACTOR * (game_result[1] - expected_score))

    return (new_rating1, new_rating2)


WIN = (1, 0)
DRAW = (0.5, 0.5)
LOSS = (0, 1)

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

    def get_skill(self, assessment: int):
        if assessment not in SKILL_DICT:
            raise Exception(
                f"Malformed Request: Skill level {assessment} not in range [1,5]"
            )
        return SKILL_DICT[assessment]

    def game_result(self, result: str, opponent) -> None:
        "Updates nessesary player information after a game is played, based on the result."
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
            raise Exception(
                f'Malformed Request: Invalid result string "{result}" - result must be "win", "draw", or "loss"'
            )

        # update elo
        self.rating = change_rating(self.rating, opponent.rating, result)[0]
        # keep track of game as being played
        self.players_played[opponent.uuid] = (
            self.players_played.get(opponent.uuid, 0) + 1
        )


def create_pairing(players: List[Player]) -> List[Tuple[dict, dict]]:
    "Returns a list of player (as dictionaries) tuple pairings."

    pairs = []
    # if the number of players are odd then have one sit out for a round
    if len(players) % 2 != 0:
        players.sort(key=lambda x: x.sitout_num)
        sitout = players[0]
        sitout.sitout_num += 1

    players.sort(key=lambda x: x.rating, reverse=True)

    # find pairs with close elo and that have not played before
    while players:
        player = players.pop(0)
        for match in players:
            # pair if good match or last player available
            if (match.uuid not in player.players_played) or (match == players[-1]):
                # run vars to make the player serializeable by json - objects cant be serialized, but dicts can
                pairs.append((player, match))
                players.remove(match)
                break

    pairs.append((sitout))
    return pairs


import random

if __name__ == "__main__":
    print("Pairing tests running...")

    players = []
    for i in range(5):
        a = Player(str(i), 3, 1902409124)
        a.rating = random.randint(100, 1000)
        players.append(a)

    print(create_pairing(players))
