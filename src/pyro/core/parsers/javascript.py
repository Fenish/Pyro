class JavascriptParser:
    def __init__(self, python_tokens):
        self.tokens = list(python_tokens)
        self.js_code = ""
        self.indentation = 0
        self.declared_variables = set()
        self.declared_functions = set()
        self.current_scope = ["global"]
        self.function_depth = 0
        self.transpile()

    def __str__(self):
        return self.js_code

    def transpile(self):
        self.js_code = ""
        i = 0
        while i < len(self.tokens):
            token = self.tokens[i]
            if token["type"] == "NAME" and token["string"] == "def":
                i = self.process_function(i)
            else:
                self.process_token(token)
                i += 1
        return self.js_code.strip()

    def process_function(self, start_index):
        self.function_depth += 1
        function_tokens = []
        bracket_count = 0
        i = start_index
        while i < len(self.tokens):
            token = self.tokens[i]
            if token["string"] == ":":
                bracket_count += 1
            elif token["type"] == "DEDENT":
                bracket_count -= 1
                if bracket_count == 0:
                    break
            function_tokens.append(token)
            i += 1

        # Process function definition
        self.js_code += "function "
        function_name = function_tokens[1]["string"]
        self.declared_functions.add(function_name)
        for token in function_tokens[1:]:  # Skip 'def'
            if token["string"] == ":":
                self.js_code += " {"
                self.indentation += 2
                self.js_code += "\n" + " " * self.indentation
            elif token["type"] == "NEWLINE":
                self.js_code += "\n" + " " * self.indentation
            else:
                self.process_token(token)

        # Close function
        self.indentation -= 2
        self.js_code += "\n" + " " * self.indentation + "}"
        self.function_depth -= 1

        return i

    def process_token(self, token):
        if token["type"] == "NAME":
            self.process_name(token)
        elif token["type"] == "STRING":
            self.js_code += token["string"]
        elif token["type"] == "NUMBER":
            self.js_code += token["string"]
        elif token["type"] == "OP":
            self.process_operator(token)
        elif token["type"] == "NEWLINE":
            self.js_code += "\n" + " " * self.indentation

    def process_name(self, token):
        if token["string"] == "print":
            self.js_code += "console.log"
        elif token["string"] in ["True", "False"]:
            self.js_code += token["string"].lower()
        elif token["string"] == "None":
            self.js_code += "null"
        else:
            var_name = token["string"]
            scope_var = f"{'.'.join(self.current_scope)}.{var_name}"
            if (
                scope_var not in self.declared_variables
                and self.function_depth == 0
                and var_name not in self.declared_functions
            ):
                self.js_code += "let "
                self.declared_variables.add(scope_var)
            self.js_code += var_name

    def process_operator(self, token):
        if token["string"] == "(":
            self.js_code += "("
        elif token["string"] == ")":
            self.js_code += ")"
        elif token["string"] == "=":
            self.js_code += " = "
