# Relational
# Copyright (C) 2008-2020  Salvo "LtWorf" Tomaselli
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
# This module provides a classes to represent relations and to perform
# relational operations on them.

import csv
from itertools import chain, repeat, product as iproduct
from collections import deque
from typing import *
from pathlib import Path

from relational.rtypes import *


__all__ = [
    'Relation',
    'Header',
]


class Relation(NamedTuple):
    '''
    This object defines a relation (as a group of consistent tuples) and operations.

    A relation is a particular kind of set, which has a number of named attributes and
    a number of tuples, which must express a value for every attribute.

    Set operations like union, intersection and difference are restricted and can only be
    performed on relations which share the same set of named attributes.

    The constructor optionally accepts a filename and then it will load the relation from
    that file.

    If no parameter is supplied an empty relation is created.

    Files need to be comma separated as described in RFC4180.

    The first line need to contain the attributes of the relation while the
    following lines contain the tuples of the relation.

    An empty relation needs a header, and can be filled using the insert()
    method.
    '''
    header: 'Header'
    content: FrozenSet[Tuple[CastValue, ...]]

    @staticmethod
    def load(filename: Union[str, Path]) -> 'Relation':
        '''
        Load a relation object from a csv file.

        The 1st row is the header and the other rows are the content.
        '''
        with open(filename) as fp:
            reader = csv.reader(fp)  # Creating a csv reader
            header = Header(next(reader))  # read 1st line
            return Relation.create_from(header, reader)

    @staticmethod
    def create_from(header: Iterable[str], content: Iterable[Iterable[str]]) -> 'Relation':
        '''
        Iterator for the header, and iterator for the content.
        '''
        header = Header(header)
        r_content: List[Tuple[CastValue, ...]] = []
        guessed_types = list(repeat({Rdate, float, int, str}, len(header)))

        for row in content:
            if len(row) != len(header):
                raise ValueError(f'Line {row} contains an incorrect amount of values')
            r_content.append(row)

            # Guess types
            for i, value in enumerate(row):
                guessed_types[i] = guessed_types[i].intersection(guess_type(value))

        typed_content = []
        for r in r_content:
            t = tuple(cast(v, guessed_types[i]) for i, v in enumerate(r))
            typed_content.append(t)

        return Relation(header, frozenset(typed_content))


    def __iter__(self):
        return iter(self.content)

    def __contains__(self, key):
        return key in self.content

    def save(self, filename: Union[Path, str]) -> None:
        '''
        Saves the relation in a file. Will save using the csv
        format as defined in RFC4180.
        '''

        with open(filename, 'w') as fp:
            writer = csv.writer(fp)  # Creating csv writer

            # It wants an iterable containing iterables
            head = (self.header,)
            writer.writerows(head)

            # Writing content, already in the correct format
            writer.writerows(self.content)

    def _rearrange(self, other: 'Relation') -> 'Relation':
        '''If two relations share the same attributes in a different order, this method
        will use projection to make them have the same attributes' order.
        It is not exactely related to relational algebra. Just a method used
        internally.
        Will raise an exception if they don't share the same attributes'''
        if not isinstance(other, Relation):
            raise TypeError('Expected an instance of the same class')
        elif self.header == other.header:
            return other
        elif len(self.header) == len(other.header) and self.header.sharedAttributes(other.header) == len(self.header):
            return other.projection(self.header)
        raise TypeError('Relations differ: [%s] [%s]' % (
            ','.join(self.header), ','.join(other.header)
        ))

    def selection(self, expr: str) -> 'Relation':
        '''
        Selection, expr must be a valid Python expression; can contain field names.
        '''
        try:
            c_expr = compile(expr, 'selection', 'eval')
        except:
            raise Exception(f'Failed to compile expression: {expr}')

        content = []
        for i in self.content:
            # Fills the attributes dictionary with the values of the tuple
            attributes = {attr: i[j]
                          for j, attr in enumerate(self.header)
                          }

            try:
                if eval(c_expr, attributes):
                    content.append(i)
            except Exception as e:
                raise Exception(f'Failed to evaluate {expr} with {attributes}\n{e}')
        return Relation(self.header, frozenset(content))

    def product(self, other: 'Relation') -> 'Relation':
        '''
        Cartesian product. Attributes of the relations must differ.
        '''

        if (not isinstance(other, Relation)):
            raise Exception('Operand must be a relation')
        if self.header.sharedAttributes(other.header) != 0:
            raise Exception(
                'Unable to perform product on relations with colliding attributes'
            )
        header = Header(self.header + other.header)

        content = frozenset(i+j for i, j in iproduct(self.content, other.content))
        return Relation(header, content)

    def projection(self, *attributes) -> 'Relation':
        '''
        Can be called in two different ways:
        a.projection('field1','field2')

        or

        a.projection(['field1','field2'])

        The cardinality of the result, might be less than the cardinality
        of the original object.
        '''
        # Parameters are supplied in a list, instead with multiple parameters
        if not isinstance(attributes[0], str):
            attributes = attributes[0]

        ids = self.header.getAttributesId(attributes)

        if len(ids) == 0:
            raise Exception('Invalid attributes for projection')
        header = Header((self.header[i] for i in ids))

        content = frozenset(tuple((i[j] for j in ids)) for i in self.content)

        return Relation(header, content)

    def rename(self, params: Dict[str, str]) -> 'Relation':
        '''
        Takes a dictionary.

        Will replace the field name as the key with its value.

        For example if you want to rename a to b, call
        rel.rename({'a':'b'})
        '''
        header = self.header.rename(params)
        return Relation(header, self.content)

    def intersection(self, other: 'Relation') -> 'Relation':
        '''
        Intersection operation. The result will contain items present in both
        operands.
        Will return an empty one if there are no common items.
        '''
        other = self._rearrange(other)  # Rearranges attributes' order
        return Relation(self.header, self.content.intersection(other.content))

    def difference(self, other: 'Relation') -> 'Relation':
        '''Difference operation. The result will contain items present in first
        operand but not in second one.
        '''
        other = self._rearrange(other)  # Rearranges attributes' order
        return Relation(self.header, self.content.difference(other.content))

    def division(self, other: 'Relation') -> 'Relation':
        '''Division operator
        The division is a binary operation that is written as R ÷ S. The
        result consists of the restrictions of tuples in R to the
        attribute names unique to R, i.e., in the header of R but not in the
        header of S, for which it holds that all their combinations with tuples
        in S are present in R.
        '''

        # d_headers are the headers from self that aren't also headers in other
        d_headers = tuple(set(self.header) - set(other.header))

        # Wikipedia defines the division as follows:

        # a1,....,an are the d_headers

        # T := πa1,...,an(R) × S
        # U := T - R
        # V := πa1,...,an(U)
        # W := πa1,...,an(R) - V

        # W is the result that we want

        t = self.projection(d_headers).product(other)
        return self.projection(d_headers).difference(t.difference(self).projection(d_headers))

    def union(self, other: 'Relation') -> 'Relation':
        '''Union operation. The result will contain items present in first
        and second operands.
        '''
        other = self._rearrange(other)  # Rearranges attributes' order
        return Relation(self.header, self.content.union(other.content))

    def thetajoin(self, other: 'Relation', expr: str) -> 'Relation':
        '''Defined as product and then selection with the given expression.'''
        return self.product(other).selection(expr)

    def outer(self, other: 'Relation') -> 'Relation':
        '''Does a left and a right outer join and returns their union.'''
        a = self.outer_right(other)
        b = self.outer_left(other)

        return a.union(b)

    def outer_right(self, other: 'Relation') -> 'Relation':
        '''
        Outer right join. Considers self as left and param as right. If the
        tuple has no corrispondence, empy attributes are filled with a "---"
        string. This is due to the fact that the None token would cause
        problems when saving and reloading the relation.
        Just like natural join, it works considering shared attributes.
        '''
        return other.outer_left(self)

    def outer_left(self, other: 'Relation', swap=False) -> 'Relation':
        '''
        See documentation for outer_right
        '''

        shared = self.header.intersection(other.header)

        # Creating the header with all the fields, done like that because order is
        # needed
        h = (i for i in other.header if i not in shared)
        header = Header(chain(self.header, h))

        # Shared ids of self
        sid = self.header.getAttributesId(shared)
        # Shared ids of the other relation
        oid = other.header.getAttributesId(shared)

        # Non shared ids of the other relation
        noid = [i for i in range(len(other.header)) if i not in oid]

        content = []
        for i in self.content:
            # Tuple partecipated to the join?
            added = False
            for j in other.content:
                match = True
                for k in range(len(sid)):
                    match = match and (i[sid[k]] == j[oid[k]])

                if match:
                    item = chain(i, (j[l] for l in noid))

                    content.append(tuple(item))
                    added = True
            # If it didn't partecipate, adds it
            if not added:
                item = chain(i, repeat('---', len(noid))) #FIXME
                content.append(tuple(item))

        return Relation(header, frozenset(content))

    def join(self, other: 'Relation') -> 'Relation':
        '''
        Natural join, joins on shared attributes (one or more). If there are no
        shared attributes, it will behave as the cartesian product.
        '''

        # List of attributes in common between the relations
        shared = self.header.intersection(other.header)

        # Creating the header with all the fields, done like that because order is
        # needed
        h = (i for i in other.header if i not in shared)
        header = Header(chain(self.header, h))

        # Shared ids of self
        sid = self.header.getAttributesId(shared)
        # Shared ids of the other relation
        oid = other.header.getAttributesId(shared)

        # Non shared ids of the other relation
        noid = [i for i in range(len(other.header)) if i not in oid]

        content = []
        for i in self.content:
            for j in other.content:
                match = True
                for k in range(len(sid)):
                    match = match and (i[sid[k]] == j[oid[k]])

                if match:
                    item = chain(i, (j[l] for l in noid))
                    content.append(tuple(item))

        return Relation(header, frozenset(content))

    def __eq__(self, other):
        if not isinstance(other, Relation):
            return False

        if len(self.content) != len(other.content):
            return False

        if set(self.header) != set(other.header):
            return False

        # Rearranges attributes' order so can compare tuples directly
        other = self._rearrange(other)

        # comparing content
        return self.content == other.content

    def __len__(self):
        return len(self.content)

    def __str__(self):
        m_len = [len(i) for i in self.header]  # Maximum lenght string

        for f in self.content:
            for col, i in enumerate(f):
                if len(i) > m_len[col]:
                    m_len[col] = len(i)

        res = ""
        for f, attr in enumerate(self.header):
            res += attr.ljust(2 + m_len[f])

        for r in self.content:
            res += "\n"
            for col, i in enumerate(r):
                res += i.ljust(2 + m_len[col])

        return res


