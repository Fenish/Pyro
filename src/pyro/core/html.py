from ..enums.head_tags import HeadTags, HeadTagValues
from ..config import Config


class Html:
    def __init__(self, body):
        self.content = ""
        self.js_files = []
        self.css_files = []

        self.body = body
        self.headers = [
            '<meta charset="UTF-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        ]

        if Config.development == True:
            self.headers.append('<script src="/static/socket.io.min.js"></script>')
            self.headers.append('<script src="/static/development.js"></script>')

        self.generate()

    def __str__(self):
        return self.content

    def add_javascript_file(self, path):
        self.js_files.append(path)

    def add_head_tag(self, tag: HeadTags, value: str):
        formatted_tag = HeadTagValues[tag].format(value)
        self.headers.append(formatted_tag)

    def generate_head(self):
        self.content += "<head>"
        for header in self.headers:
            self.content += header

        for js_file in self.js_files:
            self.content += f'<script src="{js_file}"></script>'
        self.content += "</head>"

    def generate(self):
        self.content = "<!DOCTYPE html>"
        self.content += '<html lang="en">'
        self.generate_head()
        self.content += "</html>"
        self.content += "<body>"
        self.content += self.body
        self.content += "</body>"

        return self.content
