from _ast import Expression
from typing import Iterator, List, Optional
from elements import Terminal as VT, Nonterminal as VN, Operator, Parens
from lexer import Token, Terminal
from tpcc_types.parser import *


class ParserException(Exception):
    def __init__(self, message: str, token: Token, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.message = message
        self.token = token

    def __str__(self):
        return self.message + '\nCurrent token: ' + str(self.token)


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

    def is_operator(self, value: Terminal) -> bool:
        return value in Operator

    # TODO: operator priority
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

    def parse_primary(self):
        token = self.current_token
        if token.terminal is VT.IDENT:
            return IdentifierNode(token.lexeme)
        elif token.terminal is VT.INTCONST:
            return NumberLiteralNode(int(token.lexeme))
        else:
            raise ParserException(f'Unexpected token type in expression', self.current_token)

    def _parse_expression(self, lhs: ExpressionBaseNode, min_precedence: int):
        def precedence_of(op: Operator):
            precedences = {Terminal.PLUS: 3, Terminal.MINUS: 3, Terminal.MULT: 4, Terminal.DIV: 4,
                           Terminal.EQ: 5, Terminal.NE: 5, Terminal.LT: 5, Terminal.GT: 5, Terminal.LE: 5, Terminal.GE: 5,
                           Terminal.OR: 1, Terminal.AND: 2}
            return precedences[op]

        peek = self.next_token
        while peek.terminal in Operator and precedence_of(peek.terminal) >= 1:
            operator = peek.terminal
            self.eat_token()
            self.eat_token()
            rhs = self.parse_primary()
            peek = self.next_token
            while peek.terminal in Operator and precedence_of(peek.terminal) >= precedence_of(operator):
                rhs = self._parse_expression(rhs,
                                             precedence_of(operator) +
                                             1 if precedence_of(self.next_token.terminal)
                                                  >= precedence_of(operator)
                                             else 0)
                peek = self.next_token
            lhs = BinaryExpressionNode(lhs, rhs, operator)
        #if self.next_token.terminal is VT.SCOLON:
        #    self.eat_token()
        return lhs

    def parse_expression(self):
        return self._parse_expression(self.parse_primary(), 0)

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
        self.eat_token()  # parse_expression() may not eat the last token of an expression
        self.eat_token(VT.SCOLON)
        return node

    def parse_variable_declaration(self):
        self.eat_token(VT.VAR)
        # TODO: validate variable name
        names: List[IdentifierNode] = list()
        names.append(IdentifierNode(self.current_token.lexeme))
        self.eat_token(VT.IDENT)
        while self.current_token.terminal == VT.COMMA:
            self.eat_token(VT.COMMA)
            names.append(IdentifierNode(self.next_token.lexeme))
            self.eat_token(VT.IDENT)
        self.eat_token(VT.COLON)
        variable_type_str = self.current_token.lexeme
        if variable_type_str == 'integer':
            variable_type = VariableType.Integer
            self.eat_token(VT.INT)
        else:
            raise ParserException(f'Unrecognized variable_type: {variable_type_str}', self.current_token)
        node = VariableDeclarationNode(names, variable_type)
        self.eat_token(VT.SCOLON)
        return node

    def parse_statement(self):
        if self.current_token.terminal == VT.WRITE:
            result = self.parse_output()
        elif self.current_token.terminal == VT.READ:
            result = self.parse_input()
        elif self.current_token.terminal == VT.VAR:
            result = self.parse_variable_declaration()
        elif self.current_token.terminal == VT.IF:
            result = self.parse_if_statement()
        elif self.current_token.terminal == VT.WHILE:
            result = self.parse_while_statement()
        elif self.current_token.terminal == VT.REPEAT:
            result = self.parse_repeat_statement()
        elif self.current_token.terminal == VT.IDENT:
            result = self.parse_variable_assignment()
        else:
            raise ParserException(f'Unexpected token: {self.current_token}', self.current_token)
        return result

    def parse_if_statement(self):
        self.eat_token(VT.IF)
        condition = self.parse_expression()
        self.eat_token()  # parse_expression() may not eat the last token of an expression
        self.eat_token(VT.THEN)
        true_statements = list()
        if self.current_token.terminal == VT.BEGIN:
            self.eat_token(VT.BEGIN)
            while self.current_token.terminal != VT.END:
                true_statements.append(self.parse_statement())
            self.eat_token(VT.END)
            self.eat_token(VT.DOT)
        else:
            true_statements.append(self.parse_statement())
        false_statements = list()
        if self.current_token.terminal == VT.ELSE:
            self.eat_token(VT.ELSE)
            if self.current_token.terminal == VT.BEGIN:
                self.eat_token(VT.BEGIN)
                while self.current_token.terminal != VT.END:
                    false_statements.append(self.parse_statement())
                self.eat_token(VT.END)
                self.eat_token(VT.DOT)
            else:
                false_statements.append(self.parse_statement())
        node = IfStatementNode(condition, true_statements, false_statements)
        return node

    def parse_while_statement(self):
        self.eat_token(VT.WHILE)
        condition = self.parse_expression()  # TODO: use parse_expression()
        self.eat_token()  # parse_expression() may not eat the last token of an expression
        self.eat_token(VT.DO)
        statements = list()
        if self.current_token.terminal == VT.BEGIN:
            self.eat_token(VT.BEGIN)
            while self.current_token.terminal != VT.END:
                statements.append(self.parse_statement())
            self.eat_token(VT.END)
            self.eat_token(VT.DOT)
        else:
            statements.append(self.parse_statement())
        node = WhileStatementNode(condition, statements)
        return node

    def parse_repeat_statement(self):
        self.eat_token(VT.REPEAT)
        statements = list()
        if self.current_token.terminal == VT.BEGIN:
            self.eat_token(VT.BEGIN)
            while self.current_token.terminal != VT.END:
                statements.append(self.parse_statement())
            self.eat_token(VT.END)
            self.eat_token(VT.DOT)
        else:
            statements.append(self.parse_statement())
        self.eat_token(VT.UNTIL)
        condition = self.parse_expression()
        self.eat_token()  # parse_expression() may not eat the last token of an expression
        self.eat_token(VT.SCOLON)
        node = RepeatStatementNode(condition, statements)
        return node

    def parse_program(self):
        self.eat_token(VT.PROG)
        program = self.current_token.lexeme
        node = ProgramNode(program)
        self.eat_token(VT.IDENT)
        self.eat_token(VT.SCOLON)
        return node

    def _parse(self):
        self.nodes.append(self.parse_program())
        self.parse_variable_declaration()
        self.eat_token(VT.PROC)
        self.eat_token(VT.IDENT)
        self.eat_token(VT.SCOLON)
        self.eat_token(VT.BEGIN)
        while self.next_token and self.current_token.terminal != VT.END:
            self.nodes.append(self.parse_statement())
        # End of the whole program. Stop here, otherwise eat_token() will raise StopIteration.
        # self.eat_token(VT.END)
        # self.eat_token(VT.SCOLON)

    def parse(self):
        self._parse()
        return self.nodes
