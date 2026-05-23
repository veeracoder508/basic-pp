"""
Token definitions for Basic++.
This module defines all reserved keywords, operators, delimiters, and the Token container class.
"""

from enum import StrEnum, auto


class Keywords(StrEnum):
    """Enum representing reserved keywords in basic-pp."""
    START = auto()
    END = auto()
    SET = auto()
    INPUT = auto()
    IF = auto()
    THEN = auto()
    ELSE = auto()
    ENDIF = auto()
    GOTO = auto()
    WHILE = auto()
    FOR = auto()
    TO = auto()
    STEP = auto()
    NEXT = auto()
    FUNCTION = auto()
    RETURN = auto()
    PRINT = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    # Type keywords as used with $ prefix
    STR = auto()
    INT = auto()
    BOOL = auto()
    FLOAT = auto()
    BIN = auto()
    HEX = auto()
    OCT = auto()
    CHAR = auto()

class DataTypes(StrEnum):
    """Enum representing built-in data types in basic-pp."""
    INT = "INT"
    FLOAT = "FLOAT"
    STRING = "STR"
    BOOLEAN = "BOOL"
    BINARY = "BIN"
    HEX = "HEX"
    OCTAL = "OCT"
    CHARACTER = "CHAR"
    VOID = auto()

class ArithmaticOperator(StrEnum): 
    """Enum representing arithmetic operators in basic-pp."""
    PLUS = auto()     # +
    MINUS = auto()    # -
    MULTIPLY = auto() # *
    DIVIDE = auto()   # /
    MODULO = auto()   # %
    EXPONENT = auto() # ** 

class LogicalOperator(StrEnum):
    """Enum representing logical operators in basic-pp."""
    AND = "&&"
    OR = "||"
    NOT = "!"

class BitwiseOperator(StrEnum):
    """Enum representing bitwise operators in basic-pp."""
    AND = "&"
    OR = "|"
    XOR = "^"
    NOT = "~"
    LSHIFT = "<<"
    RSHIFT = ">>"

class ComparisonOperator(StrEnum):
    """Enum representing comparison operators in basic-pp."""
    EQ = auto()  # ==
    NEQ = auto() # !=
    LT = auto()  # <
    GT = auto()  # >
    LTE = auto() # <=
    GTE = auto() # >=

class AssignmentOperator(StrEnum):
    """Enum representing assignment operators in basic-pp."""
    ASSIGN = auto()     # =
    ADD_ASSIGN = auto() # +=
    SUB_ASSIGN = auto() # -=
    MUL_ASSIGN = auto() # *=
    DIV_ASSIGN = auto() # /=
    MOD_ASSIGN = auto() # %=
    EXP_ASSIGN = auto() # **=

class MiscOperator(StrEnum):
    """Special or miscellaneous operators."""
    ADDRESS = "&"
    DEREF = "*"
    DOT = "."
    ARROW = "->"
    COMMA = ","
    SIZEOF = "sizeof"

class Delimiters(StrEnum):
    """Enum representing delimiters in basic-pp."""
    LEFT_PAREN = auto()    # (
    RIGHT_PAREN = auto()   # )
    LEFT_BRACE = auto()    # {
    RIGHT_BRACE = auto()   # }
    LEFT_BRACKET = auto()  # [
    RIGHT_BRACKET = auto() # ]
    SEMICOLON = auto()     # ;
    COMMA = auto()         # ,
    DOT = auto()           # .
    COLON = auto()         # :


class TokenType(StrEnum):
    """Enum representing the types of tokens in the language."""
    KEYWORD = auto()
    IDENTIFIER = auto()
    VALUE = auto()
    OPERATOR = auto()
    DELIMITER = auto()
    EOF = auto()


class Token:
    """
    A container for a single unit of the source code.
    
    Attributes:
        type (TokenType): The category of the token.
        value (str): The literal string value from the source.
        line (int): The line number where the token appears.
        column (int): The column position where the token begins.
    """
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self) -> str:
        # Using .name for the Enum and quoting the value for clarity
        return f"Token(type={self.type.name}, value='{self.value}', line={self.line}, col={self.column})"