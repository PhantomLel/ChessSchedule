from .app import skt, app

# init the flask routes
from .routes import flask_routes

# this inits the socket routes
from .routes import socket_routes

skt.run(app, port=5000, debug=True, use_reloader=True)
