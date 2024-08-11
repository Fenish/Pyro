import os
import uuid
import time

from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

from ..tokenizers.template import TemplateTokenizer

# HMR: Hot Module Replacement
# What is HMR?
# HMR is a feature that allows you to update your code without restarting the server or refreshing the page.
# It's a way to make your code more dynamic and interactive.
# The reason that i implement hmr is to challenge myself


def replace_id(old_tokens, new_tokens):
    old_copied_tokens = [token.copy() for token in old_tokens]
    new_copied_tokens = [token.copy() for token in new_tokens]

    id_map = {
        new["id"]: old["id"] for old, new in zip(old_copied_tokens, new_copied_tokens)
    }

    for new_token in new_copied_tokens:
        old_token_id = id_map.get(new_token["id"])
        new_token_id = new_token["id"]

        if is_uuid4(new_token_id) and is_uuid4(old_token_id):
            new_token["id"] = old_token_id

        childrens = new_token.get("children", [])
        if childrens:
            for i, child in enumerate(childrens):
                if is_uuid4(child):
                    childrens[i] = id_map.get(child, child)

    return new_copied_tokens


def is_uuid4(id_string):
    """Check if the provided string is a valid UUID4."""
    try:
        val = uuid.UUID(id_string, version=4)
    except ValueError:
        return False
    return str(val) == id_string


def find_differences(old_tokens, new_tokens):
    changes = []
    old_token_dict = {token["id"]: token for token in old_tokens}
    new_token_dict = {token["id"]: token for token in new_tokens}
    keys_to_check = [
        "tag",
        "id",
        "class",
        "parent",
        "attributes",
        "custom_attributes",
        "value",
        "isVisible",
        "location",
    ]

    for old_id in old_token_dict:
        if old_id not in new_token_dict:
            changes.append({"type": "removed", "id": old_id, "changes": {}})

    for new_id in new_token_dict:
        if new_id not in old_token_dict:
            new_token = new_token_dict[new_id]
            changes.append(
                {
                    "type": "added",
                    "id": new_id,
                    "changes": {
                        key: {"value": new_token.get(key)}
                        for key in keys_to_check
                        if key in new_token
                    },
                }
            )

    for token_id in set(old_token_dict.keys()) & set(new_token_dict.keys()):
        old_token = old_token_dict[token_id]
        new_token = new_token_dict[token_id]

        token_changes = {}
        for key in keys_to_check:
            if old_token.get(key) != new_token.get(key):
                token_changes[key] = {"value": new_token.get(key)}

        if token_changes:
            changes.append(
                {"type": "modified", "id": token_id, "changes": token_changes}
            )

    return changes


class ChangeHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher

    def on_modified(self, event):
        if event.is_directory or event.src_path != self.watcher.path:
            return

        current_time = time.time()
        if (current_time - self.watcher.last_triggered) < self.watcher.debounce_time:
            return

        self.watcher.last_triggered = current_time

        old_tokens = self.watcher.old_tokens
        new_tokenizer = TemplateTokenizer(self.get_file_content())
        new_tokens = new_tokenizer.tokens

        diff = find_differences(old_tokens, new_tokens)
        if diff:
            self.watcher.old_tokens = new_tokens
            self.watcher.parser.html_body = new_tokenizer.generate_body()
            self.watcher.socket.emit("hmr:patch-document", diff)

    def get_file_content(self):
        path = os.path.join(os.getcwd(), f"{self.watcher.module}.pyro")
        with open(path, "r") as f:
            return f.read()


class PyroWatcher:
    def __init__(self, parser, app):
        self.parser = parser
        self.old_code = parser.raw_code
        self.old_tokens = parser.html_tokens
        self.module = parser.module_path
        self.socket = app.socket
        self.path = os.path.join(os.getcwd(), f"{self.module}.pyro")
        self.observer = PollingObserver()
        self.last_triggered = 0
        self.debounce_time = 0

    def start(self):
        handler = ChangeHandler(self)
        self.observer.schedule(handler, os.path.dirname(self.path), recursive=False)
        self.observer.start()
        print(f"Started watching: {self.path}")
