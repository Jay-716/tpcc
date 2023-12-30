from typing import List
from elements import Operator


class ExpressionBaseNode:
    pass


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
    pass


class PrintStatementNode(StatementNode):
    def __init__(self, expression: ExpressionBaseNode):
        self.expression = expression

    expression: ExpressionBaseNode


class ReadStatementNode(StatementNode):
    def __init__(self, name: IdentifierNode):
        self.name = name

    name: IdentifierNode


class VariableAssignmentNode(ExpressionBaseNode):
    def __init__(self, variable_name: IdentifierNode, value: ExpressionBaseNode):
        self.variable_name = variable_name
        self.variable = value

    name: IdentifierNode
    value: ExpressionBaseNode
