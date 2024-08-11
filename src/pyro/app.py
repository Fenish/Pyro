from .config import Config

# ----------------- FLASK IMPORTS --------------------- #

from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_compress import Compress

# ----------------- PYRO IMPORTS --------------------- #

from .core.route_handler import RouteHandler
from .core.devMode.socket import SocketEvents

app = Flask(__name__)
Compress(app)
CORS(app)

# ----------------- HOT MODULE RELOAD --------------------- #
# HMR: Hot module reload, for development only


def start_socket_server():
    global socket
    if Config.development == False:
        return

    app.socket = SocketIO(
        app, cors_allowed_origins="*", transports=["pooling", "websocket"]
    )
    SocketEvents(app)


def start_server():
    start_socket_server()
    app.routeHandler = RouteHandler(app)
    app.run(host=Config.host, port=Config.port, debug=Config.development)


def start(routes=[], development=False):
    Config.development = development
    Config.routes = routes

    start_server()
