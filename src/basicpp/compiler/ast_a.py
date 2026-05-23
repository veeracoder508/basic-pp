"""
AST and Parser implementation for Basic++.
This module handles the construction of the Abstract Syntax Tree from tokens
and provides an Emitter to generate stack-based bytecode.
"""

import os
from pprint import pprint
from dataclasses import dataclass
from typing import Any, List, Tuple, Dict
from .tokens import Token, TokenType, Keywords
from .lexer import Lexer


# --- AST node definitions ---
@dataclass
class Number:
	value: Any


@dataclass
class String:
	value: str


@dataclass
class Identifier:
	name: str


@dataclass
class BinOp:
	left: Any
	op: str
	right: Any


@dataclass
class Assign:
	target: Identifier
	value: Any


@dataclass
class Print:
	values: List[Any]


@dataclass
class Program:
    body: List[Any]


@dataclass
class Input:
    target: Identifier
    dtype: str | None = None

@dataclass
class IfStmt:
    condition: Any
    then_block: List[Any]
    else_block: List[Any] | None = None

@dataclass
class ForStmt:
    variable: Identifier
    start_val: Any
    end_val: Any
    step_val: Any
    body: List[Any]

@dataclass
class GotoStmt:
    label: str

@dataclass
class LabelStmt:
    name: str

@dataclass
class UnaryOp:
    op: str
    right: Any

@dataclass
class Boolean:
    value: bool

# --- Parser ---
class ParseError(Exception):
	pass


