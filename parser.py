from enum import Enum
from typing import Iterator, List, Optional
from elements import Terminal as VT, Nonterminal as VN, Operator, Parens
from lexer import Token
from types.parser import *


class ParserException(Exception):
    def __init__(self, message: str, token: Token, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message
        self.token = token

    def __str__(self):
        return self.message + 'when processing Token: ' + str(self.token)


class Parser:
    tokens_iter: Iterator[Token]
    current_token: Token
    next_token: Token
    nodes: List
    symbol_table: dict[str, VT]

    def __init__(self, tokens: list[Token]):
        self.tokens_iter = iter(tokens)
        self.current_token = next(self.tokens_iter)
        self.next_token = next(self.tokens_iter)
        self.nodes = list()
        self.symbol_table = dict()

    def eat_token(self, token: Optional[Enum] = None):
        if token and token != self.current_token.terminal:
            raise ParserException(f'Unexpected token value, expected {token},'
                                  f'received {self.current_token.terminal}', self.current_token)
        self.current_token = self.next_token
        self.next_token = next(self.tokens_iter)

    def is_operator(self, value: Token) -> bool:
        return value.terminal in Operator

    def parse_binary_expression(self):
        left = self.parse_expression()
        operator = self.current_token.terminal
        if not self.is_operator(operator):
            raise ParserException(f'Unexpected token value, expected operator, received {self.current_token.terminal}',
                                  self.current_token)
        self.eat_token()
        right = self.parse_expression()
        node = BinaryExpressionNode(left, right, operator)
        return node

    def parse_expression(self):
        if self.current_token.terminal is VT.INTCONST:
            node = NumberLiteralNode(int(self.current_token.lexeme))
            self.eat_token()
            return node
        elif self.current_token.terminal is VT.IDENT:
            node = IdentifierNode(self.current_token.lexeme)
            self.eat_token()
            return node
        elif self.current_token.terminal in Parens:
            self.eat_token()
            node = self.parse_binary_expression()
            self.eat_token()
            return node
        else:
            raise ParserException(f'Unexpected token type {self.current_token.terminal}',
                                  self.current_token)

    def parse_output(self):
        self.eat_token(VT.WRITE)
        node = PrintStatementNode(self.parse_expression())
        return node

    def parse_input(self):
        self.eat_token(VT.READ)
        node = ReadStatementNode(IdentifierNode(self.current_token.lexeme))
        self.eat_token()
        return node

    def parse_variable_assignment(self):
        name = self.current_token.lexeme
        self.eat_token()
        self.eat_token(VT.ASSIGN)
        node = VariableAssignmentNode(IdentifierNode(name), self.parse_expression())
        return node
