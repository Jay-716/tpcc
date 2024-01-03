from elements import Terminal
import re

# matches whitespace
WHITESPACE = re.compile(r"\s")

# matches newlines
NEWLINE = re.compile(r"\n")

# matches the start of an identifier
IDENT_START = re.compile(r"[a-zA-Z_]")

# matches the reset of an identifier
IDENT_BODY = re.compile(r"\w")

# matches digits
DIGIT = re.compile(r"\d")

# matches character literals
CHARCONST = re.compile(r"'.'")

# matches identifiers
IDENT = re.compile("[a-zA-Z_]\w*")

# matches integer literals
INTCONST = re.compile(r"\-?\d+")

# matches character literals
CHARCONST = re.compile("\'.\'")

# matches invalid character literals
CHARCONST_INVALID = re.compile("^\'")

KEYWORDS = {
    ":=": Terminal.ASSIGN,
    "*": Terminal.MULT,
    "+": Terminal.PLUS,
    "-": Terminal.MINUS,
    # "div": Terminal.DIV,
    "/": Terminal.DIV,  # Unlike pascal, we use '/' as division operator.
    "and": Terminal.AND,
    "or": Terminal.OR,
    "not": Terminal.NOT,
    "<": Terminal.LT,
    ">": Terminal.GT,
    "<=": Terminal.LE,
    ">=": Terminal.GE,
    "=": Terminal.EQ,
    "<>": Terminal.NE,
    "var": Terminal.VAR,
    "array": Terminal.ARRAY,
    "of": Terminal.OF,
    "boolean": Terminal.BOOL,
    "char": Terminal.CHAR,
    "integer": Terminal.INT,
    "program": Terminal.PROG,
    "procedure": Terminal.PROC,
    "begin": Terminal.BEGIN,
    "end": Terminal.END,
    "while": Terminal.WHILE,
    "repeat": Terminal.REPEAT,
    "until": Terminal.UNTIL,
    "do": Terminal.DO,
    "if": Terminal.IF,
    "then": Terminal.THEN,
    "else": Terminal.ELSE,
    "read": Terminal.READ,
    "write": Terminal.WRITE,
    "true": Terminal.TRUE,
    "false": Terminal.FALSE,
    "[": Terminal.LBRACK,
    "]": Terminal.RBRACK,
    ";": Terminal.SCOLON,
    ":": Terminal.COLON,
    "(": Terminal.LPAREN,
    ")": Terminal.RPAREN,
    ",": Terminal.COMMA,
    ".": Terminal.DOT,
    "..": Terminal.DOTDOT
}


class Token:

    def __init__(self, lexeme, terminal, line_number):
        self.lexeme = lexeme
        self.terminal = terminal
        self.line_number = line_number

    def __str__(self):
        return f"TOKEN: {self.terminal.value} LEXEME: {self.lexeme} LINE: {self.line_number}"


class MiplInvalidConst(Exception):
    pass


class Lexer:
    """
    Breaks an input file up into tokens and holds them for a parser.
    """

    def __init__(self, filename):

        self.debug_output = False

        self._tokenize(filename)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        self.last_lexeme += 1

        if self.last_lexeme < len(self.lexemes):
            tok = self.process_lexeme(self.lexemes[self.last_lexeme])
            # print(tok)
            return tok

        else:
            raise StopIteration

    def get_tokens(self):

        for lexeme in self.lexemes:
            token = self.process_lexeme(lexeme)
            # print(token)
            yield token

    def _tokenize(self, filename):
        """
        Reads in the passed file and breaks apart text into lexemes.
        """
        self.filename = filename

        fin = open(filename)
        operand = fin.read()
        fin.close()

        self.lexemes = []
        self.last_lexeme = -1

        # use lexstart and lexend to mark next lexeme
        lexstart = 0
        lexend = 0

        # track current line
        current_line = 1

        while lexstart < len(operand):

            # ignore all whitespace
            while re.match(WHITESPACE, operand[lexstart]):

                # track current lines
                if re.match(NEWLINE, operand[lexstart]):
                    current_line += 1

                lexstart += 1

                # make sure we don't go over the edge
                if lexstart >= len(operand):
                    break

            # make sure we don't go over the edge
            if lexstart >= len(operand):
                break

            lexend = lexstart + 1

            # ignore all comments
            if operand[lexend - 1:lexend + 1] == "(*":
                while lexend < len(operand) and operand[lexend - 1:lexend + 1] != "*)":

                    # but do keep track of current line
                    if re.match(NEWLINE, operand[lexend]):
                        current_line += 1

                    lexend += 1

                lexstart = lexend + 1
                continue

            # mark identifiers
            elif re.match(IDENT_START, operand[lexstart]):
                while re.match(IDENT_BODY, operand[lexend]):
                    lexend += 1

            # mark digits
            elif re.match(DIGIT, operand[lexstart]):
                while re.match(DIGIT, operand[lexend]):
                    lexend += 1

            # mark character literals
            elif operand[lexstart] == "\'":

                # try to take three characters
                # two single quotes and literal character
                lexend = lexstart + 3

                # if these three characters don't match a character constant
                # (and don't go off the cliff)
                if not (lexend < len(operand) and re.match(CHARCONST, operand[lexstart:lexend])):

                    if operand[lexend - 2] == "\'":
                        lexend = lexstart + 2
                    else:
                        lexend = lexstart + 1

            # clump minus signs with digits
            elif operand[lexstart] == "-":
                while operand[lexend] in "0123456789":
                    lexend += 1

            # clump two dots together
            elif operand[lexstart] == ".":
                if operand[lexend] == ".":
                    lexend += 1

            # clump an equals to a colon (assignment operator)
            elif operand[lexstart] == ":":
                if operand[lexend] == "=":
                    lexend += 1

            # clump relop characters together
            elif operand[lexstart] == "<":
                if operand[lexend] in "=>":
                    lexend += 1

            elif operand[lexstart] == ">":
                if operand[lexend] == "=":
                    lexend += 1

            self.lexemes.append((operand[lexstart:lexend], current_line))
            lexstart = lexend

    def process_lexeme(self, token):
        """
        Processes a lexeme and turns it into a token.
        """
        lexeme, line_number = token

        # recognize keywords and operators
        if lexeme in KEYWORDS.keys():
            return Token(lexeme, KEYWORDS[lexeme], line_number)

        # recognize identifiers
        elif re.match(IDENT, lexeme):
            return Token(lexeme, Terminal.IDENT, line_number)

        # recognize integer literals
        elif re.match(INTCONST, lexeme):
            if not (abs(int(lexeme, 10)) >> 31):
                return Token(lexeme, Terminal.INTCONST, line_number)
            else:
                raise MiplInvalidConst(f"**** invalid integer constant: {lexeme}")

        # recognize character literals
        elif re.match(CHARCONST, lexeme):
            return Token(lexeme, Terminal.CHARCONST, line_number)

        # raise for invalid characters
        elif re.match(CHARCONST_INVALID, lexeme):
            raise MiplInvalidConst(f"**** invalid character constant: {lexeme}")

        # otherwise, return unknown
        else:
            return Token(lexeme, Terminal.UNKNOWN, line_number)
