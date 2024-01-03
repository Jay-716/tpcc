from tpcc_types.parser import VariableType


class Quaternion:
    pass


class VariableAssignmentQuaternion(Quaternion):
    variable_name: str
    variable_type: VariableType
    value: None

    def __init__(self, variable_name: str, variable_type: VariableType, value):
        self.variable_name = variable_name
        self.variable_type = variable_type
        self.value = value

    def __str__(self):
        return f'(:=, {self.value}, -, {self.variable_name})'


class CalculationQuaternion(Quaternion):
    lhs: str
    rhs: str
    operator: str
    dest: str

    def __init__(self, lhs: str, rhs: str, operator: str, dest: str):
        self.lhs = lhs
        self.rhs = rhs
        self.operator = operator
        self.dest = dest

    def __str__(self):
        return f'({self.operator}, {self.lhs}, {self.rhs}, {self.dest})'


class ConditionalJumpQuaternion(Quaternion):
    operator: str
    lhs: str
    rhs: str
    dest: int | str

    def __init__(self, operator: str, lhs: str, rhs: str, dest: int | str):
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs
        self.dest = dest

    def __str__(self):
        return f'(j{self.operator}, {self.lhs}, {self.rhs}, {self.dest})'


class UnconditionalJumpQuaternion(Quaternion):
    dest: int | str

    def __init__(self, dest: int | str):
        self.dest = dest

    def __str__(self):
        return f'(j , -, -, {self.dest})'
