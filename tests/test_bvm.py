import pytest
from basicpp.compiler import compile_source
import builtins
from basicpp.bvm import BVM

def run_src(src):
    """Helper to compile and run source code."""
    bc = compile_source(src)
    vm = BVM(bc)
    vm.run()
    return vm

def test_arithmetic_execution(capsys):
    src = "START PRINT (1 + 2) * 3 ; END"
    run_src(src)
    captured = capsys.readouterr()
    assert captured.out.strip() == "9"

def test_variable_assignment(capsys):
    src = """
    START
    x = 10 ;
    y = x + 5 ;
    PRINT y ;
    END
    """
    run_src(src)
    captured = capsys.readouterr()
    assert captured.out.strip() == "15"

def test_if_else_logic(capsys):
    src = """
    START
    x = 10 ;
    IF x > 5 THEN
        PRINT "High" ;
    ELSE
        PRINT "Low" ;
    ENDIF ;
    END
    """
    run_src(src)
    captured = capsys.readouterr()
    assert "High" in captured.out

def test_unary_operators(capsys):
    src = "START x = 10 ; PRINT -x ; END"
    run_src(src)
    captured = capsys.readouterr()
    assert captured.out.strip() == "-10"

def test_comparison_ops(capsys):
    src = """
    START
    PRINT 10 == 10 ;
    PRINT 10 != 5 ;
    PRINT 5 < 10 ;
    PRINT 10 > 5 ;
    END
    """
    run_src(src)
    captured = capsys.readouterr()
    outputs = captured.out.split()
    assert all(o == "True" for o in outputs)

def test_logical_ops(capsys):
    src = """
    START
    PRINT 5 < 10 && 10 > 5 ;
    PRINT 5 < 10 || 10 < 5 ;
    END
    """
    run_src(src)
    captured = capsys.readouterr()
    output = captured.out.strip()
    assert output == "True \nTrue"

def test_for_next_logic(capsys):
    src = """
    START
    i = 0 ;
    FOR i = 0 TO 4
        PRINT i ;
    NEXT i ;
    END
    """
    run_src(src)
    captured = capsys.readouterr()
    outputs = captured.out.split()
    assert outputs == ["0", "1", "2", "3", "4"]

def test_for_next_logic(capsys):
    src = """
    START
    i = 0 ;
    FOR i = 1 TO 10 STEP 2
        PRINT i ;
    NEXT i ;
    END
    """
    run_src(src)
    captured = capsys.readouterr()
    outputs = captured.out.split()
    assert outputs == ["1", "3", "5", "7", "9"]

def test_input_statement_int(capsys, monkeypatch):
    src = """
    START
    INPUT num $INT ;
    PRINT "You entered:", num ;
    END
    """
    monkeypatch.setattr(builtins, 'input', lambda _: "123")
    run_src(src)
    captured = capsys.readouterr()
    assert captured.out.strip() == "You entered: 123"

def test_input_statement_string(capsys, monkeypatch):
    src = """
    START
    INPUT name $STR ;
    PRINT "Hello,", name ;
    END
    """
    monkeypatch.setattr(builtins, 'input', lambda _: "World")
    run_src(src)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World"

def test_println_statement(capsys):
    src = """
    START
    PRINTLN "Hello, World!" ;
    PRINTLN "This is a new line!!!" ;
    END
    """
    run_src(src)
    captured = capsys.readouterr()
    assert captured.out.strip() == "Hello, World! \nThis is a new line!!!"
