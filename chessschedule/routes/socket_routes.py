from ..app import skt
from flask_socketio import emit

@skt.on('connect')
def connect(data):
    emit('my response', {'data': 'Connected'})

@skt.on('who won')
def msg(data):
    emit('wow cool msg', {'status' : "wow"})