# Relational
# Copyright (C) 2009-2017  Salvo "LtWorf" Tomaselli
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


def recoursive_scan(function, node, rels=None):
    '''Does a recoursive optimization on the tree.

    This function will recoursively execute the function given
    as "function" parameter starting from node to all the tree.
    if rels is provided it will be passed as argument to the function.
    Otherwise the function will be called just on the node.

    Result value: function is supposed to return the amount of changes
    it has performed on the tree.
    The various result will be added up and this final value will be the
    returned value.'''
    changes = 0
    # recoursive scan
    if node.kind == parser.UNARY:
        if rels != None:
            changes += function(node.child, rels)
        else:
            changes += function(node.child)
    elif node.kind == parser.BINARY:
        if rels != None:
            changes += function(node.right, rels)
            changes += function(node.left, rels)
        else:
            changes += function(node.right)
            changes += function(node.left)
    return changes


def duplicated_select(n):
    '''This function locates and deletes things like
    σ a ( σ a(C)) and the ones like σ a ( σ b(C))
    replacing the 1st one with a single select and
    the 2nd one with a single select with both conditions
    in and
    '''
    changes = 0
    if n.name == SELECTION and n.child.name == SELECTION:
        if n.prop != n.child.prop:  # Nested but different, joining them
            n.prop = n.prop + " and " + n.child.prop

            # This adds parenthesis if they are needed
            if n.child.prop.startswith('(') or n.prop.startswith('('):
                n.prop = '(%s)' % n.prop

        n.child = n.child.child
        changes = 1
        changes += duplicated_select(n)

    return changes + recoursive_scan(duplicated_select, n)


def futile_union_intersection_subtraction(n):
    '''This function locates things like r ᑌ r, and replaces them with r.
    R ᑌ R  --> R
    R ᑎ R --> R
    R - R --> σ False (R)
    σ k (R) - R --> σ False (R)
    R - σ k (R) --> σ not k (R)
    σ k (R) ᑌ R --> R
    σ k (R) ᑎ R --> σ k (R)
    '''

    changes = 0

    # Union and intersection of the same thing
    if n.name in (UNION, INTERSECTION, JOIN, JOIN_LEFT, JOIN_RIGHT, JOIN_FULL) and n.left == n.right:
        changes = 1
        replace_node(n, n.left)

    # selection and union of the same thing
    elif (n.name == UNION):
        if n.left.name == SELECTION and n.left.child == n.right:
            changes = 1
            replace_node(n, n.right)
        elif n.right.name == SELECTION and n.right.child == n.left:
            changes = 1
            replace_node(n, n.left)

    # selection and intersection of the same thing
    elif n.name == INTERSECTION:
        if n.left.name == SELECTION and n.left.child == n.right:
            changes = 1
            replace_node(n, n.left)
        elif n.right.name == SELECTION and n.right.child == n.left:
            changes = 1
            replace_node(n, n.right)

    # Subtraction and selection of the same thing
    elif n.name == DIFFERENCE and \
            n.right.name == SELECTION and \
            n.right.child == n.left:
        n.name = n.right.name
        n.kind = n.right.kind
        n.child = n.right.child
        n.prop = '(not (%s))' % n.right.prop
        n.left = n.right = None

    # Subtraction of the same thing or with selection on the left child
    elif n.name == DIFFERENCE and (n.left == n.right or (n.left.name == SELECTION and n.left.child == n.right)):
        changes = 1
        n.kind = parser.UNARY
        n.name = SELECTION
        n.prop = 'False'
        n.child = n.left.get_left_leaf()
        # n.left=n.right=None

    return changes + recoursive_scan(futile_union_intersection_subtraction, n)


def down_to_unions_subtractions_intersections(n):
    '''This funcion locates things like σ i==2 (c ᑌ d), where the union
    can be a subtraction and an intersection and replaces them with
    σ i==2 (c) ᑌ σ i==2(d).
    '''
    changes = 0
    _o = (UNION, DIFFERENCE, INTERSECTION)
    if n.name == SELECTION and n.child.name in _o:

        left = parser.node()
        left.prop = n.prop
        left.name = n.name
        left.child = n.child.left
        left.kind = parser.UNARY
        right = parser.node()
        right.prop = n.prop
        right.name = n.name
        right.child = n.child.right
        right.kind = parser.UNARY

        n.name = n.child.name
        n.left = left
        n.right = right
        n.child = None
        n.prop = None
        n.kind = parser.BINARY
        changes += 1

    return changes + recoursive_scan(down_to_unions_subtractions_intersections, n)