class Parser:
	def __init__(self, tokens: List[Token]):
		self.tokens = tokens
		self.pos = 0

	def current(self) -> Token:
		return self.tokens[self.pos]

	def advance(self):
		if self.pos < len(self.tokens) - 1:
			self.pos += 1
		return self.current()

	def expect(self, ttype: TokenType, value: str = None):
		tok = self.current()
		if tok.type is not ttype:
			raise ParseError(f"Expected {ttype} but got {tok.type} at {tok.line}:{tok.column}")
		if value is not None and tok.value != value:
			raise ParseError(f"Expected '{value}' but got '{tok.value}' at {tok.line}:{tok.column}")
		self.advance()
		return tok

	def parse(self) -> Program:
		stmts = []
		while self.current().type != TokenType.EOF:
			# handle keyword statements
			if self.current().type == TokenType.KEYWORD:
				kw = self.current().value.upper()
				if kw == 'PRINT':
					stmts.append(self.parse_print())
					continue
				if kw == 'SET':
					stmts.append(self.parse_set())
					continue
				if kw == 'INPUT':
					stmts.append(self.parse_input())
					continue
				if kw == 'IF':
					stmts.append(self.parse_if())
					continue
				if kw == 'FOR':
					stmts.append(self.parse_for())
					continue
				if kw == 'GOTO':
					stmts.append(self.parse_goto())
					continue
				# START/END are program markers in the grammar; ignore them
				if kw in ('START', 'END'):
					self.advance()
					continue
			if self.current().type == TokenType.IDENTIFIER:
				# assignment if followed by operator '='
				look = self.tokens[self.pos + 1] if (self.pos + 1) < len(self.tokens) else None
				if look and look.type == TokenType.OPERATOR and look.value == '=':
					stmts.append(self.parse_assign())
					continue
				# Label check: <name>:
				if look and look.type == TokenType.DELIMITER and look.value == ':':
					stmts.append(self.parse_label())
					continue

			raise ParseError(f"Unexpected token {self.current().value} at {self.current().line}:{self.current().column}")
		return Program(stmts)

	def parse_print(self) -> Print:
		self.expect(TokenType.KEYWORD, self.current().value)
		values = []
		while True:
			values.append(self.parse_expr())
			if self.current().type == TokenType.DELIMITER and self.current().value == ',':
				self.advance()
				continue
			break
		# expect semicolon
		if self.current().type == TokenType.DELIMITER and self.current().value == ';':
			self.advance()
		else:
			tok = self.current()
			raise ParseError(f"Expected ';' after PRINT at {tok.line}:{tok.column}")
		return Print(values)

	def parse_assign(self) -> Assign:
		target_tok = self.expect(TokenType.IDENTIFIER)
		target = Identifier(target_tok.value)
		# expect '='
		self.expect(TokenType.OPERATOR, '=')
		value = self.parse_expr()
		# semicolon
		if self.current().type == TokenType.DELIMITER and self.current().value == ';':
			self.advance()
		else:
			tok = self.current()
			raise ParseError(f"Expected ';' after assignment at {tok.line}:{tok.column}")
		return Assign(target, value)

	def parse_set(self) -> Assign:
		# SET <identifier> [$TYPE] = <expr> ;
		self.expect(TokenType.KEYWORD, self.current().value)
		ident_tok = self.expect(TokenType.IDENTIFIER)
		target = Identifier(ident_tok.value)
		# optional type token like $STRING
		dtype = None
		if self.current().type == TokenType.KEYWORD and isinstance(self.current().value, str) and self.current().value.startswith('$'):
			dtype = self.current().value
			self.advance()
		# expect '='
		self.expect(TokenType.OPERATOR, '=')
		value = self.parse_expr()
		# semicolon
		if self.current().type == TokenType.DELIMITER and self.current().value == ';':
			self.advance()
		else:
			tok = self.current()
			raise ParseError(f"Expected ';' after SET at {tok.line}:{tok.column}")
		return Assign(target, value)

	def parse_input(self) -> Input:
		# INPUT <identifier> [$TYPE] ;
		self.expect(TokenType.KEYWORD, self.current().value)
		ident_tok = self.expect(TokenType.IDENTIFIER)
		target = Identifier(ident_tok.value)
		dtype = None
		if self.current().type == TokenType.KEYWORD and isinstance(self.current().value, str) and self.current().value.startswith('$'):
			dtype = self.current().value
			self.advance()
		# semicolon
		if self.current().type == TokenType.DELIMITER and self.current().value == ';':
			self.advance()
		else:
			tok = self.current()
			raise ParseError(f"Expected ';' after INPUT at {tok.line}:{tok.column}")
		return Input(target, dtype)

	def parse_if(self) -> IfStmt:
		self.expect(TokenType.KEYWORD, 'IF')
		condition = self.parse_expr()
		self.expect(TokenType.KEYWORD, 'THEN')
		
		then_block = []
		else_block = None
		
		# Check for single-line vs block-style IF
		# This is a simplified check: if NEXT token isn't a newline/terminator, assume single line
		# For this implementation, we follow method 2 from GRAMMER.md (Block style)
		while not (self.current().type == TokenType.KEYWORD and self.current().value.upper() in ('ELSE', 'ENDIF')):
			then_block.append(self.parse_statement())
			
		if self.current().type == TokenType.KEYWORD and self.current().value.upper() == 'ELSE':
			self.advance()
			else_block = []
			while not (self.current().type == TokenType.KEYWORD and self.current().value.upper() == 'ENDIF'):
				else_block.append(self.parse_statement())
		
		self.expect(TokenType.KEYWORD, 'ENDIF')
		self.expect(TokenType.DELIMITER, ';')
		return IfStmt(condition, then_block, else_block)

	def parse_for(self) -> ForStmt:
		self.expect(TokenType.KEYWORD, 'FOR')
		var_tok = self.expect(TokenType.IDENTIFIER)
		self.expect(TokenType.OPERATOR, '=')
		start_val = self.parse_expr()
		self.expect(TokenType.KEYWORD, 'TO')
		end_val = self.parse_expr()
		
		step_val = Number(1) # default step
		if self.current().type == TokenType.KEYWORD and self.current().value.upper() == 'STEP':
			self.advance()
			step_val = self.parse_expr()
			
		body = []
		while not (self.current().type == TokenType.KEYWORD and self.current().value.upper() == 'NEXT'):
			body.append(self.parse_statement())
			
		self.expect(TokenType.KEYWORD, 'NEXT')
		self.expect(TokenType.IDENTIFIER, var_tok.value)
		self.expect(TokenType.DELIMITER, ';')
		return ForStmt(Identifier(var_tok.value), start_val, end_val, step_val, body)

	def parse_goto(self) -> GotoStmt:
		self.expect(TokenType.KEYWORD, 'GOTO')
		label_tok = self.expect(TokenType.IDENTIFIER)
		self.expect(TokenType.DELIMITER, ';')
		return GotoStmt(label_tok.value)

	def parse_label(self) -> LabelStmt:
		name_tok = self.expect(TokenType.IDENTIFIER)
		self.expect(TokenType.DELIMITER, ':')
		return LabelStmt(name_tok.value)

	def parse_statement(self):
		# Helper to parse a single statement inside blocks
		kw_map = {'PRINT': self.parse_print, 'SET': self.parse_set, 'INPUT': self.parse_input, 'GOTO': self.parse_goto}
		if self.current().type == TokenType.KEYWORD:
			func = kw_map.get(self.current().value.upper())
			if func: return func()
		if self.current().type == TokenType.IDENTIFIER:
			return self.parse_assign()
		raise ParseError(f"Expected statement at {self.current().line}:{self.current().column}")

	# --- Expression parsing with Precedence ---
	def parse_expr(self):
		return self.parse_logical_or()

	def parse_logical_or(self):
		node = self.parse_logical_and()
		while self.current().type == TokenType.OPERATOR and self.current().value == '||':
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_logical_and())
		return node

	def parse_logical_and(self):
		node = self.parse_bitwise_or()
		while self.current().type == TokenType.OPERATOR and self.current().value == '&&':
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_bitwise_or())
		return node

	def parse_bitwise_or(self):
		node = self.parse_bitwise_xor()
		while self.current().type == TokenType.OPERATOR and self.current().value == '|':
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_bitwise_xor())
		return node

	def parse_bitwise_xor(self):
		node = self.parse_bitwise_and()
		while self.current().type == TokenType.OPERATOR and self.current().value == '^':
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_bitwise_and())
		return node

	def parse_bitwise_and(self):
		node = self.parse_equality()
		while self.current().type == TokenType.OPERATOR and self.current().value == '&':
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_equality())
		return node

	def parse_equality(self):
		node = self.parse_comparison()
		while self.current().type == TokenType.OPERATOR and self.current().value in ('==', '!='):
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_comparison())
		return node

	def parse_comparison(self):
		node = self.parse_shift()
		while self.current().type == TokenType.OPERATOR and self.current().value in ('>', '<', '>=', '<='):
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_shift())
		return node

	def parse_shift(self):
		node = self.parse_term()
		while self.current().type == TokenType.OPERATOR and self.current().value in ('<<', '>>'):
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_term())
		return node

	def parse_term(self):
		node = self.parse_factor()
		while self.current().type == TokenType.OPERATOR and self.current().value in ('+', '-'):
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_factor())
		return node

	def parse_factor(self):
		node = self.parse_power()
		while self.current().type == TokenType.OPERATOR and self.current().value in ('*', '/', '%'):
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_power())
		return node

	def parse_power(self):
		node = self.parse_unary()
		while self.current().type == TokenType.OPERATOR and self.current().value == '**':
			op = self.current().value
			self.advance()
			node = BinOp(node, op, self.parse_unary())
		return node

	def parse_unary(self):
		if self.current().type == TokenType.OPERATOR and self.current().value in ('+', '-', '!', '~'):
			op = self.current().value
			self.advance()
			return UnaryOp(op, self.parse_unary())
		return self.parse_primary()

	def parse_primary(self):
		tok = self.current()
		if tok.type == TokenType.KEYWORD:
			if tok.value.upper() == 'TRUE':
				self.advance(); return Boolean(True)
			if tok.value.upper() == 'FALSE':
				self.advance(); return Boolean(False)

		if tok.type == TokenType.VALUE:
			val = tok.value
			self.advance()
			try:
				if isinstance(val, str) and val.startswith(('0x', '0X')):
					num = int(val, 16)
				elif isinstance(val, str) and val.startswith(('0b', '0B')):
					num = int(val, 2)
				elif isinstance(val, str) and val.startswith(('0o', '0O')):
					num = int(val, 8)
				elif '.' in val:
					num = float(val)
				else:
					num = int(val)
				return Number(num)
			except Exception:
				return String(val)

		if tok.type == TokenType.IDENTIFIER:
			self.advance()
			return Identifier(tok.value)

		if tok.type == TokenType.DELIMITER and tok.value == '(':
			self.advance()
			node = self.parse_expr()
			if self.current().type == TokenType.DELIMITER and self.current().value == ')':
				self.advance()
				return node
			raise ParseError(f"Expected ')' at {self.current().line}:{self.current().column}")

		raise ParseError(f"Unexpected primary {tok.value} at {tok.line}:{tok.column}")


