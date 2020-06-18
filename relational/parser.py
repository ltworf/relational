# Relational
# Copyright (C) 2008-2020 Salvo "LtWorf" Tomaselli
#
# Relational is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>
#
#
#
# This module implements a parser for relational algebra, and can be used
# to convert expressions into python expressions and to get the parse-tree
# of the expression.
#
# Language definition here:
# http://ltworf.github.io/relational/grammar.html
from typing import Optional, Union, List, Any, Dict
from dataclasses import dataclass

from relational import rtypes

PRODUCT = '*'
DIFFERENCE = '-'
UNION = '∪'
INTERSECTION = '∩'
DIVISION = '÷'
JOIN = '⋈'
JOIN_LEFT = '⧑'
JOIN_RIGHT = '⧒'
JOIN_FULL = '⧓'
PROJECTION = 'π'
SELECTION = 'σ'
RENAME = 'ρ'
ARROW = '➡'

b_operators = (PRODUCT, DIFFERENCE, UNION, INTERSECTION, DIVISION,
               JOIN, JOIN_LEFT, JOIN_RIGHT, JOIN_FULL)  # List of binary operators
u_operators = (PROJECTION, SELECTION, RENAME)  # List of unary operators

# Associates operator with python method
op_functions = {
    PRODUCT: 'product', DIFFERENCE: 'difference', UNION: 'union', INTERSECTION: 'intersection', DIVISION: 'division', JOIN: 'join',
    JOIN_LEFT: 'outer_left', JOIN_RIGHT: 'outer_right', JOIN_FULL: 'outer', PROJECTION: 'projection', SELECTION: 'selection', RENAME: 'rename'}


class TokenizerException (Exception):
    pass


class ParserException (Exception):
    pass


class CallableString(str):

    '''
    This is a string. However it is also callable.

    For example:
    CallableString('1+1')()
    returns 2

    It is used to contain Python expressions and print
    or execute them.
    '''

    def __call__(self, context=None):
        '''
        context is a dictionary where to
        each name is associated the relative relation
        '''
        return eval(self, context)

@dataclass
class Node:
    '''This class is a node of a relational expression. Leaves are relations
    and internal nodes are operations.

    The 'kind' property indicates whether the node is a binary operator, unary
    operator or relation.
    Since relations are leaves, a relation node will have no attribute for
    children.

    If the node is a binary operator, it will have left and right properties.

    If the node is a unary operator, it will have a child, pointing to the
    child node and a property containing the string with the props of the
    operation.

    This class is used to convert an expression into python code.'''
    name: str

    def __init__(self, name: str) -> None:
        raise NotImplementedError('This is supposed to be an abstract class')

    def toCode(self): #FIXME return type
        '''This method converts the AST into a python code object'''
        code = self._toPython()
        return compile(code, '<relational_expression>', 'eval')

    def toPython(self) -> CallableString:
        '''This method converts the AST into a python code string, which
        will require the relation module to be executed.

        The return value is a CallableString, which means that it can be
        directly called.'''
        return CallableString(self._toPython())

    def _toPython(self) -> str:
        raise NotImplementedError()

    def printtree(self, level: int = 0) -> str:
        '''returns a representation of the tree using indentation'''
        r = ''
        for i in range(level):
            r += '  '
        r += self.name
        if self.name in b_operators:
            r += self.left.printtree(level + 1)
            r += self.right.printtree(level + 1)
        elif self.name in u_operators:
            r += '\t%s\n' % self.prop
            r += self.child.printtree(level + 1)
        return '\n' + r

    def get_left_leaf(self) -> 'Node':
        raise NotImplementedError()

    def result_format(self, rels: dict) -> list: #FIXME types
        '''This function returns a list containing the fields that the resulting relation will have.
        It requires a dictionary where keys are the names of the relations and the values are
        the relation objects.'''
        if not isinstance(rels, dict):
            raise TypeError('Can\'t be of None type')

        if isinstance(self, Variable):  #FIXME this is ugly
            return list(rels[self.name].header)
        elif isinstance(self, Binary) and self.name in (DIFFERENCE, UNION, INTERSECTION):
            return self.left.result_format(rels)
        elif isinstance(self, Binary) and self.name == DIVISION:
            return list(set(self.left.result_format(rels)) - set(self.right.result_format(rels)))
        elif self.name == PROJECTION:
            return self.get_projection_prop()
        elif self.name == PRODUCT:
            return self.left.result_format(rels) + self.right.result_format(rels)
        elif self.name == SELECTION:
            return self.child.result_format(rels)
        elif self.name == RENAME:
            _vars = {}
            for i in self.prop.split(','):
                q = i.split(ARROW)
                _vars[q[0].strip()] = q[1].strip()

            _fields = self.child.result_format(rels)
            for i in range(len(_fields)):
                if _fields[i] in _vars:
                    _fields[i] = _vars[_fields[i]]
            return _fields
        elif self.name in (JOIN, JOIN_LEFT, JOIN_RIGHT, JOIN_FULL):
            return list(set(self.left.result_format(rels)).union(set(self.right.result_format(rels))))
        raise ValueError('What kind of alien object is this?')

    def __eq__(self, other): #FIXME
        if not (isinstance(other, node) and self.name == other.name and self.kind == other.kind):
            return False

        if self.kind == UNARY:
            if other.prop != self.prop:
                return False
            return self.child == other.child
        if self.kind == BINARY:
            return self.left == other.left and self.right == other.right
        return True


