"""
Lexical analyzer (Lexer) for Basic++.
This module is responsible for taking the source code as input and
producing a stream of tokens, which are then used by the parser.
"""

from .tokens import *
from typing import List, Tuple
from pprint import pprint


class Lexer:
    def __init__(self, source_code: str):
        """
        Initializes the Lexer with the source code.

        Args:
            source_code (str): The Basic++ source code to tokenize.
        
        Attributes:
            source_code (str): The input source code.
            tokens (List[Token]): A list to store the generated tokens.
            pos (int): Current position in the source code.
            line (int): Current line number.
            column (int): Current column number.
        """
        self.source_code = source_code
        self.tokens: List[Token] = []
        self.pos = 0
        self.line = 1
        self.column = 1
        self.length = len(source_code)

    def current_char(self):
        """
        Returns the character at the current position without advancing.
        Returns '\0' if at the end of the source code.
        """
        if self.pos >= self.length:
            return "\0"
        return self.source_code[self.pos]

    def peek(self, offset: int = 1) -> str:
        """
        Peeks at a character ahead of the current position by a given offset.
        Returns '\0' if peeking beyond the end of the source code.

        Args:
            offset (int): The number of characters to peek ahead.
        """
        idx = self.pos + offset
        if idx >= self.length:
            return "\0"
        return self.source_code[idx]

    def advance(self, steps: int = 1):
        for _ in range(steps):
            """
            Advances the lexer's position by a given number of steps.
            Updates line and column numbers accordingly.

            Args:
                steps (int): The number of characters to advance.
            """
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
        """
        Creates a new Token and adds it to the list of tokens.

        Args:
            type (TokenType): The type of the token.
            value (str): The literal value of the token.
        """
        token = Token(type, value, self.line, self.column)
        self.tokens.append(token)

    def skip_whitespace(self):
        """
        Skips over whitespace characters and comments (single-line and block)."""
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
                # Loop until end of block comment or EOF
                while not (self.current_char() == '*' and self.peek() == '/') and self.current_char() != '\0': 
                    self.advance()
                # If we found the closing */, consume it
                if self.current_char() == '*' and self.peek() == '/':
                    self.advance(2)
                # If we reached EOF without closing comment, it's an error, but lexer will catch '\0' later
                elif self.current_char() == '\0':
                    # Optionally raise an error here for unterminated block comment
                    pass 
                continue
            break

    def read_number(self) -> str:
        start = self.pos
        start_line = self.line
        start_col = self.column
        """
        Reads a number literal, supporting decimal, hexadecimal, binary, and octal prefixes.

        Returns:
            Tuple[str, int, int]: The number string, starting line, and starting column."""
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
            return self.source_code[start:self.pos], start_line, start_col

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
        return self.source_code[start:self.pos], start_line, start_col

    def read_identifier_or_keyword(self) -> str:
        start = self.pos
        start_line = self.line
        start_col = self.column
        """
        Reads an identifier or a keyword.

        Returns:
            Tuple[str, int, int]: The identifier/keyword string, starting line, and starting column."""
        while True:
            ch = self.current_char()
            if ch.isalnum() or ch == '_':
                self.advance()
                continue
            break
        return self.source_code[start:self.pos], start_line, start_col

    def read_string(self, quote: str) -> str:
        """
        Reads a string literal, handling escape sequences.

        Args:
            quote (str): The type of quote used (single or double).
        Returns:
            Tuple[str, int, int]: The unquoted string content, starting line, and starting column."""
        # assume current char is opening quote
        start_line = self.line
        start_col = self.column
        self.advance()  # consume opening quote
        chars = []
        while True:
            ch = self.current_char()
            if ch == '\0':
                raise Exception(f"Unterminated string starting at {start_line}:{start_col}")
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
        return ''.join(chars), start_line, start_col

    def tokenize(self) -> List[Token]:
        """
        Tokenizes the entire source code into a list of Tokens.
        """
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

        # Collect all possible operator strings from enums
        all_operators = []
        for op_enum in [ArithmaticOperator, LogicalOperator, BitwiseOperator, ComparisonOperator, AssignmentOperator, MiscOperator]:
            for member in op_enum.__members__.values():
                # For auto() assigned enums, the value is the member name itself
                # For manually assigned enums, the value is the string
                if isinstance(member.value, str):
                    all_operators.append(member.value)
                else:
                    # Handle cases like PLUS = auto() where value is 'PLUS'
                    # and we need to map it to '+'
                    # This requires a mapping or more explicit enum values
                    # For now, let's assume explicit string values for operators
                    # or rely on the single-char check for simple ones.
                    # The current tokens.py uses auto() for simple ops, and explicit for multi-char.
                    # So, we need to add the single char representations here.
                    pass
        
        # Add single character representations for auto() assigned operators
        all_operators.extend(['+', '-', '*', '/', '%', '=', '<', '>', '!', '&', '|', '^', '~'])
        
        # Sort operators by length in descending order to match multi-character operators first
        sorted_operators = sorted(list(set(all_operators)), key=len, reverse=True)

        while self.pos < self.length:
            self.skip_whitespace()
            ch = self.current_char()
            if ch == '\0' or self.pos >= self.length:
                break

            # delimiters
            if ch in single_char_delims:
                start_line, start_col = self.line, self.column
                self.add_token(single_char_delims[ch], ch)
                # adjust token position to the starting location
                self.tokens[-1].line = start_line
                self.tokens[-1].column = start_col
                self.advance()
                continue

            # numbers
            if ch.isdigit():
                num, sline, scol = self.read_number()
                self.add_token(TokenType.VALUE, num)
                self.tokens[-1].line = sline
                self.tokens[-1].column = scol
                continue

            # identifiers / keywords
            if ch.isalpha() or ch == '_':
                ident, sline, scol = self.read_identifier_or_keyword()
                # check keywords
                if ident.upper() in Keywords.__members__:
                    self.add_token(TokenType.KEYWORD, ident)
                else:
                    self.add_token(TokenType.IDENTIFIER, ident)
                self.tokens[-1].line = sline
                self.tokens[-1].column = scol
                continue

            # type markers like $STRING
            if ch == '$':
                start_line, start_col = self.line, self.column
                # consume '$'
                self.advance()
                ident, sline, scol = self.read_identifier_or_keyword()
                val = '$' + ident
                self.add_token(TokenType.KEYWORD, val)
                # set token position to where $ started
                self.tokens[-1].line = start_line
                self.tokens[-1].column = start_col
                continue

            # strings and chars
            if ch == '"' or ch == "'":
                s, sline, scol = self.read_string(ch)
                self.add_token(TokenType.VALUE, s)
                self.tokens[-1].line = sline
                self.tokens[-1].column = scol
                continue

            # Operators (try multi-char first, then single-char)
            matched = False
            for op in sorted_operators:
                if self.source_code.startswith(op, self.pos):
                    sline, scol = self.line, self.column
                    self.add_token(TokenType.OPERATOR, op)
                    self.tokens[-1].line = sline
                    self.tokens[-1].column = scol
                    self.advance(len(op))
                    # Special handling for 'sizeof' keyword which is in MiscOperator
                    if op == 'sizeof':
                        self.tokens[-1].type = TokenType.KEYWORD
                    matched = True
                    break
            if matched: # If an operator was matched, continue to the next character
                continue

            # unknown char
            raise Exception(f"Unexpected character '{ch}' at {self.line}:{self.column}")

        # EOF token
        self.add_token(TokenType.EOF, '')
        self.tokens[-1].line = self.line
        self.tokens[-1].column = self.column
        return self.tokens

def main():
    src = 'x = 1 + 2 * 3 ; PRINT x ; PRINT 1 == 1 ;'

    lex = Lexer(src)
    toks = lex.tokenize()

    pprint(toks)


if __name__ == "__main__":
    main()
