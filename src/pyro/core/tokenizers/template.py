import re
import json


class TemplateTokenizer:
    def __init__(self, raw_code):
        self.tokens = []
        self.id_counter = 1
        self.raw_code = raw_code
        self.body = self.extract_template_content()

        self.custom_attributes = [
            "py-if",
            "py-for",
        ]

        self.tokenize()

    def __str__(self) -> str:
        return json.dumps(self.tokens, indent=4)

    def __iter__(self):
        return iter(self.tokens)

    def extract_template_content(self):
        template_content = re.search(
            r"<template>(.*?)</template>", self.raw_code, re.DOTALL
        )
        return template_content.group(1).strip() if template_content else ""

    def parse_attributes(self, tag):
        attributes = []
        custom_attrs = []
        attr_pattern = re.compile(r'(\w[\w-]*)\s*=\s*"([^"]*)"')

        for match in attr_pattern.finditer(tag):
            attr_name, attr_value = match.groups()
            if (
                attr_name not in ["id", "class"]
                and attr_name not in self.custom_attributes
            ):
                attributes.append({"name": attr_name, "value": attr_value})

            if attr_name in self.custom_attributes:
                custom_attrs.append({"name": attr_name, "value": attr_value})

        return attributes, custom_attrs

    def generate_id(self, tag):
        id_match = re.search(r'id\s*=\s*"([^"]*)"', tag)
        if id_match:
            return id_match.group(1)

        id_value = f"pyroelement:{self.id_counter}"
        self.id_counter += 1
        return id_value

    def tokenize(self):
        template_content = self.body
        token_pattern = re.compile(r"(<[^>]+>)|([^<]+)")
        tokens = token_pattern.findall(template_content)

        structured_tokens = []
        parent_stack = []
        line_num = 1
        col_num = 1

        for token in tokens:
            tag, text_content = token
            text_content = text_content.strip()

            # Track location
            if tag:
                loc = {"line": line_num, "column": col_num}
                self.handle_tag(tag, parent_stack, structured_tokens, loc)
                col_num += len(tag)
            elif text_content:
                loc = {"line": line_num, "column": col_num}
                self.handle_text_content(text_content, parent_stack, loc)
                col_num += len(text_content)

            # Update line and column numbers
            # Count new lines in the content
            for char in tag or text_content:
                if char == "\n":
                    line_num += 1
                    col_num = 1  # Reset column number
                else:
                    col_num += 1

        self.tokens = self.sort_tokens(structured_tokens)

    def handle_tag(self, tag, parent_stack, structured_tokens, loc):
        if tag.startswith("</"):
            parent_stack.pop()
            return

        tag_name = re.search(r"<\s*(\w+)", tag).group(1)
        attributes, custom_attrs = self.parse_attributes(tag)
        id_value = self.generate_id(tag)
        classes = re.search(r'class\s*=\s*"([^"]*)"', tag)

        # Determine the child index for this token
        child_index = (
            len(
                [
                    token
                    for token in structured_tokens
                    if token["parent"]
                    == (parent_stack[-1]["id"] if parent_stack else None)
                ]
            )
            + 1
        )

        token_structure = {
            "tag": tag_name,
            "id": id_value,
            "class": classes.group(1) if classes else None,
            "parent": parent_stack[-1]["id"] if parent_stack else None,
            "attributes": attributes,
            "custom_attributes": custom_attrs,
            "value": None,
            "isVisible": True,
            "location": child_index,
        }

        structured_tokens.append(token_structure)
        parent_stack.append(token_structure)

    def handle_text_content(self, text_content, parent_stack, loc):
        if parent_stack:
            reactive_var_match = re.match(r"\{\{\s*(\w+)\s*\}\}", text_content)
            parent_stack[-1]["value"] = {
                "type": "reactive" if reactive_var_match else "text",
                "value": (
                    reactive_var_match.group(1) if reactive_var_match else text_content
                ),
            }

    def sort_tokens(self, tokens):
        sorted_tokens = []
        token_dict = {token["id"]: token for token in tokens}

        def add_token_with_parents(token_id):
            token = token_dict[token_id]
            if token["parent"]:
                add_token_with_parents(token["parent"])
            if token not in sorted_tokens:
                sorted_tokens.append(token)

        for token in tokens:
            add_token_with_parents(token["id"])

        return sorted_tokens

    def generate_body(self):
        def build_body(token):
            tag_open = f"<{token['tag']} id=\"{token['id']}\""
            for attr in token["attributes"]:
                tag_open += f" {attr['name']}=\"{attr['value']}\""
            for custom_attr in token["custom_attributes"]:
                tag_open += f" {custom_attr['name']}=\"{custom_attr['value']}\""
            tag_open += ">"

            # Create a temporary variable to hold child content
            child_content = []

            # Iterate through tokens to find children of the current token
            for child in self.tokens:
                if child["parent"] == token["id"]:
                    child_content.append(build_body(child))  # Recursively build child

            # Add the value if it exists
            if token["value"]:
                value_content = token["value"]["value"]
                if token["value"]["type"] == "reactive":
                    child_content.append(f"{{{{ {value_content} }}}}")
                else:
                    child_content.append(value_content)

            # Close the tag with children inside
            return f"{tag_open}{''.join(child_content)}</{token['tag']}>"

        # Start building the body from the root tokens
        return "".join(
            build_body(token) for token in self.tokens if token["parent"] is None
        )
