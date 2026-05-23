import pytest
from basicpp.compiler import compile_source
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