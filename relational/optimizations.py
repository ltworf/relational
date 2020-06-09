# Relational
# Copyright (C) 2009-2020  Salvo "LtWorf" Tomaselli
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
# This module contains functions to perform various optimizations on the expression trees.
# The list general_optimizations contains pointers to general functions, so they can be called
# within a cycle.
#
# It is possible to add new general optimizations by adding the function in the list
# general_optimizations present in this module. And the optimization will be executed with the
# other ones when optimizing.
#
# A function will have one parameter, which is the root node of the tree describing the expression.
# The class used is defined in optimizer module.
# A function will have to return the number of changes performed on the tree.

from io import StringIO
from tokenize import generate_tokens
from typing import Tuple


from relational import parser

sel_op = (
    '//=', '**=', 'and', 'not', 'in', '//', '**', '<<', '>>', '==', '!=', '>=', '<=', '+=', '-=',
    '*=', '/=', '%=', 'or', '+', '-', '*', '/', '&', '|', '^', '~', '<', '>', '%', '=', '(', ')', ',', '[', ']')

PRODUCT = parser.PRODUCT
DIFFERENCE = parser.DIFFERENCE
UNION = parser.UNION
INTERSECTION = parser.INTERSECTION
DIVISION = parser.DIVISION
JOIN = parser.JOIN
JOIN_LEFT = parser.JOIN_LEFT
JOIN_RIGHT = parser.JOIN_RIGHT
JOIN_FULL = parser.JOIN_FULL
PROJECTION = parser.PROJECTION
SELECTION = parser.SELECTION
RENAME = parser.RENAME
ARROW = parser.ARROW


def find_duplicates(node, dups=None):
    '''
    Finds repeated subtrees in a parse
    tree.
    '''
    if dups is None:
        dups = {}
    dups[str(node)] = node



def replace_leaves(node, context):
    '''
    Node is a parsed tree
    context is a dictionary containing
    parsed trees as values.

    If a name appearing in node appears
    also in context, the parse tree is
    modified to replace the node with the
    subtree found in context.
    '''
    if node.kind == parser.UNARY:
        replace_leaves(node.child, context)
    elif node.kind == parser.BINARY:
        replace_leaves(node.left, context)
        replace_leaves(node.right, context)
    elif node.name in context:
        replace_node(node, context[node.name])


def replace_node(replace, replacement):
    '''This function replaces "replace" node with the node "with",
    the father of the node will now point to the with node'''
    replace.name = replacement.name
    replace.kind = replacement.kind

    if replace.kind == parser.UNARY:
        replace.child = replacement.child
        replace.prop = replacement.prop
    elif replace.kind == parser.BINARY:
        replace.right = replacement.right
        replace.left = replacement.left


