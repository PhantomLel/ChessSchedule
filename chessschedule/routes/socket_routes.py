from ..app import skt
from flask_socketio import emit, send 
from flask_socketio import join_room, leave_room
from typing import List
from ..models.room import Room
from ..models.player import Player
from uuid import uuid1
from flask import jsonify, request

"""
emit() has a kwarg called broadcast, which dictates sending to all users connected to the socket vs sending to just the
requester. the default for emit is broadcast = True
"""

def get_room_code(code:str) -> Room:
    for room in rooms:
        if room.code == code:
            return room
    return None

def get_room_uuid(uuid:str) -> Room:
    for room in rooms:
        if room.uuid == uuid:
            return room
    return None

@skt.on('connect')
def connect(data): 
    emit('connect_res', {'Status': 'Connected'}, broadcast=False)

@skt.on("check_room")
def check_room(data):
    if get_room_code(data[code]) != None:
        output = {"room_uuid":get_room_code(data[code]).uuid}
    else:
        output = {"error":"No room with the provided code exists"}
        
    emit("check_room_res", output, broadcast=False)

@skt.on("join_room")
def join_room(data):
    selected_room = get_room_code(data["code"]) or None
    if not selected_room:
        emit("join_room_res", {"error":"No room with the provided code exists"}, broadcast=False)
    
    # associate request SID with a socket "room"
    join_room(selected_room.uuid)
    
    player = Player()
    # associate player information with chessScheduel game
    selected_room.add_player(player)
    emit("join_room_res", {"user_uuid":player.uuid}, broadcast=False)
    player_list_update(selected_room)

# maintain a list of active rooms
rooms: List[Room] = list()

@skt.on("create_room")
def create(data):
    admin_uuid = str(uuid1())
    admin_sid = request.sid
    room = Room(admin_uuid, admin_sid)
    rooms.append(room)
    emit("create_room_res", {"user":admin_uuid, "room":room.uuid,"room_code":room.room_code}, broadcast=False)

@skt.on("delete_room")
def delete_room(data):
    selected_room = get_room_uuid(data["room_uuid"]) or None   

    if not selected_room:
        emit("delete_room_res", {"error" : "No room with provided UUID exists"}, broadcast=False)
        return

    if data["user_uuid"] == room.admin_uuid:
        # tell all clients to leave the room
        emit("delete_room_res", {"message":'Room closed by admin'}, to=room.uuid)

@skt.on("check_name")
def check_name(data):
    emit("check_name_res", {"valid":get_room_uuid(data["room_uuid"]).name_is_taken(data["name"])},broadcast=False)

def player_list_update(room:Room) -> None:
    data = jsonify({"players":[vars(player) for player in room.players]})
    emit("player_list_update", data, room=room.admin_sid)