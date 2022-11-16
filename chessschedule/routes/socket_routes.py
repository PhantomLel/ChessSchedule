from ..app import skt
from flask_socketio import emit, send
from flask_socketio import join_room, leave_room
from typing import List

"""
emit() has a kwarg called broadcast, which dictates sending to all users connected to the socket vs sending to just the
requester. the default for emit is broadcast = True
"""

@skt.on('connect')
def connect(data):
    emit('my response', {'dawdoiwahdiaow': 'Connected', "akey" : 12}, broadcast=False)


@skt.on('my event')
def msg(data):
    emit('wow', {"nicemsg": data["msg"]})

# maintain a list of active rooms
rooms: List[Room] = list()

@skt.on("create_room")
def create(data):
    emit("response", {"user":"jsodaijfsdoifj", "room":"SOMEROOM"}, broadcast=False)

@skt.on("delete_room")
def delete_room(data):
    selected_room = None
    for room in rooms:
        if room.uuid == data["room_uuid"]:
            selected_room = room

    if not selected_room:
        return # some kind of error handling
    
    if data["user_uuid"] == room.admin_uuid:
        # tell all clients to leave the room
        emit("delete_room_res", 'Room closed by admin', broadcast=True)
    