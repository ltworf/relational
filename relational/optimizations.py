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
from typing import Tuple, Dict, List

from relational.relation import Relation
from relational import parser
from relational.parser import Binary, Unary, PRODUCT, \
    DIFFERENCE, UNION, INTERSECTION, DIVISION, JOIN, \
    JOIN_LEFT, JOIN_RIGHT, JOIN_FULL, PROJECTION, \
    SELECTION, RENAME, ARROW

sel_op = (
    '//=', '**=', 'and', 'not', 'in', '//', '**', '<<', '>>', '==', '!=', '>=', '<=', '+=', '-=',
    '*=', '/=', '%=', 'or', '+', '-', '*', '/', '&', '|', '^', '~', '<', '>', '%', '=', '(', ')', ',', '[', ']')


def find_duplicates(node, dups=None):
    '''
    Finds repeated subtrees in a parse
    tree.
    '''
    if dups is None:
        dups = {}
    dups[str(node)] = node


def duplicated_select(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates and deletes things like
    σ a ( σ a(C)) and the ones like σ a ( σ b(C))
    replacing the 1st one with a single select and
    the 2nd one with a single select with both conditions
    in and
    '''
    changes = 0
    while isinstance(n, Unary) and n.name == SELECTION and isinstance(n.child, Unary) and n.child.name == SELECTION:
        changes += 1
        prop = n.prop

        if n.prop != n.child.prop:  # Nested but different, joining them
            prop = n.prop + " and " + n.child.prop

            # This adds parenthesis if they are needed
            if n.child.prop.startswith('(') or n.prop.startswith('('):
                prop = '(%s)' % prop
        n = Unary(
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

    if not isinstance(n, Binary):
        return n, 0

    # Union and intersection of the same thing
    if n.name in (UNION, INTERSECTION, JOIN, JOIN_LEFT, JOIN_RIGHT, JOIN_FULL) and n.left == n.right:
        return n.left, 1

    # selection and union of the same thing
    elif n.name == UNION:
        if n.left.name == SELECTION and isinstance(n.left, Unary) and n.left.child == n.right:
            return n.right, 1
        elif n.right.name == SELECTION and isinstance(n.right, Unary) and n.right.child == n.left:
            return n.left, 1

    # selection and intersection of the same thing
    elif n.name == INTERSECTION:
        if n.left.name == SELECTION and n.left.child == n.right:
            return n.left, 1
        elif n.right.name == SELECTION and \
                isinstance(n.right, Unary) and \
                n.right.child == n.left:
            return n.right, 1

    # Subtraction and selection of the same thing
    elif n.name == DIFFERENCE and \
            isinstance(n, Binary) and \
            n.right.name == SELECTION and \
            isinstance(n.right, Unary) and \
            n.right.child == n.left:
        return Unary(
            SELECTION,
            '(not (%s))' % n.right.prop,
            n.right.child), 1

    # Subtraction of the same thing or with selection on the left child
    elif n.name == DIFFERENCE and \
            isinstance(n, Binary) and \
            (n.left == n.right or (n.left.name == SELECTION and n.left.child == n.right)):
        return Unary(
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
    if isinstance(n, Unary) and n.name == SELECTION and n.child.name in _o:
        assert isinstance(n.child, Binary)
        l = Unary(SELECTION, n.prop, n.child.left)
        r = Unary(SELECTION, n.prop, n.child.right)

        return Binary(n.child.name, l, r), 1
    return n, 0


def duplicated_projection(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates thing like π i ( π j (R)) and replaces
    them with π i (R)'''

    if isinstance(n, Unary) and n.name == PROJECTION and isinstance(n.child, Unary) and n.child.name == PROJECTION:
        return Unary(
            PROJECTION,
            n.prop,
            n.child.child), 1
    return n, 0


def selection_inside_projection(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates things like  σ j (π k(R)) and
    converts them into π k(σ j (R))'''
    if isinstance(n, Unary) and n.name == SELECTION and isinstance(n.child, Unary) and n.child.name == PROJECTION:
        child = Unary(
            SELECTION,
            n.prop,
            n.child.child
        )

        return Unary(PROJECTION, n.child.prop, child), 0
    return n, 0


def swap_union_renames(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates things like
    ρ a➡b(R) ∪ ρ a➡b(Q)
    and replaces them with
    ρ a➡b(R ∪ Q).
    Does the same with subtraction and intersection'''
    if n.name in (DIFFERENCE, UNION, INTERSECTION) and \
            isinstance(n, Binary) and \
            n.left.name == RENAME and \
            isinstance(n.left, Unary) and\
            n.right.name == RENAME and \
            isinstance(n.right, Unary):
        l_vars = n.left.get_rename_prop()
        r_vars = n.right.get_rename_prop()
        if r_vars == l_vars:
            child = Binary(n.name, n.left.child, n.right.child)
            return Unary(RENAME, n.left.prop, child), 1
    return n, 0


def futile_renames(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function purges renames like
    ρ id->id,a->q (A)
    into
    ρ a->q (A)

    or removes the operation entirely if they all get removed
    '''
    if isinstance(n, Unary) and n.name == RENAME:
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
    if isinstance(n, Unary) and \
            n.name == RENAME and \
            isinstance(n.child, Unary) and \
            n.child.name == RENAME:
        # Located two nested renames.
        prop = n.prop + ',' + n.child.prop
        child = n.child.child
        n = Unary(RENAME, prop, child)

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


class LevelString(str):
    level = 0


def tokenize_select(expression: str) -> List[LevelString]:
    '''This function returns the list of tokens present in a
    selection. The expression can contain parenthesis.
    It will use a subclass of str with the attribute level, which
    will specify the nesting level of the token into parenthesis.'''
    g = generate_tokens(StringIO(str(expression)).readline)
    l = list(token[1] for token in g)

    # Changes the 'a','.','method' token group into a single 'a.method' token
    try:
        while True:
            dot = l.index('.')
            l[dot] = '%s.%s' % (l[dot - 1], l[dot + 1])
            l.pop(dot + 1)
            l.pop(dot - 1)
    except:
        pass

    r = []
    level = 0
    for i in l:
        if not i:
            continue
        value = LevelString(i)
        value.level = level

        if value == '(':
            level += 1
        elif value == ')':
            level -= 1
        r.append(value)

    return r


def swap_rename_projection(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates things like
    π k(ρ j(R))
    and replaces them with
    ρ j(π k(R)).
    This will let rename work on a hopefully smaller set
    and more important, will hopefully allow further optimizations.

    Will also eliminate fields in the rename that are cut in the projection.
    '''

    if isinstance(n, Unary) and \
            n.name == PROJECTION and \
            isinstance(n.child, Unary) and \
            n.child.name == RENAME:
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

        child = Unary(PROJECTION,'' , n.child.child)
        child.set_projection_prop(list(projections))
        n = Unary(RENAME, '', child)
        n.set_rename_prop(renames)
        return n, 1

    return n, 0


def swap_rename_select(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates things like
    σ k(ρ j(R))
    and replaces them with
    ρ j(σ k(R)).
    Renaming the attributes used in the
    selection, so the operation is still valid.'''

    if isinstance(n, Unary) and \
            n.name == SELECTION and \
            isinstance(n.child, Unary) and \
            n.child.name == RENAME:
        # This is an inverse mapping for the rename
        renames = {v: k for k, v in n.child.get_rename_prop().items()}

        # tokenizes expression in select
        tokens = tokenize_select(n.prop)

        # Renaming stuff, no enum because I edit the tokens
        for i in range(len(tokens)):
            splitted = tokens[i].split('.', 1)
            if splitted[0] in renames:
                tokens[i] = LevelString(renames[splitted[0]])
                if len(splitted) > 1:
                    tokens[i] = LevelString(tokens[i] + '.' + splitted[1])

        child = Unary(SELECTION, ' '.join(tokens), n.child.child)
        return Unary(RENAME, n.child.prop, child), 1
    return n, 0


def select_union_intersect_subtract(n: parser.Node) -> Tuple[parser.Node, int]:
    '''This function locates things like
    σ i(a) ∪ σ q(a)
    and replaces them with
    σ (i OR q) (a)
    Removing a O(n²) operation like the union'''
    if isinstance(n, Binary) and \
            n.name in {UNION, INTERSECTION, DIFFERENCE} and \
            isinstance(n.left, Unary) and \
            n.left.name == SELECTION and \
            isinstance(n.right, Unary) and \
            n.right.name == SELECTION and \
            n.left.child == n.right.child:
        d = {UNION: 'or', INTERSECTION: 'and', DIFFERENCE: 'and not'}
        op = d[n.name]

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

            prop = t_str % (n.left.prop, op, n.right.prop)
        else:
            prop = '%s %s %s' % (n.left.prop, op, n.right.prop)
        return Unary(SELECTION, prop, n.left.child), 1
    return n, 0


def union_and_product(n: parser.Node) -> Tuple[parser.Node, int]:
    '''
    A * B ∪ A * C = A * (B ∪ C)
    Same thing with inner join
    '''
    if isinstance(n, Binary) and \
            n.name == UNION and \
            isinstance(n.left, Binary) and \
            n.left.name in {PRODUCT, JOIN} and \
            isinstance(n.right, Binary) and \
            n.left.name == n.right.name:

        if n.left.left == n.right.left or n.left.left == n.right.right:
            l = n.left.right
            r = n.right.left if n.left.left == n.right.right else n.right.right
            newchild = Binary(UNION, l, r)
            return Binary(n.left.name, n.left.left, newchild), 1
        elif n.left.right == n.right.left or n.left.left == n.right.right:
            l = n.left.left
            r = n.right.left if n.right.left == n.right.right else n.right.right
            newchild = Binary(UNION, l, r)
            return Binary(n.left.name, n.left.right, newchild), 1
    return n, 0


def projection_and_union(n: parser.Node, rels: Dict[str, Relation]) -> Tuple[parser.Node, int]:
    '''
    Turns
        π a,b,c(A) ∪ π a,b,c(B)

    into
        π a,b,c(A ∪ B)

    if A and B are union compatible
    '''
    changes = 0
    if n.name == UNION and \
            isinstance(n, Binary) and \
            n.left.name == PROJECTION and \
            isinstance(n.left, Unary) and \
            n.right.name == PROJECTION and \
            isinstance(n.right, Unary) and \
            set(n.left.child.result_format(rels)) == set(n.right.child.result_format(rels)):
        child = Binary(UNION, n.left.child, n.right.child)
        return Unary(PROJECTION, n.right.prop, child), 0
    return n, 0


def selection_and_product(n: parser.Node, rels: Dict[str, Relation]) -> Tuple[parser.Node, int]:
    '''This function locates things like σ k (R*Q) and converts them into
    σ l (σ j (R) * σ i (Q)). Where j contains only attributes belonging to R,
    i contains attributes belonging to Q and l contains attributes belonging to both'''

    if isinstance(n, Unary) and n.name == SELECTION and \
            isinstance(n.child, Binary) and \
            n.child.name in (PRODUCT, JOIN):
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

            if l_fields and not r_fields:
                left.append(i)
            elif r_fields and not l_fields:
                right.append(i)
            else:  # Unknown.. adding in both
                both.append(i)

        # Preparing left selection
        if left:
            l_prop = ' and '.join((' '.join(i) for i in left))
            if '(' in l_prop:
                l_prop = '(%s)' % l_prop
            l_node = Unary(SELECTION, l_prop, n.child.left)
        else:
            l_node = n.child.left

        # Preparing right selection
        if right:
            r_prop = ' and '.join((' '.join(i) for i in right))
            if '(' in r_prop:
                r_prop = '(%s)' % r_prop
            r_node = Unary(SELECTION, r_prop, n.child.right)
        else:
            r_node = n.child.right

        b_node = Binary(n.child.name, l_node, r_node)

        # Changing main selection
        if both:
            both_prop = ' and '.join((' '.join(i) for i in both))
            if '(' in both_prop:
                both_prop = '(%s)' % both_prop
            r = Unary(SELECTION, both_prop, b_node)
            return r, len(left) + len(right)
        else:  # No need for general select
            return b_node, 1

    return n, 0


def useless_projection(n: parser.Node, rels: Dict[str, Relation]) -> Tuple[parser.Node, int]:
    '''
    Removes projections that are over all the fields
    '''
    if isinstance(n, Unary) and n.name == PROJECTION and \
            set(n.child.result_format(rels)) == set(i.strip() for i in n.prop.split(',')):
        return n.child, 1

    return n, 0

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
    select_union_intersect_subtract,
    union_and_product,
]
specific_optimizations = [
    selection_and_product,
    projection_and_union,
    useless_projection,
]
