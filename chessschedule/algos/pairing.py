from ..models.player import Player
from typing import Tuple, List


def create_pairing(players) -> List[Tuple[Player, Player]]:
    """
    Params
    players : List[Player]

    Returns
    List[Tuple[Player, Player]]
    """

    pairs = []
    players.sort(key=lambda x: x.rating, reverse=True)

    # find pairs with close elo and that have not played before
    while players:
        player = players.pop(0)
        for match in players:
            # pair if good match or last player available
            if (match.uuid not in player.players_played) or (match == players[-1]):
                pairs.append((player, match))
                players.remove(match)
                break

    return pairs


"""
# test cases - put somewhere else later
players = []
for i in range(6):
    a = Player(str(i))
    a.rating += i*100
    players.append(a)

for j in range(10):
    d = create_pairing(players)
    for x in d:
        x[0].game_result("loss", x[1])
        x[1].game_result("win", x[0])
        players.append(x[0])
        players.append(x[1])

    #print(f"pairings: {[[[x[0].name, x[0].rating],[x[1].name, x[1].rating]] for x in d]}")
    print(f"results : {[[x.name, x.rating] for x in players]}")
    print("-"*10)
"""
