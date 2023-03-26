from ..app import skt, app
from flask_socketio import emit
from flask_socketio import join_room, leave_room
from typing import List
from ..models.room import Room
from ..models.player import Player
from uuid import uuid1
from flask import request, session
import random


# ------------------- large line ------------------
def get_room_code(code: str) -> Room:
    "Gets a room with the code provided"
    for room in rooms:
        if room.room_code == code:
            return room
    return None


def get_room_uuid(uuid: str) -> Room:
    "Gets a room with the room_uuid provided"
    for room in rooms:
        if room.uuid == uuid:
            return room
    return None


def get_room_host_uuid(host_uuid: str) -> Room:
    "Gets a room with the host_uuid provided"
    for room in rooms:
        if room.admin_uuid == host_uuid:
            return room
    # throw the exception to stop execution
    raise Exception(f"Unable to find room with host_uuid {host_uuid}")
    return None


def player_list_update(room: Room) -> None:
    "Sends an event to the room's host to update current player list"
    data = {"players": [vars(player) for player in room.players]}
    emit("player_list_update", data, to=room.admin_sid)


def emit_pairings(room: Room) -> None:
    pairings = room.get_pairings()
    emit(
        "pairings",
        {"round": room.round, "pairings": pairings},
        to=room.uuid,
        broadcast=True,
    )
    emit(
        "pairings",
        {"round": room.round, "pairings": pairings},
        to=room.admin_sid,
        broadcast=False,
    )


# ------------------- big line ------------------


@skt.on("connect")
def connect(data):
    "Initial socket connection route"
    emit("connect_res", {"Status": "Connected"}, broadcast=False)


@skt.on("get_room_state")
def get_room_state(data):
    room = get_room_uuid(data["uuid"])
    if room is None:
        emit(
            "get_room_state_res",
            {"status": 500, "error": "No room with provided uuid was found."},
        )
        return
    emit("get_room_state_res", {"state": room.state()})


@skt.on("check_room")
def check_room(data):
    "Checks if a room exists, and returns room's uuid if it does"
    if get_room_code(data["code"]) != None:
        output = {"room_uuid": get_room_code(data["code"]).uuid}
    else:
        output = {"error": "No room with the provided code exists"}

    emit("check_room_res", output, broadcast=False)


@skt.on("get_pairings")
def get_pairings(data):
    room = get_room_uuid(data["room_uuid"])
    if room is None:
        emit(
            "error",
            {status: 500, "error": "No room with provided uuid exists"},
            broadcast=False,
        )
    emit("get_pairings_res", {"pairings": room.round_pairings}, broadcast=False)


@skt.on("join_room")
def join_comp(data):
    "Socket route that enters a player client into a game"
    selected_room = get_room_code(data["code"])
    if selected_room is None:
        emit(
            "join_room_res",
            {"error": "No room with the provided code exists"},
            broadcast=False,
        )
        return
    if selected_room.started:
        emit(
            "join_room_res",
            {"error": "This game is already in progress"},
            broadcast=False,
        )
        return

    # associate request SID with a socket "room"
    join_room(selected_room.uuid)

    player = Player(data["name"], data["skill"], request.sid)
    # associate player information with chessScheduel game
    selected_room.add_player(player)
    emit("join_room_res", {"user_uuid": player.uuid}, broadcast=False)
    player_list_update(selected_room)


@skt.on("get_all_players")
def get_all_players(data):
    "Socket route that returns a list of all players"
    player_list_update(get_room_uuid(data["room_uuid"]))


# maintain a list of active rooms
rooms: List[Room] = list()


@skt.on("create_room")
def create(data):
    "Socket route that creates a room"
    admin_uuid = str(uuid1())
    admin_sid = request.sid
    while 1:
        room = Room(admin_uuid, admin_sid, session)
        for r in rooms:
            if r.room_code == room.room_code:
                del room
                break
        break

    rooms.append(room)
    emit(
        "create_room_res",
        {"host_uuid": admin_uuid, "room_uuid": room.uuid, "room_code": room.room_code},
        broadcast=False,
    )
    # debug
    # for i in range(24):
    #     # random name and elo
    #     a = Player("", 5, 5000)
    #     a.rating = random.randint(100, 1000)
    #     a.name = str(a.rating)
    #     room.add_player(a)
    player_list_update(room)


@skt.on("room_exists")
def room_exists(data):
    "Socket route that checks if a room exists"
    emit("room_exists", {"exists": get_room_uuid(data["room_uuid"]) is not None})


