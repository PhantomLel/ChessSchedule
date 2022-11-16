from ..app import skt
from flask_socketio import emit
from flask_socketio import join_room, leave_room


@skt.on('connect')
def connect(data):
    emit('my response', {'dawdoiwahdiaow': 'Connected', "akey" : 12})

@skt.on('my event')
def msg(data):
    emit('wow', {"nicemsg": data["msg"]})

@skt.on("create_room")
def create(data):
    emit("response", {"user":"jsodaijfsdoifj", "room":})