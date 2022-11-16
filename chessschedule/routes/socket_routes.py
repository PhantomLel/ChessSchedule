from ..app import skt
from flask_socketio import emit

@skt.on('connect')
def connect(data):
    emit('my response', {'dawdoiwahdiaow': 'Connected', "akey" : 12})

@skt.on('my event')
def msg(data):
    emit('wow', {"nicemsg" : data["msg"]})