@dataclass
class Variable(Node):
    def _toPython(self) -> str:
        return self.name

    def __str__(self):
        return self.name

    def get_left_leaf(self) -> Node:
        return self


@dataclass
class Binary(Node):
    left: Node
    right: Node

    def get_left_leaf(self) -> Node:
        return self.left.get_left_leaf()

    def _toPython(self) -> str:
        return '%s.%s(%s)' % (self.left._toPython(), op_functions[self.name], self.right._toPython())

    def __str__(self):
        le = self.left.__str__()
        if isinstance(self.right, Binary):
            re = "(" + self.right.__str__() + ")"
        else:
            re = self.right.__str__()
        return (le + self.name + re) #TODO use fstrings


@dataclass
class Unary(Node):
    prop: str
    child: Node

    def get_left_leaf(self) -> Node:
        return self.child.get_left_leaf()

    def __str__(self):
        return self.name + " " + self.prop + " (" + self.child.__str__() + ")" #TODO use fstrings

    def _toPython(self) -> str:
        prop = self.prop

        # Converting parameters
        if self.name == PROJECTION:
            prop = repr(self.get_projection_prop())
        elif self.name == RENAME:
            prop = repr(self.get_rename_prop())
        else:  # Selection
            prop = repr(prop)

        return '%s.%s(%s)' % (self.child._toPython(), op_functions[self.name], prop)

    def get_projection_prop(self) -> List[str]:
        if self.name != PROJECTION:
            raise ValueError('This is only supported on projection nodes')
        return [i.strip() for i in self.prop.split(',')]

    def set_projection_prop(self, p: List[str]) -> None:
        if self.name != PROJECTION:
            raise ValueError('This is only supported on projection nodes')
        self.prop = ','.join(p)

    def get_rename_prop(self) -> Dict[str, str]:
        '''
        Returns the dictionary that the rename operation wants
        '''
        if self.name != RENAME:
            raise ValueError('This is only supported on rename nodes')
        r = {}
        for i in self.prop.split(','):
            q = i.split(ARROW)
            r[q[0].strip()] = q[1].strip()
        return r

    def set_rename_prop(self, renames: Dict[str, str]) -> None:
        '''
        Sets the prop field based on the dictionary for renames
        '''
        if self.name != RENAME:
            raise ValueError('This is only supported on rename nodes')
        self.prop = ','.join(f'{k}{ARROW}{v}' for k, v in renames.items())


