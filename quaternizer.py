from typing import Iterator, List, Optional
from elements import Terminal as VT
from tpcc_types.parser import *
from tpcc_types.quaternion import *


class QuaternizerException(Exception):
    def __init__(self, message: str, node: StatementNode, *args, **kwargs) -> None:
        super().__init__(message, *args, **kwargs)
        self.message = message
        self.node = node

    def __str__(self) -> str:
        return self.message + '\nCurrent node: ' + str(self.node)


class Quaternizer:
    nodes: Iterator[StatementNode]
    quaternions: List[Quaternion]
    current_pos: int  # The position of next quaternion to be generated, started from 1.
    current_node: StatementNode
    temporary_variables: int
    temporary_labels: int

    def __init__(self, nodes: List[StatementNode]):
        self.nodes = iter(nodes)
        self.quaternions = list()
        self.current_pos = 0
        self.temporary_variables = 0
        self.temporary_labels = 0

    def next_node(self) -> Optional[StatementNode]:
        try:
            self.current_node = next(self.nodes)
        except StopIteration:
            return None
        return self.current_node

    def emit(self, quaternion: Quaternion) -> int:
        self.quaternions.append(quaternion)
        self.current_pos = len(self.quaternions)
        return self.current_pos

    def get_temporary_variable(self) -> str:
        self.temporary_variables += 1
        return f't{self.temporary_variables}'

    def get_temporary_label(self) -> str:
        self.temporary_labels += 1
        return f'l{self.temporary_labels}'

    def generate(self):
        self._generate()
        return self.quaternions

    def _generate(self):
        node = self.next_node()
        while node is not None:
            last_chain = self.parse_node(node)
            node = self.next_node()
            if last_chain is not None:
                self.backpatch(last_chain, self.current_pos + 1)

    def parse_node(self, node: StatementNode):
        if type(node) is ProgramNode:
            # Do nothing since we only support single file with single program currently.
            pass
        elif type(node) is VariableAssignmentNode:
            self.parse_variable_assignment(node)
        elif type(node) is IfStatementNode:
            return self.parse_if_statement(node)
        elif type(node) is WhileStatementNode:
            return self.parse_while_statement(node)
        elif type(node) is RepeatStatementNode:
            self.parse_repeat_statement(node)
        else:
            raise QuaternizerException(f'Unexpected node type: {type(node)}', self.current_node)

    def parse_variable_assignment(self, node: VariableAssignmentNode):
        self._parse_variable_assignment(node)

    def _parse_variable_assignment(self, node: VariableAssignmentNode):
        # TODO: we need to get variable type here
        if type(node.value) is NumberLiteralNode:
            self.emit(VariableAssignmentQuaternion(node.name.value, VariableType.Integer, str(node.value.value)))
        elif type(node.value) is IdentifierNode:
            self.emit(VariableAssignmentQuaternion(node.name.value, VariableType.Integer, node.value.value))
        elif type(node.value) is BinaryExpressionNode:
            result = self.calculate_expression(node.value)
            self.emit(VariableAssignmentQuaternion(node.name.value, VariableType.Integer, result))
        else:
            raise QuaternizerException(f'Unexpected variable value node type: {type(node)}', self.current_node)

    def calculate_expression(self, node: BinaryExpressionNode) -> str:
        if type(node.left) is NumberLiteralNode:
            lhs = str(node.left.value)
        elif type(node.left) is IdentifierNode:
            lhs = node.left.value
        elif type(node.left) is BinaryExpressionNode:
            lhs = self.calculate_expression(node.left)
        else:
            raise QuaternizerException(f'Unexpected expression operand: {type(node.left)}', self.current_node)
        if type(node.right) is NumberLiteralNode:
            rhs = str(node.right.value)
        elif type(node.right) is IdentifierNode:
            rhs = node.right.value
        elif type(node.right) is BinaryExpressionNode:
            rhs = self.calculate_expression(node.right)
        else:
            raise QuaternizerException(f'Unexpected expression operand: {type(node.right)}', self.current_node)
        tmp = self.get_temporary_variable()
        if node.operator is VT.PLUS:
            op = '+'
        elif node.operator is VT.MINUS:
            op = '-'
        elif node.operator is VT.MULT:
            op = '*'
        elif node.operator is VT.DIV:
            op = '/'
        else:
            raise QuaternizerException(f'Unexpected expression operator: {node.operator.value}', self.current_node)
        self.emit(CalculationQuaternion(lhs, rhs, op, tmp))
        return tmp

    def parse_if_statement(self, node: IfStatementNode):
        return self._parse_if_statement(node)

    def _parse_if_statement(self, node: IfStatementNode):
        condition_begin, true_exit, false_exit = self.trans_condition(node.condition)
        true_begin = self.current_pos + 1
        self.backpatch(true_exit, true_begin)
        # false exit should jump to the beginning of true statements
        c_chain = false_exit
        true_chain = 1
        for statement in node.true_statements:
            chain = self.parse_node(statement)
            true_chain = chain if chain is not None else 1
        # merge false exit and true statements exit, since they should jump to the same destination.
        s_chain = self.merge(c_chain, true_chain)
        jump_out = self.emit(UnconditionalJumpQuaternion(0))  # jump across false statements
        # false exit jumps to false statements
        self.backpatch(c_chain, jump_out + 1)
        # true statements exit and jump out exit should jump to the same destination
        tp_chain = self.merge(jump_out, true_chain)
        false_chain = 1
        for statement in node.false_statements:
            chain = self.parse_node(statement)
            false_chain = chain if chain is not None else 1
        # true statements, jump out and false statements should jump to the same destination
        s_chain = self.merge(tp_chain, false_chain)
        return s_chain

    def parse_while_statement(self, node: WhileStatementNode):
        condition_begin, true_exit, false_exit = self.trans_condition(node.condition)
        while_begin = self.current_pos + 1
        # true exit jumps to the beginning of while statements
        self.backpatch(true_exit, while_begin)
        while_chain = 1
        for statement in node.statements:
            chain = self.parse_node(statement)
            while_chain = chain if chain is not None else 1
        # jump to the beginning of the whole statement
        self.backpatch(while_chain, condition_begin)
        self.emit(UnconditionalJumpQuaternion(condition_begin))
        chain = false_exit
        return chain

    def parse_repeat_statement(self, node: RepeatStatementNode):
        repeat_begin = self.current_pos + 1
        for statement in node.statements:
            self.parse_node(statement)
        condition_begin, true_exit, false_exit = self.trans_condition(node.condition)
        # trans_condition() will generate an unconditional jump for false exit,
        # which is simply the next quaternion of repeat condition jump, so the false exit jump here is extra,
        # we need to increase repeat_end to avoid false exit jump onto itself.
        repeat_end = self.current_pos + 1
        self.backpatch(true_exit, repeat_end)
        self.backpatch(false_exit, repeat_begin)

    def trans_condition(self, condition: BinaryExpressionNode):
        if condition.operator == VT.OR:
            l_begin, l_true_exit, l_false_exit = self.trans_condition(condition.left)
            r_begin, r_true_exit, r_false_exit = self.trans_condition(condition.right)
            code_begin = l_begin
            self.backpatch(l_false_exit, r_begin)
            true_exit = self.merge(l_true_exit, r_true_exit)
            false_exit = r_false_exit
            return code_begin, true_exit, false_exit
        elif condition.operator == VT.AND:
            l_begin, l_true_exit, l_false_exit = self.trans_condition(condition.left)
            r_begin, r_true_exit, r_false_exit = self.trans_condition(condition.right)
            code_begin = l_begin
            self.backpatch(l_true_exit, r_begin)
            true_exit = r_true_exit
            false_exit = self.merge(l_false_exit, r_false_exit)
            return code_begin, true_exit, false_exit
        elif condition.operator == VT.EQ:
            op = '='
        elif condition.operator == VT.NE:
            op = '!='
        elif condition.operator == VT.GT:
            op = '>'
        elif condition.operator == VT.LT:
            op = '<'
        elif condition.operator == VT.GE:
            op = '>='
        elif condition.operator == VT.LE:
            op = '<='
        else:
            raise QuaternizerException(f'Unexpected condition operator: {condition.operator}')
        if type(condition.left) is NumberLiteralNode:
            lhs = str(condition.left.value)
        elif type(condition.left) is IdentifierNode:
            lhs = condition.left.value
        elif type(condition.left) is BinaryExpressionNode:
            # TODO: We may need to backpatch and merge here too, but it seems that the control flow will not reach here.
            return self.trans_condition(condition.left)
        else:
            raise QuaternizerException(f'Unexpected condition operand: {condition.left}', self.current_node)
        if type(condition.right) is NumberLiteralNode:
            rhs = str(condition.right.value)
        elif type(condition.right) is IdentifierNode:
            rhs = condition.right.value
        elif type(condition.right) is BinaryExpressionNode:
            # TODO: We may need to backpatch and merge here too, but it seems that the control flow will not reach here.
            return self.trans_condition(condition.right)
        else:
            raise QuaternizerException(f'Unexpected condition operand: {condition.right}', self.current_node)
        #true_exit = self.get_temporary_label()
        #false_exit = self.get_temporary_label()
        true_exit = 0
        false_exit = 0
        start_pos = self.emit(ConditionalJumpQuaternion(op, lhs, rhs, true_exit))
        false_pos = self.emit(UnconditionalJumpQuaternion(false_exit))
        return start_pos, start_pos, false_pos

    def fill_label(self, label: str, pos: int):
        for quaternion in self.quaternions:
            if type(quaternion) is ConditionalJumpQuaternion:
                if quaternion.dest == label:
                    quaternion.dest = pos
            elif type(quaternion) is UnconditionalJumpQuaternion:
                if quaternion.dest == label:
                    quaternion.dest = pos

    def backpatch(self, head: int, dest: int):
        head -= 1  # to index
        while head != 0 and head < len(self.quaternions):
            old_head = self.quaternions[head].dest
            self.quaternions[head].dest = dest
            head = old_head

    def merge(self, lhs: int, rhs: int):
        lhs -= 1  # to index
        rhs -= 1  # to index
        if rhs == 0:
            return lhs + 1
        else:
            head = rhs
            while head != 0 and head < len(self.quaternions):
                old_head = head
                head = self.quaternions[head].dest
            # head == 0
            self.quaternions[old_head].dest = lhs
            return rhs + 1



