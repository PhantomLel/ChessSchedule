from uuid import uuid1
from typing import List, Dict,Tuple 
from .player import Player
from ..algos import pairing
from random import randint


class Room:
    def __init__(self, admin_uuid: str, admin_sid: str, session) -> None:
        self.uuid = str(uuid1())
        self.admin_uuid = admin_uuid
        self.admin_sid = admin_sid

        # TODO this is a temporary solution - the odds of a collision are low but possible
        self.room_code = str(randint(1_000_000, 9_999_999))
        self.players: List[Player] = list()
        self.player_names = set()
        self.rounds = 1
        self.current_pairings:List[Tuple[dict, dict]]

    def add_player(self, player: Player) -> None:
        if player.name in self.player_names:
            raise Exception(f"Player name already taken: " + player.name)
        self.players.append(player)
        self.player_names.add(player.name)

    def name_is_taken(self, name: str) -> bool:
        return name in self.player_names

    def get_pairings(self):
        self.current_pairings = pairing.create_pairing(self.players)
        return self.current_pairings