def duplicated_projection(n):
    '''This function locates thing like π i ( π j (R)) and replaces
    them with π i (R)'''
    changes = 0

    if n.name == PROJECTION and n.child.name == PROJECTION:
        n.child = n.child.child
        changes += 1

    return changes + recoursive_scan(duplicated_projection, n)


def selection_inside_projection(n):
    '''This function locates things like  σ j (π k(R)) and
    converts them into π k(σ j (R))'''
    changes = 0

    if n.name == SELECTION and n.child.name == PROJECTION:
        changes = 1
        temp = n.prop
        n.prop = n.child.prop
        n.child.prop = temp
        n.name = PROJECTION
        n.child.name = SELECTION

    return changes + recoursive_scan(selection_inside_projection, n)


def swap_union_renames(n):
    '''This function locates things like
    ρ a➡b(R) ᑌ ρ a➡b(Q)
    and replaces them with
    ρ a➡b(R ᑌ Q).
    Does the same with subtraction and intersection'''
    changes = 0

    if n.name in (DIFFERENCE, UNION, INTERSECTION) and n.left.name == n.right.name and n.left.name == RENAME:
        l_vars = {}
        for i in n.left.prop.split(','):
            q = i.split(ARROW)
            l_vars[q[0].strip()] = q[1].strip()

        r_vars = {}
        for i in n.right.prop.split(','):
            q = i.split(ARROW)
            r_vars[q[0].strip()] = q[1].strip()

        if r_vars == l_vars:
            changes = 1

            # Copying self, but child will be child of renames
            q = parser.node()
            q.name = n.name
            q.kind = parser.BINARY
            q.left = n.left.child
            q.right = n.right.child

            n.name = RENAME
            n.kind = parser.UNARY
            n.child = q
            n.prop = n.left.prop
            n.left = n.right = None

    return changes + recoursive_scan(swap_union_renames, n)


def futile_renames(n):
    '''This function purges renames like id->id'''
    changes = 0

    if n.name == RENAME:
        # Located two nested renames.
        changes = 1

        # Creating a dictionary with the attributes
        _vars = {}
        for i in n.prop.split(','):
            q = i.split(ARROW)
            _vars[q[0].strip()] = q[1].strip()
        # Scans dictionary to locate things like "a->b,b->c" and replace them
        # with "a->c"
        for key in list(_vars.keys()):
            value = _vars.get(key)
            if key == value:
                _vars.pop(value)  # Removes the unused one

        if len(_vars) == 0: # Nothing to rename, removing the rename op
            replace_node(n, n.child)
        else:
            n.prop = ','.join('%s%s%s' % (i[0], ARROW, i[1]) for i in _vars.items())

    return changes + recoursive_scan(futile_renames, n)


def subsequent_renames(n):
    '''This function removes redoundant subsequent renames joining them into one'''

    '''Purges renames like id->id Since it's needed to be performed BEFORE this one
    so it is not in the list with the other optimizations'''
    futile_renames(n)
    changes = 0

    if n.name == RENAME and n.child.name == RENAME:
        # Located two nested renames.
        changes = 1
        # Joining the attribute into one
        n.prop += ',' + n.child.prop
        n.child = n.child.child

        # Creating a dictionary with the attributes
        _vars = {}
        for i in n.prop.split(','):
            q = i.split(ARROW)
            _vars[q[0].strip()] = q[1].strip()
        # Scans dictionary to locate things like "a->b,b->c" and replace them
        # with "a->c"
        for key in list(_vars.keys()):
            value = _vars.get(key)
            if value in _vars.keys():
                if _vars[value] != key:
                    # Double rename on attribute
                    _vars[key] = _vars[_vars[key]]  # Sets value
                    _vars.pop(value)  # Removes the unused one
                else:  # Cycle rename a->b,b->a
                    _vars.pop(value)  # Removes the unused one
                    _vars.pop(key)  # Removes the unused one

        if len(_vars) == 0:  # Nothing to rename, removing the rename op
            replace_node(n, n.child)
        else:
            n.prop = ','.join('%s%s%s' % (i[0], ARROW, i[1]) for i in _vars.items())

    return changes + recoursive_scan(subsequent_renames, n)


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


