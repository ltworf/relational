# Relational
# Copyright (C) 2016  Salvo "LtWorf" Tomaselli
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
# This module splits a query into a program.


from relational import parser


class Program:
    def __init__(self, rels):
        self.queries = []
        self.dictionary = {} # Key is the query, value is the relation
        self.vgen = vargen(rels, 'optm_')

    def __str__(self):
        r = ''
        for q in self.queries:
            r += '%s = %s' % (q[0], q[1]) + '\n'
        return r.rstrip()

    def append_query(self, node):
        strnode = str(node)

        rel = self.dictionary.get(strnode)
        if rel:
            return rel

        qname = next(self.vgen)
        self.queries.append((qname, node))
        n = parser.Node()
        n.kind = parser.RELATION
        n.name = qname
        self.dictionary[strnode] = n
        return n

def _separate(node, program):
    if node.kind == parser.UNARY and node.child.kind != parser.RELATION:
        _separate(node.child, program)
        rel = program.append_query(node.child)
        node.child = rel
    elif node.kind == parser.BINARY:
        if node.left.kind != parser.RELATION:
            _separate(node.left, program)
            rel = program.append_query(node.left)
            node.left = rel
        if node.right.kind != parser.RELATION:
            _separate(node.right, program)
            rel = program.append_query(node.right)
            node.right = rel
    program.append_query(node)

def vargen(avoid, prefix=''):
    '''
    Generates temp variables.

    Avoid contains variable names to skip.
    '''
    count = 0

    while True:
        r = ''
        c = count
        while True:
            r = chr((c % 26) + 97) + r
            if c < 26:
                break
            c //= 26

        r = prefix + r
        if r not in avoid:
            yield r
        count += 1

def split(node, rels):
    '''
    Split a query into a program.

    The idea is that if there are duplicated subdtrees they
    get executed only once.
    '''
    p = Program(rels)
    _separate(node, p)
    return str(p)