# --- Bytecode emitter ---
class Emitter:
	def __init__(self):
		self.consts: List[Any] = []
		self.names: List[str] = []
		self.code: List[Tuple[str, Any]] = []

	def add_const(self, value):
		if value in self.consts:
			return self.consts.index(value)
		self.consts.append(value)
		return len(self.consts) - 1

	def add_name(self, name: str):
		if name in self.names:
			return self.names.index(name)
		self.names.append(name)
		return len(self.names) - 1

	def emit(self, opname: str, arg: Any = None):
		self.code.append((opname, arg))

	def compile(self, node):
		if isinstance(node, Program):
			for stmt in node.body:
				self.compile(stmt)
			self.emit('RETURN_VALUE', None)
		elif isinstance(node, Assign):
			self.compile(node.value)
			idx = self.add_name(node.target.name)
			self.emit('STORE_NAME', node.target.name)
		elif isinstance(node, Input):
			self.emit('READ_INPUT', node.target.name)
			self.emit('STORE_NAME', node.target.name)
		elif isinstance(node, IfStmt):
			self.compile(node.condition)
			label_suffix = str(id(node))
			else_label = f"ELSE_{label_suffix}"
			endif_label = f"ENDIF_{label_suffix}"
			
			self.emit('JUMP_IF_FALSE', else_label if node.else_block else endif_label)
			for stmt in node.then_block: self.compile(stmt)
			
			if node.else_block:
				self.emit('JUMP', endif_label)
				self.emit('LABEL', else_label)
				for stmt in node.else_block: self.compile(stmt)
				self.emit('LABEL', endif_label)
			else:
				self.emit('LABEL', endif_label)
		elif isinstance(node, LabelStmt):
			self.emit('LABEL', node.name)
		elif isinstance(node, GotoStmt):
			self.emit('JUMP', node.label)
		elif isinstance(node, Print):
			for v in node.values:
				self.compile(v)
				self.emit('PRINT_ITEM', None)
			self.emit('PRINT_NEWLINE', None)
		elif isinstance(node, BinOp):
			self.compile(node.left)
			self.compile(node.right)
			opmap = {
				'+': 'BINARY_ADD', '-': 'BINARY_SUBTRACT', '*': 'BINARY_MULTIPLY', 
				'/': 'BINARY_TRUE_DIVIDE', '%': 'BINARY_MODULO', '==': 'COMPARE_EQ',
				'!=': 'COMPARE_NEQ', '>': 'COMPARE_GT', '<': 'COMPARE_LT',
				'>=': 'COMPARE_GTE', '<=': 'COMPARE_LTE', '&&': 'LOGICAL_AND', '||': 'LOGICAL_OR',
				'&': 'BINARY_AND', '|': 'BINARY_OR', '^': 'BINARY_XOR',
				'<<': 'BINARY_LSHIFT', '>>': 'BINARY_RSHIFT',
				'**': 'BINARY_POWER'
			}
			opname = opmap.get(node.op)
			if not opname:
				raise Exception(f'Unsupported binary op {node.op}')
			self.emit(opname, None)
		elif isinstance(node, UnaryOp):
			self.compile(node.right)
			opmap = {'-': 'UNARY_NEGATIVE', '+': 'UNARY_POSITIVE', '!': 'UNARY_NOT', '~': 'UNARY_INVERT'}
			self.emit(opmap[node.op], None)
		elif isinstance(node, (Number, String)):
			idx = self.add_const(node.value)
			self.emit('LOAD_CONST', node.value)
		elif isinstance(node, Boolean):
			self.emit('LOAD_CONST', node.value)
		elif isinstance(node, Identifier):
			self.emit('LOAD_NAME', node.name)
		else:
			raise Exception(f'Unknown node type: {type(node)}')

	def assemble(self) -> dict:
		return {
			'code': self.code,
			'consts': self.consts,
			'names': self.names,
		}


def compile_source(source: str) -> Dict[str, List[Tuple[str, Any]] | List[Any] | List[str]]:
	lexer = Lexer(source)
	tokens = lexer.tokenize()
	parser = Parser(tokens)
	prog = parser.parse()
	emitter = Emitter()
	emitter.compile(prog)
	return emitter.assemble()


def write_bytecode_to_file(file_name: str, content: Dict[str, List[Tuple[str, Any]] | List[Any] | List[str]]):
	os.makedirs("__basicpp__", exist_ok=True)
	with open(f"__basicpp__/{file_name}", 'w', encoding='utf-8') as f:
		for i, (op, arg) in enumerate(content.get('code', [])):
			arg_str = str(arg) if arg is not None else ""
			f.write(f"{i*2:>4} {op:<20} {arg_str}\n")


def main():
	# tiny self-test
	src = """START
x = 1 + 2 * 3 ; 
PRINT x ;
PRINT x == x ;
END"""
	print("==== SOURCE ===")
	print(src)
	print("==== BYTECODE ===")
	bc = compile_source(src)
	pprint(bc)
	write_bytecode_to_file('test.bc', bc) # Test the bytecode file

if __name__ == '__main__':
	main()
