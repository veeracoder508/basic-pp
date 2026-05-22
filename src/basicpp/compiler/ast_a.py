import os
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
			if self.current().type == TokenType.KEYWORD and self.current().value.upper() == 'PRINT':
				stmts.append(self.parse_print())
				continue
			if self.current().type == TokenType.IDENTIFIER:
				# assignment if followed by operator '='
				look = self.tokens[self.pos + 1] if (self.pos + 1) < len(self.tokens) else None
				if look and look.type == TokenType.OPERATOR and look.value == '=':
					stmts.append(self.parse_assign())
					continue
			# skip unknown/standalone tokens by advancing to avoid infinite loop
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

	# Expression parsing (simple precedence)
	def parse_expr(self):
		return self.parse_term()

	def parse_term(self):
		node = self.parse_factor()
		while self.current().type == TokenType.OPERATOR and self.current().value in ('+', '-'):
			op = self.current().value
			self.advance()
			right = self.parse_factor()
			node = BinOp(node, op, right)
		return node

	def parse_factor(self):
		node = self.parse_unary()
		while self.current().type == TokenType.OPERATOR and self.current().value in ('*', '/', '%'):
			op = self.current().value
			self.advance()
			right = self.parse_unary()
			node = BinOp(node, op, right)
		return node

	def parse_unary(self):
		if self.current().type == TokenType.OPERATOR and self.current().value in ('+', '-'):
			op = self.current().value
			self.advance()
			node = self.parse_unary()
			return BinOp(Number(0), op, node)
		return self.parse_primary()

	def parse_primary(self):
		tok = self.current()
		if tok.type == TokenType.VALUE:
			# try numeric
			val = tok.value
			self.advance()
			# determine numeric or string
			# strings from lexer are unquoted; numbers are numeric literals
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
		elif isinstance(node, Print):
			for v in node.values:
				self.compile(v)
				self.emit('PRINT_ITEM', None)
			self.emit('PRINT_NEWLINE', None)
		elif isinstance(node, BinOp):
			self.compile(node.left)
			self.compile(node.right)
			opmap = {'+': 'BINARY_ADD', '-': 'BINARY_SUBTRACT', '*': 'BINARY_MULTIPLY', '/': 'BINARY_TRUE_DIVIDE', '%': 'BINARY_MODULO'}
			opname = opmap.get(node.op)
			if not opname:
				raise Exception(f'Unsupported binary op {node.op}')
			self.emit(opname, None)
		elif isinstance(node, Number):
			idx = self.add_const(node.value)
			self.emit('LOAD_CONST', node.value)
		elif isinstance(node, String):
			idx = self.add_const(node.value)
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

if __name__ == '__main__':
	# tiny self-test
	src = 'x = 1 + 2 * 3 ; PRINT x ;'
	bc = compile_source(src)
	print(bc)
	write_bytecode_to_file('test.bc', bc) # Test the bytecode file
