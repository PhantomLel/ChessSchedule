from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
app.debug = True
skt = SocketIO(app)
