import os

from .tokenizers.template import TemplateTokenizer
from .tokenizers.python import PythonTokenizer


class PyroParser:
    def __init__(self, module_path):
        self.module_path = module_path
        self.raw_code = ""
        self.html_tokens = ""
        self.python_tokens = ""

        self.html_body = ""

        self.tokenize()

    def load_code(self):
        path = os.path.join(os.getcwd(), f"{self.module_path}.pyro")
        with open(path, "r") as f:
            return f.read()

    def tokenize(self):
        self.raw_code = self.load_code()
        tokenizer = TemplateTokenizer(self.raw_code)

        self.html_tokens = tokenizer.tokens
        self.html_body = tokenizer.generate_body()
        # self.python_tokens = PythonTokenizer(self.raw_code)
        # print("Python Tokens:", self.python_tokens)
        # javascript_code = JavascriptParser(self.python_tokens)
        # print("Javascript Code:\n", javascript_code)
        # print(self.python_tokens)
        # print("Html Tokens:", self.html_tokens)
