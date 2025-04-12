import re
import json
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Token class to represent different types of tokens
class Token:
    def __init__(self, type_, value, line, column):
        self.type = type_
        self.value = value
        self.line = line
        self.column = column

    def to_dict(self):
        return {
            "type": self.type,
            "value": self.value,
            "line": self.line,
            "column": self.column
        }

# Lexer class
class Lexer:
    def __init__(self):
        self.token_specification = [
            ('PREPROCESSOR', r'#\s*include\s*[<"][^>"]+[>"]'),  # #include<...> or #include "..."
            ('COMMENT',      r'//.*'),                          # Single-line comment
            ('MULTICOMMENT', r'/\*[\s\S]*?\*/'),                # Multi-line comment
            ('STRING',       r'"[^"\n]*"'),                     # Double-quoted string
            ('CHAR',         r"'.'"),                           # Character literal
            ('NUMBER',       r'\d+(\.\d*)?'),                   # Integer or decimal number
            ('ID',           r'[A-Za-z_]\w*'),                  # Identifiers
            ('OP',           r'\+\+|--|==|!=|<=|>=|&&|\|\||[+\-*/%<>=!&|]'),  # Operators
            ('DELIM',        r'[;,]'),                          # Delimiters ; ,
            ('BRACE',        r'[{}()\[\]]'),                    # Brackets and braces
            ('NEWLINE',      r'\n'),                            # Newlines
            ('SKIP',         r'[ \t\r]+'),                      # Whitespace
            ('MISMATCH',     r'.'),                             # Anything else
        ]

        self.keywords = {
            'int', 'float', 'double', 'char', 'void',
            'if', 'else', 'while', 'for', 'return', 'break', 'continue',
            'struct', 'class', 'include', 'define', 'main', 'printf'
        }

    def tokenize(self, code):
        self.tokens = []
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_specification)
        line_num = 1
        line_start = 0

        for mo in re.finditer(tok_regex, code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - line_start

            if kind == 'NEWLINE':
                line_start = mo.end()
                line_num += 1
                continue
            elif kind in {'SKIP', 'COMMENT', 'MULTICOMMENT'}:
                continue
            elif kind == 'ID' and value in self.keywords:
                kind = 'KEYWORD'
            elif kind == 'MISMATCH':
                raise RuntimeError(f"{value!r} unexpected on line {line_num}")

            self.tokens.append(Token(kind, value, line_num, column))

        return self.tokens

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/tokenize', methods=['POST'])
def tokenize():
    try:
        code = request.json.get('code', '')
        lexer = Lexer()
        tokens = lexer.tokenize(code)
        return jsonify([token.to_dict() for token in tokens])
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
