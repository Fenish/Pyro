from flask import request

from .route_handler import RouteHandler


class SocketEvents:
    def __init__(self, socket, app):
        self.app = app
        self.socket = socket
        self.register_events()

    def register_events(self):
        @self.socket.on("connect")
        def on_connect():
            print("Client connected")

            content = None
            route_handler = self.app.routeHandler
            client_path = request.headers.get("Referer", "/")

            if len(route_handler.parsers.keys()) != 0:
                return

            if (route_handler.parsers.get(client_path)) is not None:
                content = route_handler.default_route(client_path)
            else:
                content = route_handler.resolve_content("/404")

            self.socket.emit("hmr:update-content", content)

        @self.socket.on("disconnect")
        def on_disconnect():
            print("Client disconnected")

        @self.socket.on("ping")
        def _ping(message):
            self.socket.emit("pong")
