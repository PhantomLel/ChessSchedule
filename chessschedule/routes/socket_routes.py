from ..app import skt
from flask_socketio import emit, send
from flask_socketio import join_room, leave_room

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


@skt.on("create_room")
def create(data):
    emit("response", {"user":"jsodaijfsdoifj", "room":"SOMEROOM"}, broadcast=False)