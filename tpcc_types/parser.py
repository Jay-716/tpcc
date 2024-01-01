from enum import Enum
from typing import List
from elements import Operator


class VariableType(Enum):
    Integer = 1


class ExpressionBaseNode:
    def __str__(self):
        return str(type(self)) + ': ' + str(self.__dict__)



class NumberLiteralNode(ExpressionBaseNode):
    def __init__(self, value: int):
        self.value = value

    value: int


class BinaryExpressionNode(ExpressionBaseNode):
    def __init__(self, left: ExpressionBaseNode, right: ExpressionBaseNode, operator: Operator):
        self.left = left
        self.right = right
        self.operator = operator

    left: ExpressionBaseNode
    right: ExpressionBaseNode
    operator: Operator


class IdentifierNode(ExpressionBaseNode):
    def __init__(self, value: str):
        self.value = value

    value: str


class StatementNode:
    def __str__(self):
        return str(type(self)) + ': ' + str(self.__dict__)


class PrintStatementNode(StatementNode):
    def __init__(self, expression: ExpressionBaseNode):
        self.expression = expression

    expression: ExpressionBaseNode


class ReadStatementNode(StatementNode):
    def __init__(self, name: IdentifierNode):
        self.name = name

    name: IdentifierNode


class VariableAssignmentNode(StatementNode):
    def __init__(self, variable_name: IdentifierNode, value: ExpressionBaseNode):
        self.name = variable_name
        self.value = value

    name: IdentifierNode
    value: ExpressionBaseNode


class VariableDeclarationNode(ExpressionBaseNode):
    def __init__(self, variable_names: List[IdentifierNode], variable_type: VariableType):
        self.names = variable_names
        self.variable_type = variable_type

    names: List[IdentifierNode]
    variable_type: VariableType


class IfStatementNode(StatementNode):
    def __init__(self, condition: ExpressionBaseNode, statements: List[StatementNode]):
        self.condition = condition
        self.statements = statements

    condition: ExpressionBaseNode
    statements: List[StatementNode]


class WhileStatementNode(StatementNode):
    def __init__(self, condition: ExpressionBaseNode, statements: List[StatementNode]):
        self.condition = condition
        self.statements = statements

    condition: ExpressionBaseNode
    statements: List[StatementNode]


class RepeatStatementNode(StatementNode):
    def __init__(self, condition: ExpressionBaseNode, statements: List[StatementNode]):
        self.condition = condition
        self.statements = statements

    condition: ExpressionBaseNode
    statements: List[StatementNode]


class ProgramNode(StatementNode):
    def __init__(self, program_name: str):
        self.program_name = program_name

    program_name: str
