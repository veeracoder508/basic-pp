import types
import sys
import importlib.util
import pytest
import pathlib
from basicpp import tokens as tokens_mod
from basicpp import lexer as lexer_mod


def test_simple_tokens_and_positions():
    src = 'x = 42 ;\nPRINT "hi" ;'
    lex = lexer_mod.Lexer(src)
    toks = lex.tokenize()

    # find meaningful tokens (ignore EOF at end)
    values = [(t.type, t.value, t.line, t.column) for t in toks[:-1]]

    # expected sequence: ID x, OP =, VALUE 42, DELIM ;, KEYWORD PRINT, VALUE hi, DELIM ;
    assert values[0][0] == tokens_mod.TokenType.IDENTIFIER
    assert values[0][1] == 'x'
    assert (values[0][2], values[0][3]) == (1, 1)

    assert values[1][0] == tokens_mod.TokenType.OPERATOR
    assert values[1][1] == '='

    assert values[2][0] == tokens_mod.TokenType.VALUE
    assert values[2][1] == '42'

    assert values[3][0] == tokens_mod.TokenType.DELIMITER
    assert values[3][1] == ';'

    assert values[4][0] == tokens_mod.TokenType.KEYWORD
    assert values[4][1].upper() == 'PRINT'
    # PRINT should be at line 2
    assert values[4][2] == 2

    assert values[5][0] == tokens_mod.TokenType.VALUE
    assert values[5][1] == 'hi'

    assert values[6][0] == tokens_mod.TokenType.DELIMITER
    assert values[6][1] == ';'


def test_comments_and_numeric_prefixes():
    src = 'a = 0xFF ; b = 0b1010 ; // end comment\n c = 0o77 ;'
    lex = lexer_mod.Lexer(src)
    toks = lex.tokenize()
    vals = [ (t.type, t.value) for t in toks if t.type != tokens_mod.TokenType.EOF]

    # expect identifiers and values present
    assert ('IDENTIFIER' not in str(vals)) is False  # trivial check tokens exist
    # check hex, bin, octal values present
    assert any(v == '0xFF' for (_t,v) in vals)
    assert any(v == '0b1010' for (_t,v) in vals)
    assert any(v == '0o77' for (_t,v) in vals)


def test_unterminated_string_error_reports_position():
    src = 'PRINT "unterminated'
    lex = lexer_mod.Lexer(src)
    with pytest.raises(Exception) as exc:
        lex.tokenize()
    assert 'Unterminated string' in str(exc.value)
    # should include starting position
    assert ':' in str(exc.value)
