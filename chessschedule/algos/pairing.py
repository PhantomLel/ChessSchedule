from ..models.player import Player
from typing import Tuple, List
import random, json


def create_pairing(players: List[Player]) -> List[Tuple[dict, dict]]:
    "Returns a list of player (as dictionaries) tuple pairings."

    pairs = []
    odd = False
    # if the number of players are odd then have one sit out for a round
    if len(players) % 2 != 0:
        players.sort(key=lambda x: x.sitout_num)
        # for testing REMOVE LATER.
        sitout = random.choice(players)
        players.remove(sitout)
        sitout.sitout_num += 1
        odd = True

    players.sort(key=lambda x: x.rating, reverse=True)

    # find pairs with close elo and that have not played before
    while players:
        player = players.pop(0)
        for match in players:
            # pair if good match or last player available
            if (match.uuid not in player.players_played) or (match == players[-1]):
                # run vars to make the player serializeable by json - objects cant be serialized, but dicts can
                pairs.append((vars(player), vars(match)))
                players.remove(match)
                break

    if odd:
        # must first be put in list then changed into tuple for whatever reason i hate life
        pairs.append(tuple([vars(sitout)]))
    print(json.dumps(pairs))
    return pairs


if __name__ == "__main__":
    print("Pairing tests running...")

    players = []
    for i in range(6):
        a = Player(str(i))
        a.rating += i * 100
        players.append(a)

    for j in range(10):
        d = create_pairing(players)
        for x in d:
            x[0].game_result("loss", x[1])
            x[1].game_result("win", x[0])
            players.append(x[0])
            players.append(x[1])

        # print(f"pairings: {[[[x[0].name, x[0].rating],[x[1].name, x[1].rating]] for x in d]}")
        print(f"results : {[[x.name, x.rating] for x in players]}")
        print("-" * 10)