@skt.on("check_name")
def check_name(data):
    "Valid if name is not taken, and not valid if name is taken."
    emit(
        "check_name_res",
        {"valid": not get_room_uuid(data["room_uuid"]).name_is_taken(data["name"])},
        broadcast=False,
    )


@skt.on("start_game")
def start_game(data):
    "Socket route that starts the game"
    room = get_room_host_uuid(data["host_uuid"])
    if room is None:
        emit("start_game_res", {"status": 500}, broadcast=False)
        return
    else:
        room.started = True
        emit("start_game_res", {"status": 200}, broadcast=False)
    emit_pairings(room)


@skt.on("game_result")
def game_result(data):
    "Socket route that players send to tell the server the game's result"
    room = get_room_uuid(data["room_uuid"])
    success = room.game_result(data["player_uuid"], data["result"])
    user = room.get_player_by_uuid(data["player_uuid"])
    opponent = room.get_opponent_by_uuid(data["player_uuid"])

    if success == "success":
        room.matches_left -= 1
        # update the host's leaderboard
        emit("leaderboard", room.leaders(1000), to=room.admin_sid, broadcast=False)
        if room.matches_left <= 0:
            emit(
                "round_results", {"results": room.results}, to=room.uuid, broadcast=True
            )
    if success != "inconclusive":
        emit(
            "game_result_res",
            {"status": 200 if success == "success" else 500},
            to=user.sid,
            broadcast=False,
        )
        if opponent is not None:  # when a user has a bye, their opponent is None
            emit(
                "game_result_res",
                {"status": 200 if success == "success" else 500},
                to=opponent.sid,
                broadcast=False,
            )


@skt.on("get_leaderboard")
def get_leaderboard(data):
    "Socket route that returns leaderboard information. Called by each individual client."
    room = get_room_uuid(data["room_uuid"])
    emit("leaderboard", room.leaders(1000), broadcast=False)


@skt.on("next_round")
def next_round(data):
    "Socket route that starts the next round of games"
    room = get_room_uuid(data["room_uuid"])
    if room.admin_uuid != data["host_uuid"]:
        emit("next_round_res", {"status": 502}, broadcast=False)
        return

    if data["ensure_match_completions"] and room.matches_left != 0:
        emit("next_round_res", {"status": 501}, broadcast=False)
        return

    room.reset_round()
    emit("next_room_res", {"status": 200}, broadcast=False)
    emit_pairings(room)


@skt.on("end_game_host")
def end_game(data):
    "Socket route that ends the game of a room"
    room = get_room_uuid(data["room_uuid"])
    print(data["host_uuid"])
    if data["host_uuid"] != room.admin_uuid:
        # the odds of this are vanishlingly infinitesimal
        emit("error", {"status": 502}, broadcast=False)
        return

    # send game ended to players
    emit("game_ended", {"results": room.leaders(10)}, to=room.uuid, broadcast=True)
    # send game ended to host
    emit("game_ended", {"results": room.leaders(10)}, broadcast=False)
    rooms.remove(room)


@skt.on("reconnect_player")
def reconnect_player(data):
    room = get_room_uuid(data["room_uuid"])
    if room is None:
        emit(
            "reconnect_player_res",
            {"status": 500, "error": "No room with provided code exists"},
            broadcast=False,
        )
        return

    player = room.get_player_by_uuid(data["player_uuid"])
    player.sid = request.sid
    join_room(room.uuid)
    emit(
        "reconnect_player_res",
        {
            "status": 200,
            "room_state": room.state(),
            "player_state": room.player_state(data["player_uuid"]),
        },
        broadcast=False,
    )


@skt.on("reconnect_host")
def reconnect_host(data):
    print(f"Host reconnection attempt: {data}")
    room = get_room_uuid(data["room_uuid"])
    if room is None:
        emit(
            "reconnect_host_res",
            {"status": 500, "error": "No room with provided code exists"},
            broadcast=False,
        )
        return
    if room.admin_uuid != data["host_uuid"]:
        app.logger.info(f"ROOM ADMIN UUID: {room.admin_uuid}\n{data['host_uuid']}")
        emit(
            "reconnect_host_res",
            {"status": 500, "error": "Host verification failed"},
            broadcast=False,
        )
        return
    room.admin_sid = request.sid
    emit("reconnect_host_res", {"status": 200, "state": room.state()}, broadcast=False)
