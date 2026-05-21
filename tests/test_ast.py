from basicpp import ast as ast_mod


def test_compile_assignment_and_print_bytecode():
    src = 'x = 1 + 2 * 3 ; PRINT x ;'
    bc = ast_mod.compile_source(src)
    # expected sequence: LOAD_CONST 1, LOAD_CONST 2, LOAD_CONST 3, BINARY_MULTIPLY, BINARY_ADD, STORE_NAME 'x', LOAD_NAME 'x', PRINT_ITEM, PRINT_NEWLINE, RETURN_VALUE
    expected_ops = [
        ('LOAD_CONST', 1),
        ('LOAD_CONST', 2),
        ('LOAD_CONST', 3),
        ('BINARY_MULTIPLY', None),
        ('BINARY_ADD', None),
        ('STORE_NAME', 'x'),
        ('LOAD_NAME', 'x'),
        ('PRINT_ITEM', None),
        ('PRINT_NEWLINE', None),
        ('RETURN_VALUE', None),
    ]
    assert bc['code'] == expected_ops
    # consts should contain 1,2,3
    assert 1 in bc['consts'] and 2 in bc['consts'] and 3 in bc['consts']
    assert 'x' in bc['names']


def test_compile_print_multiple_values():
    src = 'PRINT 1, "two", 3 ;'
    bc = ast_mod.compile_source(src)
    # should load consts and print
    ops = [op for op in bc['code'] if op[0].startswith('LOAD') or op[0].startswith('PRINT')]
    # ensure 3 LOAD_CONST before PRINT_ITEM's
    assert any(op == ('LOAD_CONST', 1) for op in ops)
    assert any(op == ('LOAD_CONST', 'two') for op in ops)
    assert any(op == ('LOAD_CONST', 3) for op in ops)
