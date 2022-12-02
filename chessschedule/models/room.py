from uuid import uuid1
from typing import List, Dict, Tuple
from .player import Player
from ..algos import pairing, elo
from random import randint
from collections import namedtuple

Claim = namedtuple("Claim", "winner_uuid claimer")


class Room:
    def __init__(self, admin_uuid: str, admin_sid: str, session) -> None:
        self.uuid = str(uuid1())
        self.admin_uuid = admin_uuid
        self.admin_sid = admin_sid

        # TODO this is a temporary solution - the odds of a collision are low but possible
        self.room_code = str(randint(1_000_000, 9_999_999))
        self.players: List[Player] = list()
        self.player_names = set()
        self.round = 1
        self.matches_left = None
        self.current_pairings: List[Tuple[dict, dict]]
        self.claims: List[Claim] = list()
        self.draw_claims: List[str] = list()
        self.results = list()

    def reset_round(self):
        "Resets all attributes of a room that are temporary for a round"
        self.results = list()
        self.draw_claims = list()
        self.claims = list()
        self.current_pairings = list()
        self.matches_left = None
        self.round += 1

    def leaders(self, num: int) -> Dict[str, List[Dict]]:
        "Gives a list of the top players and their win/draw/loss record"
        if num > len(self.players):
            num = len(self.players)

        leaders = sorted(self.players, key=lambda x: x.rating, reverse=True)[:num]
        return {
            "rankings": [
                {"name": p.name, "score": [p.wins, p.draws, p.losses, p.rating]}
                for p in leaders
            ]
        }

    def add_player(self, player: Player) -> None:
        "Adds a player object to the game"
        if player.name in self.player_names:
            raise Exception(f"Player name already taken: " + player.name)
        self.players.append(player)
        self.player_names.add(player.name)

    def name_is_taken(self, name: str) -> bool:
        "Returns false if the name provided is already the name of another player else true"
        return name in self.player_names

    def get_pairings(self):
        "Returns a list of player-to-player pairings as created by algorithm"
        self.current_pairings = pairing.create_pairing(self.players.copy())
        self.matches_left = len(self.current_pairings)
        return self.current_pairings

    def get_player_by_uuid(self, user_uuid: str):
        "Returns a player with the provided uuid"
        for player in self.players:
            if player.uuid == user_uuid:
                return player
        return None

    def get_opponent_by_uuid(self, user_uuid: str) -> str:
        "Gets the opponent of the player that has provided uuid"
        opponent_uuid = None
        for pairing in self.current_pairings:
            if len(pairing) == 1:
                continue  # continue on bye
            if pairing[0]["uuid"] == user_uuid:
                opponent_uuid = pairing[1]["uuid"]
                break
            elif pairing[1]["uuid"] == user_uuid:
                opponent_uuid = pairing[0]["uuid"]
                break

        if (
            opponent_uuid is None
        ):  # opponent is none, can happen when player has a bye or if something went wrong
            return None
        return self.get_player_by_uuid(opponent_uuid)

    def get_player_claim(self, user) -> str:
        "Gets the game-result-claim of the player i.e. win/lose/draw"
        if type(user) is str:
            user = self.get_player_by_uuid(user)
        elif user is None:
            return "bye"

        result = None
        if user.uuid in self.draw_claims:
            return "draw"

        for claim in self.claims:
            if claim.claimer != user.uuid:
                continue
            result = "win" if claim.winner_uuid == user.uuid else "loss"
        return result

    def get_opponent_claim(self, user_uuid):
        "Gets the result claim of the opponent of the player that has the provided uuid"
        opponent = self.get_opponent_by_uuid(user_uuid)
        return self.get_player_claim(opponent)

    def remove_claim(self, uuid) -> None:
        "Removes claims made by the player with the provided uuid"
        for claim in self.claims:
            if claim.claimer == uuid:
                self.claims.remove(claim)
        for claim in self.draw_claims:
            if claim == uuid:
                self.draw_claims.remove(claim)

    def game_result(self, user_uuid: str, user_claim: str) -> str:
        """
        Function that takes user input of the result of a game (win/lose/draw)
        Ensures that a player and their opponent agre on the result of a match
            - if they do not, it returns "failure" to reprompt players for result
            - if they do, it updates player ratings and stores the result
        """
        opponent = self.get_opponent_by_uuid(user_uuid)
        user = self.get_player_by_uuid(user_uuid)

        opponent_claim = self.get_player_claim(opponent)
        if user_claim == "draw":
            # draw logic
            if opponent_claim == "draw":
                # the players draw
                user.rating, opponent.rating = elo.change_rating(
                    user.rating, opponent.rating, [0.5, 0.5]
                )
                user.game_result("draw", opponent.uuid)
                opponent.game_result("draw", user.uuid)
                return "success"
            elif opponent_claim is None:
                self.draw_claims.append(user_uuid)
                return "inconclusive"
            else:
                self.remove_claim(opponent.uuid)
                return "failure"

        if opponent_claim is None:
            self.claims.append(Claim(user_claim, user_uuid))
            return "inconclusive"

        if opponent_claim == "bye":
            self.results.append([user.name])
            return "success"

        user_claim = "win" if user_claim == user_uuid else "loss"
        if user_claim == "win" and opponent_claim == "loss":
            # update ratings
            user.rating, opponent.rating = elo.change_rating(
                user.rating, opponent.rating, [1, 0]
            )
            user.game_result("win", opponent.uuid)
            opponent.game_result("loss", user.uuid)
            self.results.append([user.name, opponent.name, user.name])
            return "success"
        elif user_claim == "loss" and opponent_claim == "win":
            # update ratings
            user.rating, opponent.rating = elo.change_rating(
                user.rating, opponent.rating, [0, 1]
            )
            user.game_result("loss", opponent.uuid)
            opponent.game_result("win", user.uuid)
            self.results.append([user.name, opponent.name, opponent.name])
            return "success"
        else:
            self.remove_claim(opponent.uuid)
            return "failure"
