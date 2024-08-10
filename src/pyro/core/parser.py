import os

from .tokenizers.template import TemplateTokenizer
from .tokenizers.python import PythonTokenizer

from .parsers.javascript import JavascriptParser


class PyroParser:
    def __init__(self, module_path):
        self.module_path = module_path
        self.raw_code = ""
        self.html_tokens = ""
        self.python_tokens = ""

        self.html_body = ""

        self.load_code()
        self.tokenize()

    def load_code(self):
        path = os.path.join(os.getcwd(), f"{self.module_path}.pyro")
        with open(path, "r") as f:
            self.raw_code = f.read()

    def tokenize(self):
        self.html_tokens = TemplateTokenizer(self.raw_code)
        self.html_body = self.html_tokens.body
        # self.python_tokens = PythonTokenizer(self.raw_code)
        # print("Python Tokens:", self.python_tokens)
        # javascript_code = JavascriptParser(self.python_tokens)
        # print("Javascript Code:\n", javascript_code)
        # print(self.python_tokens)
        # print("Html Tokens:", self.html_tokens)