def parse_tokens(expression: List[Union[list, str]]) -> Node:
    '''Generates the tree from the tokenized expression
    If no expression is specified then it will create an empty node'''
    if len(expression) == 0:
        raise ParserException('Failed to parse empty expression')

    # If the list contains only a list, it will consider the lower level list.
    # This will allow things like ((((((a))))) to work
    while len(expression) == 1 and isinstance(expression[0], list):
        expression = expression[0]

    # The list contains only 1 string. Means it is the name of a relation
    if len(expression) == 1:

        if not rtypes.is_valid_relation_name(expression[0]):
            raise ParserException(
                u"'%s' is not a valid relation name" % expression[0])
        return Variable(expression[0]) #FIXME Move validation in the object

    # Expression from right to left, searching for binary operators
    # this means that binary operators have lesser priority than
    # unary operators.
    # It finds the operator with lesser priority, uses it as root of this
    # (sub)tree using everything on its left as left parameter (so building
    # a left subtree with the part of the list located on left) and doing
    # the same on right.
    # Since it searches for strings, and expressions into parenthesis are
    # within sub-lists, they won't be found here, ensuring that they will
    # have highest priority.
    for i in range(len(expression) - 1, -1, -1):
        if expression[i] in b_operators:  # Binary operator


            if len(expression[:i]) == 0:
                raise ParserException(
                    u"Expected left operand for '%s'" % self.name)

            if len(expression[i + 1:]) == 0:
                raise ParserException(
                    u"Expected right operand for '%s'" % self.name)
            return Binary(expression[i], parse_tokens(expression[:i]), parse_tokens(expression[i + 1:]))
    '''Searches for unary operators, parsing from right to left'''
    for i in range(len(expression) - 1, -1, -1):
        if expression[i] in u_operators:  # Unary operator
            if len(expression) <= i + 2:
                raise ParserException(
                    u"Expected more tokens in '%s'" % self.name)

            return Unary(
                expression[i],
                prop=expression[1 + i].strip(),
                child=parse_tokens(expression[2 + i])
            )
    raise ParserException(f'Parse error on {expression!r}')


def _find_matching_parenthesis(expression: str, start=0, openpar='(', closepar=')') -> Optional[int]:
    '''This function returns the position of the matching
    close parenthesis to the 1st open parenthesis found
    starting from start (0 by default)'''
    par_count = 0  # Count of parenthesis

    string = False
    escape = False

    for i in range(start, len(expression)):
        if expression[i] == '\'' and not escape:
            string = not string
        if expression[i] == '\\' and not escape:
            escape = True
        else:
            escape = False
        if string:
            continue

        if expression[i] == openpar:
            par_count += 1
        elif expression[i] == closepar:
            par_count -= 1
            if par_count == 0:
                return i  # Closing parenthesis of the parameter
    return None

def _find_token(haystack: str, needle: str) -> int:
    '''
    Like the string function find, but
    ignores tokens that are within a string
    literal.
    '''
    r = -1
    string = False
    escape = False

    for i in range(len(haystack)):
        if haystack[i] == '\'' and not escape:
            string = not string
        if haystack[i] == '\\' and not escape:
            escape = True
        else:
            escape = False
        if string:
            continue

        if haystack[i:].startswith(needle):
            return i
    return r


def tokenize(expression: str) -> list:
    '''This function converts a relational expression into a list where
    every token of the expression is an item of a list. Expressions into
    parenthesis will be converted into sublists.'''

    # List for the tokens
    items = [] #  type: List[Union[str,list]]

    expression = expression.strip()  # Removes initial and ending spaces

    while len(expression) > 0:
        if expression.startswith('('):  # Parenthesis state
            end = _find_matching_parenthesis(expression)
            if end is None:
                raise TokenizerException(
                    "Missing matching ')' in '%s'" % expression)
            # Appends the tokenization of the content of the parenthesis
            items.append(tokenize(expression[1:end]))
            # Removes the entire parentesis and content from the expression
            expression = expression[end + 1:].strip()

        elif expression.startswith((SELECTION, RENAME, PROJECTION)):  # Unary operators
            items.append(expression[0:1])
                         # Adding operator in the top of the list
            expression = expression[
                1:].strip()  # Removing operator from the expression

            if expression.startswith('('):  # Expression with parenthesis, so adding what's between open and close without tokenization
                par = expression.find(
                    '(', _find_matching_parenthesis(expression))
            else:  # Expression without parenthesis, so adding what's between start and parenthesis as whole
                par = _find_token(expression, '(')

            items.append(expression[:par].strip())
                         # Inserting parameter of the operator
            expression = expression[
                par:].strip()  # Removing parameter from the expression
        else:  # Relation (hopefully)
            expression += ' '  # To avoid the special case of the ending

            # Initial part is a relation, stop when the name of the relation is
            # over
            for r in range(1, len(expression)):
                if rtypes.RELATION_NAME_REGEXP.match(expression[:r + 1]) is None:
                    break
            items.append(expression[:r])
            expression = expression[r:].strip()
    return items


def tree(expression: str) -> Node:
    '''This function parses a relational algebra expression into a AST and returns
    the root node using the Node class.'''
    return parse_tokens(tokenize(expression))


def parse(expr: str) -> CallableString:
    '''This function parses a relational algebra expression, and returns a
    CallableString (a string that can be called) whith the corresponding
    Python expression.
    '''
    return tree(expr).toPython()
