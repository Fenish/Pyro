import os
import uuid
import time

from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler

from ..tokenizers.template import TemplateTokenizer


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
            new_token["id"] = old_token_id  # Assign old_token_id to new_token["id"]

        childrens = new_token.get("children", [])  # Use get to avoid KeyError
        if childrens:
            for i, child in enumerate(childrens):
                if is_uuid4(child):
                    childrens[i] = id_map.get(
                        child, child
                    )  # Replace child if it's a UUID

    return new_copied_tokens


def is_uuid4(id_string):
    """Check if the provided string is a valid UUID4."""
    try:
        val = uuid.UUID(id_string, version=4)
    except ValueError:
        return False
    return str(val) == id_string


def find_differences(old_tokens, new_tokens):
    def compare_tokens(old_token, new_token):
        differences = {}

        if old_token["tag"] != new_token["tag"]:
            differences["tag"] = new_token["tag"]

        if old_token["id"] != new_token["id"]:
            differences["id"] = new_token["id"]

        if old_token["class"] != new_token["class"]:
            differences["class"] = new_token["class"]

        if old_token["attributes"] != new_token["attributes"]:
            differences["attributes"] = new_token["attributes"]

        if old_token["custom_attributes"] != new_token["custom_attributes"]:
            differences["custom_attributes"] = new_token["custom_attributes"]

        if old_token["value"] != new_token["value"]:
            differences["value"] = new_token["value"]

        if old_token["isVisible"] != new_token["isVisible"]:
            differences["isVisible"] = new_token["isVisible"]

        # Handle children differences
        old_children_set = set(old_token["children"])
        new_children_set = set(new_token["children"])

        added_children = new_children_set - old_children_set
        removed_children = old_children_set - new_children_set

        if added_children or removed_children:
            differences["children"] = {
                "added": list(added_children),
                "removed": list(removed_children),
            }

            # Add full tag details for added elements
            if added_children:
                differences["elements"] = [
                    next(child for child in new_tokens if child["id"] == added_child_id)
                    for added_child_id in added_children
                ]

        return differences if differences else None

    old_copied_tokens = [token.copy() for token in old_tokens]
    new_copied_tokens = [token.copy() for token in new_tokens]

    id_map = {
        new["id"]: old["id"] for old, new in zip(old_copied_tokens, new_copied_tokens)
    }

    for new_token in new_copied_tokens:
        old_token_id = id_map.get(new_token["id"])
        new_token_id = new_token["id"]

        if is_uuid4(new_token_id) and is_uuid4(old_token_id):
            new_token_id = old_token_id

        new_token["id"] = new_token_id

        new_token["children"] = [
            id_map.get(child_id, child_id) for child_id in new_token["children"]
        ]

    changes = []
    for old_token, new_token in zip(old_copied_tokens, new_copied_tokens):
        token_diff = compare_tokens(old_token, new_token)
        if token_diff:
            changes.append({"id": old_token["id"], "changes": token_diff})

    return changes if changes else None


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
        print("File changed:", event.src_path)

        old_tokens = self.watcher.old_tokens
        decoy_html_tokens = TemplateTokenizer(self.get_file_content()).tokens

        diff = find_differences(old_tokens, decoy_html_tokens)
        if diff:
            changed_ids = replace_id(old_tokens, decoy_html_tokens)
            # print("old:", old_tokens)
            # print("new:", decoy_html_tokens)

            # print("changed_ids:", changed_ids)
            # print("diff:", diff)

            self.watcher.old_tokens = changed_ids
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
