from ..app import skt
from flask_socketio import emit, send
from flask_socketio import join_room, leave_room
from typing import List
from ..models.room import Room
from uuid import uuid1

"""
emit() has a kwarg called broadcast, which dictates sending to all users connected to the socket vs sending to just the
requester. the default for emit is broadcast = True
"""

def get_room_code(code:str):
    for room in rooms:
        if room.code == code:
            return room
    return None

def get_room_uuid(uuid:str):
    for room in rooms:
        if room.uuid == uuid:
            return room
    return None

@skt.on('connect')
def connect(data):
    # TODO emit needed information
    emit('connect_res', {'Status': 'Connected', "akey" : 12}, broadcast=False)

@skt.on("join_room")
def join_room(data):
    selected_room = get_room_code(data["code"]) or None
    if not selected_room: return # TODO some error to user
    join_room(selected_room.uuid)
    emit()

# maintain a list of active rooms
rooms: List[Room] = list()

@skt.on("create_room")
def create(data):
    admin_uuid = uuid1()
    room = Room(admin_uuid)
    rooms.append(room)
    # TODO emit needed information
    emit("create_room_res", {"user":admin_uuid, "room":room.uuid,"room_code":room.room_code}, broadcast=False)

@skt.on("delete_room")
def delete_room(data):
    selected_room = get_room_uuid(data["room_uuid"]) or None   

    if not selected_room:
        return # TODO some error to user
    
    if data["user_uuid"] == room.admin_uuid:
        # tell all clients to leave the room
        emit("delete_room_res", 'Room closed by admin', to=room.uuid)
