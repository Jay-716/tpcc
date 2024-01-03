from enum import Enum
from typing import List
from elements import Operator


class VariableType(Enum):
    Integer = 1


class ExpressionBaseNode:
    def __str__(self):
        return f'{type(self).__name__}: {self.__dict__}'



class NumberLiteralNode(ExpressionBaseNode):
    value: int

    def __init__(self, value: int):
        self.value = value


class BinaryExpressionNode(ExpressionBaseNode):
    left: ExpressionBaseNode
    right: ExpressionBaseNode
    operator: Operator

    def __init__(self, left: ExpressionBaseNode, right: ExpressionBaseNode, operator: Operator):
        self.left = left
        self.right = right
        self.operator = operator


class IdentifierNode(ExpressionBaseNode):
    value: str

    def __init__(self, value: str):
        self.value = value


class StatementNode:
    def __str__(self):
        return f'{type(self).__name__}: {self.__dict__}'


class PrintStatementNode(StatementNode):
    expression: ExpressionBaseNode

    def __init__(self, expression: ExpressionBaseNode):
        self.expression = expression


class ReadStatementNode(StatementNode):
    name: IdentifierNode

    def __init__(self, name: IdentifierNode):
        self.name = name


class VariableAssignmentNode(StatementNode):
    name: IdentifierNode
    value: ExpressionBaseNode

    def __init__(self, variable_name: IdentifierNode, value: ExpressionBaseNode):
        self.name = variable_name
        self.value = value


class VariableDeclarationNode(ExpressionBaseNode):
    names: List[IdentifierNode]
    variable_type: VariableType

    def __init__(self, variable_names: List[IdentifierNode], variable_type: VariableType):
        self.names = variable_names
        self.variable_type = variable_type


class IfStatementNode(StatementNode):
    condition: ExpressionBaseNode
    true_statements: List[StatementNode]
    false_statements: List[StatementNode]

    def __init__(self, condition: ExpressionBaseNode,
                 true_statements: List[StatementNode], false_statements: List[StatementNode] = []):
        self.condition = condition
        self.true_statements = true_statements
        self.false_statements = false_statements


class WhileStatementNode(StatementNode):
    def __init__(self, condition: ExpressionBaseNode, statements: List[StatementNode]):
        condition: ExpressionBaseNode
        statements: List[StatementNode]

        self.condition = condition
        self.statements = statements


class RepeatStatementNode(StatementNode):
    condition: ExpressionBaseNode
    statements: List[StatementNode]

    def __init__(self, condition: ExpressionBaseNode, statements: List[StatementNode]):
        self.condition = condition
        self.statements = statements


class ProgramNode(StatementNode):
    program_name: str

    def __init__(self, program_name: str):
        self.program_name = program_name

