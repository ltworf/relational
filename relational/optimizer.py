# Relational
# Copyright (C) 2008-2016  Salvo "LtWorf" Tomaselli
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
# This module optimizes relational expressions into ones that require less time to be executed.
#
# expression: In all the functions expression can be either an UTF-8 encoded string, containing a valid
# relational query, or it can be a parse tree for a relational expression (ie: class parser.node).
# The functions will always return a string with the optimized query, but if a parse tree was provided,
# the parse tree itself will be modified accordingly.
from typing import Union, Optional, Dict, Any

from relational import optimizations
from relational.parser import Node, RELATION, UNARY, BINARY, op_functions, tokenize, tree
from relational import querysplit
from relational.maintenance import UserInterface

ContextDict = Dict[str,Any]


def optimize_program(code, rels: ContextDict):
    '''
    Optimize an entire program, composed by multiple expressions
    and assignments.
    '''
    lines = code.split('\n')
    context = {} #  type: ContextDict

    for line in  lines:
        line = line.strip()
        if line.startswith(';') or not line:
            continue
        res, query = UserInterface.split_query(line)
        last_res = res
        parsed = tree(query)
        optimizations.replace_leaves(parsed, context)
        context[res] = parsed
    node = optimize_all(context[last_res], rels, tostr=False)
    return querysplit.split(node, rels)


def optimize_all(expression: Union[str, Node], rels: ContextDict, specific: bool = True, general: bool = True, debug: Optional[list] = None, tostr: bool = True) -> Union[str, Node]:
    '''This function performs all the available optimizations.

    expression : see documentation of this module
    rels: dic with relation name as key, and relation istance as value
    specific: True if it has to perform specific optimizations
    general: True if it has to perform general optimizations
    debug: if a list is provided here, after the end of the function, it
        will contain the query repeated many times to show the performed
        steps.

    Return value: this will return an optimized version of the expression'''
    if isinstance(expression, str):
        n = tree(expression)  # Gets the tree
    elif isinstance(expression, Node):
        n = expression
    else:
        raise (TypeError("expression must be a string or a node"))

    if isinstance(debug, list):
        dbg = True
    else:
        dbg = False

    total = 1
    while total != 0:
        total = 0
        if specific:
            for i in optimizations.specific_optimizations:
                res = i(n, rels)  # Performs the optimization
                if res != 0 and dbg:
                    debug.append(str(n))
                total += res
        if general:
            for i in optimizations.general_optimizations:
                res = i(n)  # Performs the optimization
                if res != 0 and dbg:
                    debug.append(str(n))
                total += res
    if tostr:
        return str(n)
    else:
        return n


def specific_optimize(expression, rels: ContextDict):
    '''This function performs specific optimizations. Means that it will need to
    know the fields used by the relations.

    expression : see documentation of this module
    rels: dic with relation name as key, and relation istance as value

    Return value: this will return an optimized version of the expression'''
    return optimize_all(expression, rels, specific=True, general=False)


def general_optimize(expression):
    '''This function performs general optimizations. Means that it will not need to
    know the fields used by the relations

    expression : see documentation of this module

    Return value: this will return an optimized version of the expression'''
    return optimize_all(expression, None, specific=False, general=True)
