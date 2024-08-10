import json
import re
import tokenize
from io import BytesIO


class PythonTokenizer:
    def __init__(self, raw_code):
        self.tokens = []
        self.raw_code = raw_code
        self.tokenize()

    def __str__(self):
        return json.dumps(self.tokens)

    def __iter__(self):
        return iter(self.tokens)

    def extract_python_content(self):
        python_content = re.search(r"<python>(.*?)</python>", self.raw_code, re.DOTALL)
        return python_content.group(1).strip() if python_content else self.raw_code

    def tokenize(self):
        python_content = self.extract_python_content()

        # Convert the string to bytes for tokenize.tokenize()
        bytes_io = BytesIO(python_content.encode("utf-8"))

        try:
            for tok in tokenize.tokenize(bytes_io.readline):
                token_info = {
                    "type": tokenize.tok_name[tok.type],
                    "string": tok.string,
                    "start": (tok.start[0], tok.start[1]),
                    "end": (tok.end[0], tok.end[1]),
                }
                self.tokens.append(token_info)
        except tokenize.TokenError as e:
            print(f"Tokenization Error: {e}")

    def get_tokens(self):
        return self.tokens
