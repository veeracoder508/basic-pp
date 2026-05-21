from .tokens import *
from typing import List, Tuple


class Lexer:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens: List[Token] = []
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(source_code)

    def current_char(self):
        if self.pos >= self.length:
            return "\0"
        return self.source_code[self.pos]

    def peek(self, offset: int = 1) -> str:
        idx = self.pos + offset
        if idx >= self.length:
            return "\0"
        return self.source_code[idx]

    def advance(self, steps: int = 1):
        for _ in range(steps):
            if self.pos >= self.length:
                return
            ch = self.source_code[self.pos]
            self.pos += 1
            if ch == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1

    def add_token(self, type: TokenType, value: str):
        token = Token(type, value, self.line, self.column)
        self.tokens.append(token)

    def skip_whitespace(self):
        while True:
            ch = self.current_char()
            if ch in [' ', '\t', '\r', '\n']:
                self.advance()
                continue
            # comments
            if ch == '/' and self.peek() == '/':
                # single-line comment
                self.advance(2)
                while self.current_char() not in ['\n', '\0']:
                    self.advance()
                continue
            if ch == '/' and self.peek() == '*':
                # block comment
                self.advance(2)
                while not (self.current_char() == '*' and self.peek() == '/') and self.current_char() != '\0':
                    self.advance()
                if self.current_char() == '*' and self.peek() == '/':
                    self.advance(2)
                continue
            break

    def read_number(self) -> str:
        start = self.pos
        ch = self.current_char()
        # handle 0x, 0b, 0o prefixes
        if ch == '0' and self.peek().lower() in ('x', 'b', 'o'):
            prefix = self.peek().lower()
            self.advance(2)
            valid = ''
            if prefix == 'x':
                valid = '0123456789abcdefABCDEF'
            elif prefix == 'b':
                valid = '01'
            else:
                valid = '01234567'
            while self.current_char() in valid:
                self.advance()
            return self.source_code[start:self.pos]

        # decimal/float
        has_dot = False
        while True:
            ch = self.current_char()
            if ch.isdigit():
                self.advance()
                continue
            if ch == '.' and not has_dot and self.peek().isdigit():
                has_dot = True
                self.advance()
                continue
            break
        return self.source_code[start:self.pos]

    def read_identifier_or_keyword(self) -> str:
        start = self.pos
        while True:
            ch = self.current_char()
            if ch.isalnum() or ch == '_':
                self.advance()
                continue
            break
        return self.source_code[start:self.pos]

    def read_string(self, quote: str) -> str:
        # assume current char is opening quote
        self.advance()  # consume opening quote
        start = self.pos
        chars = []
        while True:
            ch = self.current_char()
            if ch == '\0':
                raise Exception('Unterminated string')
            if ch == '\\':
                self.advance()
                esc = self.current_char()
                if esc == 'n':
                    chars.append('\n')
                elif esc == 't':
                    chars.append('\t')
                elif esc == 'r':
                    chars.append('\r')
                else:
                    chars.append(esc)
                self.advance()
                continue
            if ch == quote:
                self.advance()
                break
            chars.append(ch)
            self.advance()
        return ''.join(chars)

    def tokenize(self) -> List[Token]:
        single_char_delims = {
            '(': TokenType.DELIMITER,
            ')': TokenType.DELIMITER,
            '{': TokenType.DELIMITER,
            '}': TokenType.DELIMITER,
            '[': TokenType.DELIMITER,
            ']': TokenType.DELIMITER,
            ';': TokenType.DELIMITER,
            ',': TokenType.DELIMITER,
            '.': TokenType.DELIMITER,
            ':': TokenType.DELIMITER,
        }

        # operators of varying lengths, try longest first
        multi_ops = ['===', '!==', '==', '!=', '>=', '<=', '&&', '||', '<<', '>>', '+=', '-=', '*=', '/=', '%=', '**=', '->', '**']

        while self.pos < self.length:
            self.skip_whitespace()
            ch = self.current_char()
            if ch == '\0' or self.pos >= self.length:
                break

            # delimiters
            if ch in single_char_delims:
                self.add_token(single_char_delims[ch], ch)
                self.advance()
                continue

            # numbers
            if ch.isdigit():
                num = self.read_number()
                self.add_token(TokenType.VALUE, num)
                continue

            # identifiers / keywords
            if ch.isalpha() or ch == '_':
                ident = self.read_identifier_or_keyword()
                # check keywords
                if ident.upper() in Keywords.__members__:
                    self.add_token(TokenType.KEYWORD, ident)
                else:
                    self.add_token(TokenType.IDENTIFIER, ident)
                continue

            # strings and chars
            if ch == '"' or ch == "'":
                s = self.read_string(ch)
                self.add_token(TokenType.VALUE, s)
                continue

            # operators (try multi-char)
            matched = False
            for op in sorted(multi_ops, key=len, reverse=True):
                if self.source_code.startswith(op, self.pos):
                    self.add_token(TokenType.OPERATOR, op)
                    self.advance(len(op))
                    matched = True
                    break
            if matched:
                continue

            # single-char operators (default to OPERATOR)
            if ch in '+-*/%<>=!&|^~':
                self.add_token(TokenType.OPERATOR, ch)
                self.advance()
                continue

            # unknown char
            raise Exception(f"Unexpected character '{ch}' at {self.line}:{self.column}")

        # EOF token
        self.add_token(TokenType.EOF, '')
        return self.tokens

