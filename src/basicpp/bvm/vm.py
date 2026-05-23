"""
Basic Virtual Machine (BVM) implementation for Basic++.
This module executes the bytecode produced by the compiler.
"""

import sys
from typing import Any, List, Dict, Tuple


class BVM:
    def __init__(self, bytecode: Dict[str, Any]):
        """
        Initializes the VM with the bytecode dictionary.

        Args:
            bytecode (dict): Dictionary containing 'code', 'consts', and 'names'.
        """
        self.code: List[Tuple[str, Any]] = bytecode.get('code', [])
        self.consts: List[Any] = bytecode.get('consts', [])
        self.names: List[str] = bytecode.get('names', [])
        
        self.stack: List[Any] = []
        self.variables: Dict[str, Any] = {}
        self.ip = 0  # Instruction Pointer
        self.labels: Dict[str, int] = {}
        
        self._resolve_labels()

    def _resolve_labels(self):
        """Pre-pass to map labels to instruction indices."""
        for i, (op, arg) in enumerate(self.code):
            if op == 'LABEL':
                self.labels[arg] = i

    def push(self, value: Any):
        self.stack.append(value)

    def pop(self) -> Any:
        if not self.stack:
            raise RuntimeError("Stack underflow")
        return self.stack.pop()

    def run(self):
        """Main execution loop."""
        while self.ip < len(self.code):
            op, arg = self.code[self.ip]
            
            if op == 'RETURN_VALUE':
                break
            
            elif op == 'LOAD_CONST':
                self.push(arg)
            
            elif op == 'LOAD_NAME':
                if arg not in self.variables:
                    raise NameError(f"Variable '{arg}' is not defined")
                self.push(self.variables[arg])
            
            elif op == 'STORE_NAME':
                self.variables[arg] = self.pop()
            
            elif op == 'READ_INPUT':
                val = input()
                # Attempt basic type conversion
                try:
                    if '.' in val: val = float(val)
                    else: val = int(val)
                except ValueError:
                    pass
                self.push(val)

            elif op == 'PRINT_ITEM':
                print(self.pop(), end=' ')
            
            elif op == 'PRINT_NEWLINE':
                print()

            elif op == 'BINARY_ADD':
                b = self.pop()
                a = self.pop()
                self.push(a + b)
            
            elif op == 'BINARY_SUBTRACT':
                b = self.pop()
                a = self.pop()
                self.push(a - b)
            
            elif op == 'BINARY_MULTIPLY':
                b = self.pop()
                a = self.pop()
                self.push(a * b)
            
            elif op == 'BINARY_TRUE_DIVIDE':
                b = self.pop()
                a = self.pop()
                self.push(a / b)
            
            elif op == 'BINARY_MODULO':
                b = self.pop()
                a = self.pop()
                self.push(a % b)

            elif op.startswith('COMPARE_'):
                b = self.pop()
                a = self.pop()
                if op == 'COMPARE_EQ': self.push(a == b)
                elif op == 'COMPARE_NEQ': self.push(a != b)
                elif op == 'COMPARE_GT': self.push(a > b)
                elif op == 'COMPARE_LT': self.push(a < b)
                elif op == 'COMPARE_GTE': self.push(a >= b)
                elif op == 'COMPARE_LTE': self.push(a <= b)

            elif op == 'UNARY_NEGATIVE':
                self.push(-self.pop())

            elif op == 'UNARY_POSITIVE':
                self.push(+self.pop())

            elif op == 'UNARY_NOT':
                self.push(not self.pop())

            elif op == 'UNARY_INVERT':
                self.push(~self.pop())

            elif op == 'LOGICAL_AND':
                b = self.pop()
                a = self.pop()
                self.push(a and b)
            
            elif op == 'LOGICAL_OR':
                b = self.pop()
                a = self.pop()
                self.push(a or b)

            elif op == 'JUMP':
                self.ip = self.labels[arg]
                continue
            
            elif op == 'JUMP_IF_FALSE':
                condition = self.pop()
                if not condition:
                    self.ip = self.labels[arg]
                    continue

            elif op == 'LABEL':
                pass # Labels are handled in pre-pass

            else:
                raise RuntimeError(f"Unknown opcode: {op}")

            self.ip += 1


def main():
    from basicpp.compiler import compile_source

    # A small integrated test to verify the BVM works as expected
    test_src = """
    START
    SET x $INT = 10 ;
    SET y $INT = 5 ;
    result = (x + y) * 2 ;
    PRINT "The result of (10 + 5) * 2 is:", result ;
    END
    """
    print("Running BVM Self-Test...")
    bc = compile_source(test_src)
    BVM(bc).run()

if __name__ == '__main__':
    main()
    