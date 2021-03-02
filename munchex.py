####################
# Imports
####################
from string_with_arrows import *

####################
# Constants
####################

DIGITS = "0123456789"

####################
# Errors
####################

# This is the base error.
# We take in details and a name and then we set the variables to those
# We also have a class to return a formatted error


class Error:
    def __init__(self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details

    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f"\nFile {self.pos_start.filename}, line {self.pos_start.line + 1}"
        result += '\n\n' + \
            string_with_arrows(self.pos_start.fileText,
                               self.pos_start, self.pos_end)
        return result

# This is a more specific error that is a sub class of Error so has access to the init section
# It then takes in details and creates an error with the specific name and details


class IllegalCharError(Error):
    def __init__(self, pos_start, pos_end, details):
        super().__init__(pos_start, pos_end, "Illegal Character", details)


class InvalidSyntaxError(Error):
    def __init__(self, pos_start, pos_end, details):
    super().__init__(pos_start, pos_end, "Invalid Syntax", details)

####################
# Position
####################


class Position:
    def __init__(self, index, line, column, filename, fileText):
        self.index = index
        self.line = line
        self.column = column
        self.filename = filename
        self.fileText = fileText

    # This moves on to the next index and updates the line and column number if necessary
    def advance(self, current_char):
        self.index += 1
        self.column += 1

        # If the current character is a new line, then we increment the line variable and reset the column
        if(current_char == "\n"):
            self.line += 1
            self.column = 0

        return self

    # This will just create a copy of the position
    def copy(self):
        return Position(self.index, self.line, self.column, self.filename, self.fileText)

####################
# Tokens
####################


TT_INT = "INT"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"


class Token:
    def __init__(self, type_, value_=None):
        self.type = type_
        self.value = value_

    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

####################
# Lexer
####################


class Lexer:
    def __init__(self, filename, text):
        self.filename = filename
        self.text = text
        self.pos = Position(-1, 0, -1, filename, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.index] if self.pos.index < len(
            self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            # First check if it is a space or a tab
            # If it is, skip it
            if self.current_char in ' \t':
                self.advance()
            # We check if the character is a digit
            elif self.current_char in DIGITS:
                # We then add the result of our make number class which can figure out whether or not it had multiple digits and wheather it is a float or an int
                tokens.append(self.make_number())
            # Then check for the +, -, *, /, (, or ) symbols and add a token with those
            elif self.current_char == "+":
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == "-":
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == "*":
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == "/":
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == "(":
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ")":
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                # This makes it so we return nothing for this text and return the specific error. If it is successful, we return "tokens" and None as our error
                return [], IllegalCharError(pos_start, self.pos, "'" + char + "'")

        return tokens, None

    def make_number(self):
        num_str = ""
        dot_count = 0

        # We want to make sure we are not finished with the text and then we want to make sure it is still a number and/or a .
        while self.current_char != None and self.current_char in DIGITS + ".":
            if self.current_char == ".":
                # We can't have more than a single dot in a number.
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))

####################
# Nodes
####################


class NumberNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        return f'{self.token}'

# Binary Operation Node (For +, -, *, and /)


class BinOpNode:
    def __init__(self, left_node, operator_token, right_node):
        self.left_node = left_node
        self.operator_token = operator_token
        self.right_node = right_node

    def __repr__(self):
        return f'({self.left_node}, {self.operator_token}, {self.right_node})'

####################
# Parser
####################


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = -1
        self.advance()

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        return self.current_token

    def parse(self):
        result = self.expression()
        return result

    def factor(self):
        token = self.current_token

        # We check if it is a int or a float and then we advance to the next token and return a number node with that int/float
        if token.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(token)

    def term(self):
        return self.binary_operation(self.factor, (TT_MUL, TT_DIV))

    def expression(self):
        return self.binary_operation(self.term, (TT_PLUS, TT_MINUS))

    # The function corresponds to the rule we are looking for either term or factor
    # The operations are the list of operations that can be accepted
    def binary_operation(self, function, operations):
        # Calls the above function to get the token I believe
        #left = self.factor()
        # In this generic one, we call whatever function we are looking for.
        left = function()

        # Here we loop forever as long as it is a multiplication or a division and we get the operator and then advance it.
        # We then get the right side of the term as we get the next factor.
        # Then we create a binary operation node and return it
        # while self.current_token in (TT_MUL, TT_DIV):
        while self.current_token.type in operations:
            operator_token = self.current_token
            self.advance()
            #right = self.factor()
            right = function()

            left = BinOpNode(left, operator_token, right)

        return left

####################
# Run
####################


def run(filename, text):
    # Generate Tokens
    lexer = Lexer(filename, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Generate Abstract Syntax Tree
    parser = Parser(tokens)
    ast = parser.parse()

    # return tokens, error
    return ast, None
