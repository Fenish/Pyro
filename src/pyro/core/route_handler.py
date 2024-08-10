import os
from .html import Html
from .parser import PyroParser
from flask import make_response, send_from_directory, redirect, request

from ..config import Config


class RouteHandler:
    def __init__(self, app):
        self.app = app
        self.routes = Config.routes
        self.parsers = {}

        self.register()

    def resolve_path(self, path):
        for route in self.routes:
            if route["path"] == path:
                return route
        return None

    def resolve_content(self, path):
        route = self.resolve_path(path)
        if route is None:
            return None

        module = route["module"]
        parser = PyroParser(module)

        if self.parsers.get(path) is None:
            self.parsers[path] = parser

        html = Html(parser.html_body)
        return html.content

    def register(self):
        @self.app.route("/")
        @self.app.route("/404")
        @self.app.route("/<path:path>")
        def _dynamic(path=""):
            request_path = request.path
            return make_response(self.default_route(request_path))

        @self.app.route("/favicon.ico")
        def _favicon():
            return send_from_directory(
                os.path.join(self.app.root_path, "static"),
                "favicon.ico",
                mimetype="image/vnd.microsoft.icon",
            )

    def default_route(self, path):
        content = self.resolve_content(path)
        if content is not None:
            return content

        if path != "/404":
            return redirect("/404", code=302)
        return "404 Page not found"