def swap_rename_projection(n):
    '''This function locates things like π k(ρ j(R))
    and replaces them with ρ j(π k(R)).
    This will let rename work on a hopefully smaller set
    and more important, will hopefully allow further optimizations.
    Will also eliminate fields in the rename that are cutted in the projection.
    '''
    changes = 0

    if n.name == PROJECTION and n.child.name == RENAME:
        changes = 1

        # π index,name(ρ id➡index(R))
        _vars = {}
        for i in n.child.prop.split(','):
            q = i.split(ARROW)
            _vars[q[1].strip()] = q[0].strip()

        _pr = n.prop.split(',')
        for i in range(len(_pr)):
            try:
                _pr[i] = _vars[_pr[i].strip()]
            except:
                pass

        _pr_reborn = n.prop.split(',')
        for i in list(_vars.keys()):
            if i not in _pr_reborn:
                _vars.pop(i)
        n.name = n.child.name

        n.prop = ','.join('%s%s%s' % (i[1], ARROW, i[0]) for i in _vars.items())

        n.child.name = PROJECTION
        n.child.prop = ''
        for i in _pr:
            n.child.prop += i + ','
        n.child.prop = n.child.prop[:-1]

    return changes + recoursive_scan(swap_rename_projection, n)


def swap_rename_select(n):
    '''This function locates things like σ k(ρ j(R)) and replaces
    them with ρ j(σ k(R)). Renaming the attributes used in the
    selection, so the operation is still valid.'''
    changes = 0

    if n.name == SELECTION and n.child.name == RENAME:
        changes = 1
        # Dictionary containing attributes of rename
        _vars = {}
        for i in n.child.prop.split(','):
            q = i.split(ARROW)
            _vars[q[1].strip()] = q[0].strip()

        # tokenizes expression in select
        _tokens = tokenize_select(n.prop)

        # Renaming stuff
        for i in range(len(_tokens)):
            splitted = _tokens[i].split('.', 1)
            if splitted[0] in _vars:
                if len(splitted) == 1:
                    _tokens[i] = _vars[_tokens[i].split('.')[0]]
                else:
                    _tokens[i] = _vars[
                        _tokens[i].split('.')[0]] + '.' + splitted[1]

        # Swapping operators
        n.name = RENAME
        n.child.name = SELECTION

        n.prop = n.child.prop
        n.child.prop = ' '.join(_tokens)

    return changes + recoursive_scan(swap_rename_select, n)


def select_union_intersect_subtract(n):
    '''This function locates things like σ i(a) ᑌ σ q(a)
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

        newnode = parser.node()

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


def union_and_product(n):
    '''
    A * B ∪ A * C = A * (B ∪ C)
    Same thing with inner join
    '''

    changes = 0
    if n.name == UNION and n.left.name in {PRODUCT, JOIN} and n.left.name == n.right.name:

        newnode = parser.node()
        newnode.kind = parser.BINARY
        newnode.name = n.left.name

        newchild = parser.node()
        newchild.kind = parser.BINARY
        newchild.name = UNION

        if n.left.left == n.right.left or n.left.left == n.right.right:
            newnode.left = n.left.left
            newnode.right = newchild

            newchild.left = n.left.right
            newchild.right = n.right.left if n.left.left == n.right.right else n.right.right
            replace_node(n, newnode)
            changes = 1
        elif n.left.right == n.right.left or n.left.left == n.right.right:
            newnode.left = n.left.right
            newnode.right = newchild

            newchild.left = n.left.left
            newchild.right = n.right.left if n.right.left == n.right.right else n.right.right
            replace_node(n, newnode)
            changes = 1
    return changes + recoursive_scan(union_and_product, n)


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
    return changes + recoursive_scan(projection_and_union, n, rels)


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
            l_node = parser.node()
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
            r_node = parser.node()
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


def useless_projection(n, rels):
    '''
    Removes projections that are over all the fields
    '''
    changes = 0
    if n.name == PROJECTION and \
            set(n.child.result_format(rels)) == set(i.strip() for i in n.prop.split(',')):
        changes = 1
        replace_node(n, n.child)

    return changes + recoursive_scan(useless_projection, n, rels)

general_optimizations = [
    duplicated_select,
    down_to_unions_subtractions_intersections,
    duplicated_projection,
    selection_inside_projection,
    subsequent_renames,
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

if __name__ == "__main__":
    print (tokenize_select("skill == 'C' and  id % 2 == 0"))