class Header(tuple):

    '''This class defines the header of a relation.
    It is used within relations to know if requested operations are accepted'''

    def __new__(cls, fields):
        return super(Header, cls).__new__(cls, tuple(fields))

    def __init__(self, *args, **kwargs):
        '''Accepts a list with attributes' names. Names MUST be unique'''

        for i in self:
            if not is_valid_relation_name(i):
                raise Exception(f'"{i}" is not a valid attribute name')

        if len(self) != len(set(self)):
            raise Exception('Attribute names must be unique')

    def __repr__(self):
        return "Header(%s)" % super(Header, self).__repr__()

    def rename(self, params: Dict[str, str]) -> 'Header':
        '''Returns a new header, with renamed fields.

        params is a dictionary of {old:new} names
        '''
        attrs = list(self)
        for old, new in params.items():
            if not is_valid_relation_name(new):
                raise Exception(f'{new} is not a valid attribute name')
            try:
                id_ = attrs.index(old)
                attrs[id_] = new
            except:
                raise Exception(f'Field not found: {old}')
        return Header(attrs)

    def sharedAttributes(self, other: 'Header') -> int:
        '''Returns how many attributes this header has in common with a given one'''
        return len(set(self).intersection(set(other)))

    def union(self, other: 'Header') -> Set[str]:
        '''Returns the union of the sets of attributes with another header.'''
        return set(self).union(set(other))

    def intersection(self, other: 'Header') -> Set[str]:
        '''Returns the set of common attributes with another header.'''
        return set(self).intersection(set(other))

    def getAttributesId(self, param: Iterable[str]) -> List[int]:
        '''Returns a list with numeric index corresponding to field's name'''
        try:
            return [self.index(i) for i in param]
        except ValueError as e:
            raise Exception('One of the fields is not in the relation: %s' % ','.join(param))
