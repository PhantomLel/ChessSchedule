from uuid import uuid1
from typing import List
from .player import Player
from random import randint
class Room:
    def __init__(self, admin_uuid:str) -> None:
        self.uuid = str(uuid1())
        self.admin_uuid = admin_uuid

        # TODO this is a temporary solution - the odds of a collision are low but possible
        self.room_code = str(randint(1_000_000, 9_999_999))
        self.players: List[Player] = list()
        self.player_names = set()
    
    def add_player(player:Player) -> None:
        self.players.append(player)
    
    def name_is_taken(name:str) -> bool:
        self.player_names.add(name)
        return name in self.player_names