def duplicated_select(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates and deletes things like
    σ a ( σ a(C)) and the ones like σ a ( σ b(C))
    replacing the 1st one with a single select and
    the 2nd one with a single select with both conditions
    in and
    '''
    changes = 0
    while n.name == SELECTION and n.child.name == SELECTION:
        changes += 1
        prop = n.prop

        if n.prop != n.child.prop:  # Nested but different, joining them
            prop = n.prop + " and " + n.child.prop

            # This adds parenthesis if they are needed
            if n.child.prop.startswith('(') or n.prop.startswith('('):
                prop = '(%s)' % prop
        n = parser.Unary(
            SELECTION,
            prop,
            n.child.child,
        )
    return n, changes


def futile_union_intersection_subtraction(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates things like r ∪ r, and replaces them with r.
    R ∪ R  --> R
    R ∩ R --> R
    R - R --> σ False (R)
    σ k (R) - R --> σ False (R)
    R - σ k (R) --> σ not k (R)
    σ k (R) ∪ R --> R
    σ k (R) ∩ R --> σ k (R)
    '''

    changes = 0

    # Union and intersection of the same thing
    if n.name in (UNION, INTERSECTION, JOIN, JOIN_LEFT, JOIN_RIGHT, JOIN_FULL) and n.left == n.right:
        return n.left, 1

    # selection and union of the same thing
    elif (n.name == UNION):
        if n.left.name == SELECTION and n.left.child == n.right:
            return n.right, 1
        elif n.right.name == SELECTION and n.right.child == n.left:
            return n.left, 1

    # selection and intersection of the same thing
    elif n.name == INTERSECTION:
        if n.left.name == SELECTION and n.left.child == n.right:
            return n.left, 1
        elif n.right.name == SELECTION and n.right.child == n.left:
            return n.right, 1

    # Subtraction and selection of the same thing
    elif n.name == DIFFERENCE and \
            n.right.name == SELECTION and \
            n.right.child == n.left:
        return parser.Unary(
            SELECTION,
            '(not (%s))' % n.right.prop,
            n.right.child), 1

    # Subtraction of the same thing or with selection on the left child
    elif n.name == DIFFERENCE and (n.left == n.right or (n.left.name == SELECTION and n.left.child == n.right)):
        return parser.Unary(
            SELECTION,
            'False',
            n.get_left_leaf()
        ), 1
    return n, 0


def down_to_unions_subtractions_intersections(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This funcion locates things like σ i==2 (c ∪ d), where the union
    can be a subtraction and an intersection and replaces them with
    σ i==2 (c) ∪ σ i==2(d).
    '''
    changes = 0
    _o = (UNION, DIFFERENCE, INTERSECTION)
    if n.name == SELECTION and n.child.name in _o:
        l = parser.Unary(SELECTION, n.prop, n.child.left)
        r = parser.Unary(SELECTION, n.prop, n.child.right)

        return parser.Binary(n.child.name, l, r), 1
    return n, 0


def duplicated_projection(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates thing like π i ( π j (R)) and replaces
    them with π i (R)'''

    if n.name == PROJECTION and n.child.name == PROJECTION:
        return parser.Unary(
            PROJECTION,
            n.prop,
            n.child.child), 1
    return n, 0


def selection_inside_projection(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates things like  σ j (π k(R)) and
    converts them into π k(σ j (R))'''
    if n.name == SELECTION and n.child.name == PROJECTION:
        child = parser.Unary(
            SELECTION,
            n.prop,
            n.child.child
        )

        return parser.Unary(PROJECTION, n.child.prop, child), 0
    return n, 0


def swap_union_renames(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates things like
    ρ a➡b(R) ∪ ρ a➡b(Q)
    and replaces them with
    ρ a➡b(R ∪ Q).
    Does the same with subtraction and intersection'''
    if n.name in (DIFFERENCE, UNION, INTERSECTION) and n.left.name == RENAME and n.right.name == RENAME:
        l_vars = n.left.get_rename_prop()
        r_vars = n.right.get_rename_prop()
        if r_vars == l_vars:
            child = parser.Binary(n.name, n.left.child, n.right.child)
            return parser.Unary(RENAME, n.left.prop, child), 1
    return n, 0


def futile_renames(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function purges renames like
    ρ id->id,a->q (A)
    into
    ρ a->q (A)

    or removes the operation entirely if they all get removed
    '''
    if n.name == RENAME:
        renames = n.get_rename_prop()
        changes = False
        for k, v in renames.items():
            if k == v:
                changes = True
                del renames[k]
        if len(renames) == 0: # Nothing to rename, removing the rename
            return n.child, 1
        elif changes:
            # Changing the node in place, no need to return to cause a recursive step
            n.set_rename_prop(renames)

    return n, 0


def subsequent_renames(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function removes redundant subsequent renames joining them into one
    ρ .. ρ .. (A)
    into
    ρ ... (A)
    '''
    if n.name == RENAME and n.child.name == RENAME:
        # Located two nested renames.
        prop = n.prop + ',' + n.child.prop
        child = n.child.child
        n = parser.Unary(RENAME, prop, child)

        # Creating a dictionary with the attributes
        renames = n.get_rename_prop()

        # Scans dictionary to locate things like "a->b,b->c" and replace them
        # with "a->c"
        for key, value in tuple(renames.items()):

            if value in renames:
                if renames[value] != key:
                    # Double rename on attribute
                    renames[key] = renames[renames[key]]  # Sets value
                    del renames[value]  # Removes the unused one
                else:  # Cycle rename a->b,b->a
                    del renames[value] # Removes the unused one
                    del renames[key] # Removes the unused one

        if len(renames) == 0:  # Nothing to rename, removing the rename op
            return n.child, 1
        else:
            n.set_rename_prop(renames)
            return n, 1

    return n, 0


class level_string(str):
    level = 0


def tokenize_select(expression):
    '''This function returns the list of tokens present in a
    selection. The expression can contain parenthesis.
    It will use a subclass of str with the attribute level, which
    will specify the nesting level of the token into parenthesis.'''
    g = generate_tokens(StringIO(str(expression)).readline)
    l = list(token[1] for token in g)

    l.remove('')

    # Changes the 'a','.','method' token group into a single 'a.method' token
    try:
        while True:
            dot = l.index('.')
            l[dot] = '%s.%s' % (l[dot - 1], l[dot + 1])
            l.pop(dot + 1)
            l.pop(dot - 1)
    except:
        pass

    level = 0
    for i in range(len(l)):
        l[i] = level_string(l[i])
        l[i].level = level

        if l[i] == '(':
            level += 1
        elif l[i] == ')':
            level -= 1

    return l


def swap_rename_projection(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates things like
    π k(ρ j(R))
    and replaces them with
    ρ j(π k(R)).
    This will let rename work on a hopefully smaller set
    and more important, will hopefully allow further optimizations.

    Will also eliminate fields in the rename that are cut in the projection.
    '''

    if n.name == PROJECTION and n.child.name == RENAME:
        # π index,name(ρ id➡index(R))
        renames = n.child.get_rename_prop()
        projections = set(n.get_projection_prop())

        # Use pre-rename names in the projection
        for k, v in renames.items():
            if v in projections:
                projections.remove(v)
                projections.add(k)

        # Eliminate fields
        for i in list(renames.keys()):
            if i not in projections:
                del renames[i]

        child = parser.Unary(PROJECTION,'' , n.child.child)
        child.set_projection_prop(projections)
        n = parser.Unary(RENAME, '', child)
        n.set_rename_prop(renames)
        return n, 1

    return n, 0


def swap_rename_select(n: parser.Node) -> int:
    '''This function locates things like
    σ k(ρ j(R))
    and replaces them with
    ρ j(σ k(R)).
    Renaming the attributes used in the
    selection, so the operation is still valid.'''

    if n.name == SELECTION and n.child.name == RENAME:
        # This is an inverse mapping for the rename
        renames = {v: k for k, v in n.child.get_rename_prop().items()}

        # tokenizes expression in select
        tokens = tokenize_select(n.prop)

        # Renaming stuff, no enum because I edit the tokens
        for i in range(len(tokens)):
            splitted = tokens[i].split('.', 1)
            if splitted[0] in renames:
                tokens[i] = renames[splitted[0]]
                if len(splitted) > 1:
                    tokens[i] += '.' + splitted[1]

        child = parser.Unary(SELECTION, ' '.join(tokens), n.child.child)
        return parser.Unary(RENAME, n.child.prop, child), 1
    return n, 0


def select_union_intersect_subtract(n: parser.Node) -> int:
    '''This function locates things like σ i(a) ∪ σ q(a)
    and replaces them with σ (i OR q) (a)
    Removing a O(n²) operation like the union'''
    changes = 0
    if n.name in {UNION, INTERSECTION, DIFFERENCE} and \
                n.left.name == SELECTION and \
                n.right.name == SELECTION and \
                n.left.child == n.right.child:
        changes = 1

        d = {UNION: 'or', INTERSECTION: 'and', DIFFERENCE: 'and not'}
        op = d[n.name]

        newnode = parser.Node()

        if n.left.prop.startswith('(') or n.right.prop.startswith('('):
            t_str = '('
            if n.left.prop.startswith('('):
                t_str += '(%s)'
            else:
                t_str += '%s'
            t_str += ' %s '
            if n.right.prop.startswith('('):
                t_str += '(%s)'
            else:
                t_str += '%s'
            t_str += ')'

            newnode.prop = t_str % (n.left.prop, op, n.right.prop)
        else:
            newnode.prop = '%s %s %s' % (n.left.prop, op, n.right.prop)
        newnode.name = SELECTION
        newnode.child = n.left.child
        newnode.kind = parser.UNARY
        replace_node(n, newnode)

    return changes + recoursive_scan(select_union_intersect_subtract, n)


def union_and_product(n: parser.Node) -> Tuple[parser.Node, int]:
    '''
    A * B ∪ A * C = A * (B ∪ C)
    Same thing with inner join
    '''
    if n.name == UNION and n.left.name in {PRODUCT, JOIN} and n.left.name == n.right.name:

        if n.left.left == n.right.left or n.left.left == n.right.right:
            l = n.left.right
            r = n.right.left if n.left.left == n.right.right else n.right.right
            newchild = parser.Binary(UNION, l, r)
            return parser.Binary(n.left.name, n.left.left, newchild), 1
        elif n.left.right == n.right.left or n.left.left == n.right.right:
            l = n.left.left
            r = n.right.left if n.right.left == n.right.right else n.right.right
            newchild = parser.Binary(UNION, l, r)
            return parser.Binary(n.left.name, n.left.right, newchild), 1
    return n, 0


def projection_and_union(n, rels):
    '''
    Turns
        π a,b,c(A) ∪ π a,b,c(B)

    into
        π a,b,c(A ∪ B)

    if A and B are union compatible
    '''
    changes = 0
    if n.name == UNION and \
            n.left.name == PROJECTION and \
            n.right.name == PROJECTION and \
            set(n.left.child.result_format(rels)) == set(n.right.child.result_format(rels)):
        newchild = parser.Node()

        newchild.kind = parser.BINARY
        newchild.name = UNION
        newchild.left = n.left.child
        newchild.right = n.right.child

        newnode = parser.Node()
        newnode.child = newchild
        newnode.kind = parser.UNARY
        newnode.name = PROJECTION
        newnode.prop = n.right.prop
        replace_node(n, newnode)
        changes = 1
    return n, 0


def selection_and_product(n, rels):
    '''This function locates things like σ k (R*Q) and converts them into
    σ l (σ j (R) * σ i (Q)). Where j contains only attributes belonging to R,
    i contains attributes belonging to Q and l contains attributes belonging to both'''
    changes = 0

    if n.name == SELECTION and n.child.name in (PRODUCT, JOIN):
        l_attr = n.child.left.result_format(rels)
        r_attr = n.child.right.result_format(rels)

        tokens = tokenize_select(n.prop)
        groups = []
        temp = []

        for i in tokens:
            if i == 'and' and i.level == 0:
                groups.append(temp)
                temp = []
            else:
                temp.append(i)
        if len(temp) != 0:
            groups.append(temp)
            temp = []

        left = []
        right = []
        both = []

        for i in groups:
            l_fields = False  # has fields in left?
            r_fields = False  # has fields in left?

            for j in set(i).difference(sel_op):
                j = j.split('.')[0]
                if j in l_attr:  # Field in left
                    l_fields = True
                if j in r_attr:  # Field in right
                    r_fields = True

            if l_fields and r_fields:  # Fields in both
                both.append(i)
            elif l_fields:
                left.append(i)
            elif r_fields:
                right.append(i)
            else:  # Unknown.. adding in both
                both.append(i)

        # Preparing left selection
        if len(left) > 0:
            changes = 1
            l_node = parser.Node()
            l_node.name = SELECTION
            l_node.kind = parser.UNARY
            l_node.child = n.child.left
            l_node.prop = ''
            n.child.left = l_node
            while len(left) > 0:
                c = left.pop(0)
                for i in c:
                    l_node.prop += i + ' '
                if len(left) > 0:
                    l_node.prop += ' and '
            if '(' in l_node.prop:
                l_node.prop = '(%s)' % l_node.prop

        # Preparing right selection
        if len(right) > 0:
            changes = 1
            r_node = parser.Node()
            r_node.name = SELECTION
            r_node.prop = ''
            r_node.kind = parser.UNARY
            r_node.child = n.child.right
            n.child.right = r_node
            while len(right) > 0:
                c = right.pop(0)
                r_node.prop += ' '.join(c)
                if len(right) > 0:
                    r_node.prop += ' and '
            if '(' in r_node.prop:
                r_node.prop = '(%s)' % r_node.prop
        # Changing main selection
        n.prop = ''
        if len(both) != 0:
            while len(both) > 0:
                c = both.pop(0)
                n.prop += ' '.join(c)
                if len(both) > 0:
                    n.prop += ' and '
            if '(' in n.prop:
                n.prop = '(%s)' % n.prop
        else:  # No need for general select
            replace_node(n, n.child)

    return changes + recoursive_scan(selection_and_product, n, rels)


def useless_projection(n, rels) -> int:
    '''
    Removes projections that are over all the fields
    '''
    changes = 0
    if n.name == PROJECTION and \
            set(n.child.result_format(rels)) == set(i.strip() for i in n.prop.split(',')):
        changes = 1
        replace_node(n, n.child)

    return changes + recursive_scan(useless_projection, n, rels)

general_optimizations = [
    duplicated_select,
    down_to_unions_subtractions_intersections,
    duplicated_projection,
    selection_inside_projection,
    subsequent_renames,
    futile_renames,
    swap_rename_select,
    futile_union_intersection_subtraction,
    swap_union_renames,
    swap_rename_projection,
    #select_union_intersect_subtract,
    union_and_product,
]
specific_optimizations = [
    #selection_and_product,
    #projection_and_union,
    #useless_projection,
]
