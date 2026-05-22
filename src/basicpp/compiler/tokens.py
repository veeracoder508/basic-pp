from enum import StrEnum, auto


class Keywords(StrEnum):
    """Enum representing reserved keywords in basic-pp."""
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    FUNCTION = auto()
    RETURN = auto()
    PRINT = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()

class DataTypes(StrEnum):
    """Enum representing built-in data types in basic-pp."""
    INT = auto()
    FLOAT = auto()
    STRING = auto()
    BOOLEAN = auto()
    VOID = auto()

class ArithmaticOperator(StrEnum): 
    """Enum representing arithmatic operators in basic-pp."""
    PLUS = auto()     # +
    MINUS = auto()    # -
    MULTIPLY = auto() # *
    DIVIDE = auto()   # /
    MODULO = auto()   # %
    EXPONENT = auto() # **

class LogicalOperator(StrEnum):
    """Enum representing logical operators in basic-pp."""
    AND = auto()
    OR = auto()
    NOT = auto()

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
    def __init__(self, type: TokenType, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {self.value}, {self.line}, {self.column})"