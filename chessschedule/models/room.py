from uuid import uuid1
from random import randint
class Room:
    def __init__(self, admin_uuid:str) -> None:
        self.uuid = uuid1()
        self.admin_uuid = admin_uuid

        # TODO this is a temporary solution - the odds of a collision are low but possible
        self.room_code = str(randint(1_000_000, 9_999_999)) 