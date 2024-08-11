from flask import request

from ..route_handler import RouteHandler


class SocketEvents:
    def __init__(self, app):
        self.app = app
        self.socket = app.socket
        self.register_events()

    def register_events(self):
        @self.socket.on("connect")
        def on_connect():
            print("Client connected")

        @self.socket.on("disconnect")
        def on_disconnect():
            print("Client disconnected")

        @self.socket.on("hmr:path")
        def _ping(path):
            content = None
            route_handler = self.app.routeHandler

            if len(route_handler.parsers.keys()) != 0:
                return

            content = route_handler.default_route(path)
            self.send("hmr:update-document", content)

    def send(self, event, data):
        self.socket.emit(event, data)
