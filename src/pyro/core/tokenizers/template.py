import re
import uuid
import json


class TemplateTokenizer:
    def __init__(self, raw_code):
        self.tokens = []
        self.raw_code = raw_code
        self.body = self.extract_template_content()

        self.custom_attributes = [
            "py-if",
            "py-for",
        ]

        self.tokenize()

    def __str__(self) -> str:
        return json.dumps(self.tokens)

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
        return id_match.group(1) if id_match else str(uuid.uuid4())

    def tokenize(self):
        template_content = self.body
        token_pattern = re.compile(r"(<[^>]+>)|([^<]+)")
        tokens = token_pattern.findall(template_content)

        structured_tokens = []
        parent_stack = []

        for token in tokens:
            tag, text_content = token
            text_content = text_content.strip()

            if tag:
                self.handle_tag(tag, parent_stack, structured_tokens)
            elif text_content:
                self.handle_text_content(text_content, parent_stack)

        self.tokens = structured_tokens

    def handle_tag(self, tag, parent_stack, structured_tokens):
        if tag.startswith("</"):
            parent_stack.pop()
            return

        tag_name = re.search(r"<\s*(\w+)", tag).group(1)
        attributes, custom_attrs = self.parse_attributes(tag)
        id_value = self.generate_id(tag)
        classes = re.search(r'class\s*=\s*"([^"]*)"', tag)

        token_structure = {
            "tag": tag_name,
            "id": id_value,
            "class": classes.group(1) if classes else None,
            "parent": parent_stack[-1]["id"] if parent_stack else None,
            "attributes": attributes,
            "custom_attributes": custom_attrs,  # Add custom attributes field
            "value": None,
            "isVisible": True,
        }

        structured_tokens.append(token_structure)
        parent_stack.append(token_structure)

    def handle_text_content(self, text_content, parent_stack):
        if parent_stack:
            reactive_var_match = re.match(r"\{\{\s*(\w+)\s*\}\}", text_content)
            parent_stack[-1]["value"] = {
                "type": "reactive" if reactive_var_match else "text",
                "value": (
                    reactive_var_match.group(1) if reactive_var_match else text_content
                ),
            }


import re
import uuid
import json


class TemplateTokenizer:
    def __init__(self, raw_code):
        self.tokens = []
        self.raw_code = raw_code
        self.body = self.extract_template_content()

        self.custom_attributes = [
            "py-if",
            "py-for",
        ]

        self.tokenize()

    def __str__(self) -> str:
        return json.dumps(self.tokens)

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
        return id_match.group(1) if id_match else str(uuid.uuid4())

    def tokenize(self):
        template_content = self.body
        token_pattern = re.compile(r"(<[^>]+>)|([^<]+)")
        tokens = token_pattern.findall(template_content)

        structured_tokens = []
        parent_stack = []

        for token in tokens:
            tag, text_content = token
            text_content = text_content.strip()

            if tag:
                self.handle_tag(tag, parent_stack, structured_tokens)
            elif text_content:
                self.handle_text_content(text_content, parent_stack)

        self.tokens = structured_tokens

    def handle_tag(self, tag, parent_stack, structured_tokens):
        if tag.startswith("</"):
            parent_stack.pop()
            return

        tag_name = re.search(r"<\s*(\w+)", tag).group(1)
        attributes, custom_attrs = self.parse_attributes(tag)
        id_value = self.generate_id(tag)
        classes = re.search(r'class\s*=\s*"([^"]*)"', tag)

        token_structure = {
            "tag": tag_name,
            "id": id_value,
            "class": classes.group(1) if classes else None,
            "parent": parent_stack[-1]["id"] if parent_stack else None,
            "attributes": attributes,
            "custom_attributes": custom_attrs,
            "value": None,
            "isVisible": True,
            "children": [],
        }

        if parent_stack:
            parent_stack[-1]["children"].append(token_structure)
        else:
            structured_tokens.append(token_structure)

        parent_stack.append(token_structure)

    def handle_text_content(self, text_content, parent_stack):
        if parent_stack:
            reactive_var_match = re.match(r"\{\{\s*(\w+)\s*\}\}", text_content)
            parent_stack[-1]["value"] = {
                "type": "reactive" if reactive_var_match else "text",
                "value": (
                    reactive_var_match.group(1) if reactive_var_match else text_content
                ),
            }

    def generate_body(self):
        def build_body(token):
            tag_open = f"<{token['tag']} id=\"{token['id']}\""
            for attr in token["attributes"]:
                tag_open += f" {attr['name']}=\"{attr['value']}\""
            for custom_attr in token["custom_attributes"]:
                tag_open += f" {custom_attr['name']}=\"{custom_attr['value']}\""
            tag_open += ">"

            content = []
            if token["value"]:
                value_content = token["value"]["value"]
                if token["value"]["type"] == "reactive":
                    content.append(f"{{{{ {value_content} }}}}")
                else:
                    content.append(value_content)

            for child in token["children"]:
                content.append(build_body(child))

            return f"{tag_open}{''.join(content)}</{token['tag']}>"

        return "".join(build_body(token) for token in self.tokens)
