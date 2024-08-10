from typing import Literal

HeadTags = Literal[
    "title",
    "description",
    "author",
    "keywords",
    "robots",
    "stylesheet",
    "icon",
    "favicon",
]

HeadTagValues = {
    "title": "<title>{}</title>",
    "description": '<meta name="description" content="{}">',
    "author": '<meta name="author" content="{}">',
    "keywords": '<meta name="keywords" content="{}">',
    "robots": '<meta name="robots" content="{}">',
    "stylesheet": '<link rel="stylesheet" href="{}">',
    "icon": '<link rel="icon" href="{}">',
    "favicon": '<link rel="shortcut icon" href="{}">',
}
