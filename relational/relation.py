# Relational
# Copyright (C) 2008  Salvo "LtWorf" Tomaselli
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
from itertools import chain, repeat
from collections import deque

from relational.rtypes import *


class relation (object):

    '''This objects defines a relation (as a group of consistent tuples) and operations
    A relation can be represented using a table
    Calling an operation and providing a non relation parameter when it is expected will
    result in a None value'''
    __hash__ = None

    def __init__(self, filename=""):
        '''Creates a relation, accepts a filename and then it will load the relation from
        that file. If no parameter is supplied an empty relation is created. Empty
        relations are used in internal operations.
        By default the file will be handled like a comma separated as described in
        RFC4180.'''

        self._readonly = False

        if len(filename) == 0:  # Empty relation
            self.content = set()
            self.header = header([])
            return
        with open(filename) as fp:
            reader = csv.reader(fp)  # Creating a csv reader
            self.header = header(next(reader))  # read 1st line
            self.content = set()
            attributes = len(self.header)

            iterator = ((self.insert(i) for i in reader))
            deque(iterator, maxlen=0)

    def _make_writable(self):
        '''If this relation is marked as readonly, this
        method will copy the content to make it writable too'''

        if self._readonly:
            self.content = set(self.content)
            self._readonly = False

    def __iter__(self):
        return iter(self.content)

    def __contains__(self, key):
        return key in self.content

    def save(self, filename):
        '''Saves the relation in a file. By default will save using the csv
        format as defined in RFC4180, but setting comma_separated to False,
        it will use the old format with space separated values.
        '''

        fp = open(filename, 'w')  # Opening file in write mode

        writer = csv.writer(fp)  # Creating csv writer

        # It wants an iterable containing iterables
        head = (self.header,)
        writer.writerows(head)

        # Writing content, already in the correct format
        writer.writerows(self.content)
        fp.close()  # Closing file

    def _rearrange(self, other):
        '''If two relations share the same attributes in a different order, this method
        will use projection to make them have the same attributes' order.
        It is not exactely related to relational algebra. Just a method used
        internally.
        Will raise an exception if they don't share the same attributes'''
        if not isinstance(other, relation):
            raise Exception('Expected an instance of the same class')
        elif self.header == other.header:
            return other
        elif self.header.sharedAttributes(other.header) == len(self.header):
            return other.projection(self.header)
        raise Exception('Relations differ: [%s] [%s]' % (
            ','.join(self.header), ','.join(other.header)
        ))

    def selection(self, expr):
        '''Selection, expr must be a valid boolean expression, can contain field names,
        constant, math operations and boolean ones.'''
        newt = relation()
        newt.header = header(self.header)
        for i in self.content:
            # Fills the attributes dictionary with the values of the tuple
            attributes = {attr: i[j].autocast()
                          for j, attr in enumerate(self.header)
                          }

            try:
                if eval(expr, attributes):
                    newt.content.add(i)
            except Exception as e:
                raise Exception(
                    "Failed to evaluate %s\n%s" % (expr, e.__str__()))
        return newt

    def product(self, other):
        '''Cartesian product, attributes must be different to avoid collisions
        Doing this operation on relations with colliding attributes will
        cause an exception.
        It is possible to use rename on attributes and then use the product'''

        if (not isinstance(other, relation)):
            raise Exception('Operand must be a relation')
        if self.header.sharedAttributes(other.header) != 0:
            raise Exception(
                'Unable to perform product on relations with colliding attributes'
            )
        newt = relation()
        newt.header = header(self.header + other.header)

        for i in self.content:
            for j in other.content:
                newt.content.add(i + j)
        return newt

    def projection(self, * attributes):
        '''Projection operator, takes many parameters, for each field to use.
        Can also use a single parameter with a list.
        Will delete duplicate items
        If an empty list or no parameters are provided, returns None'''
        # Parameters are supplied in a list, instead with multiple parameters
        if not isinstance(attributes[0], str):
            attributes = attributes[0]

        ids = self.header.getAttributesId(attributes)

        if len(ids) == 0:
            raise Exception('Invalid attributes for projection')
        newt = relation()
        # Create the header
        h = (self.header[i] for i in ids)
        newt.header = header(h)

        # Create the body
        for i in self.content:
            row = (i[j] for j in ids)
            newt.content.add(tuple(row))
        return newt

    def rename(self, params):
        '''Operation rename. Takes a dictionary
        Will replace the itmem with its content.
        For example if you want to rename a to b, provide {"a":"b"}
        '''
        result = []

        newt = relation()
        newt.header = self.header.rename(params)

        newt.content = self.content
        newt._readonly = True
        self._readonly = True
        return newt

    def intersection(self, other):
        '''Intersection operation. The result will contain items present in both
        operands.
        Will return an empty one if there are no common items.
        Will return None if headers are different.
        It is possible to use projection and rename to make headers match.'''
        other = self._rearrange(other)  # Rearranges attributes' order
        newt = relation()
        newt.header = header(self.header)

        newt.content = self.content.intersection(other.content)
        return newt

    def difference(self, other):
        '''Difference operation. The result will contain items present in first
        operand but not in second one.
        Will return an empty one if the second is a superset of first.
        Will return None if headers are different.
        It is possible to use projection and rename to make headers match.'''
        other = self._rearrange(other)  # Rearranges attributes' order
        newt = relation()
        newt.header = header(self.header)

        newt.content = self.content.difference(other.content)
        return newt

    def division(self, other):
        '''Division operator
        The division is a binary operation that is written as R ÷ S. The
        result consists of the restrictions of tuples in R to the
        attribute names unique to R, i.e., in the header of R but not in the
        header of S, for which it holds that all their combinations with tuples
        in S are present in R.
        '''

        # d_headers are the headers from self that aren't also headers in other
        d_headers = tuple(set(self.header) - set(other.header))

        '''
        Wikipedia defines the division as follows:

        a1,....,an are the d_headers

        T := πa1,...,an(R) × S
        U := T - R
        V := πa1,...,an(U)
        W := πa1,...,an(R) - V

        W is the result that we want
        '''

        t = self.projection(d_headers).product(other)
        return self.projection(d_headers).difference(t.difference(self).projection(d_headers))

    def union(self, other):
        '''Union operation. The result will contain items present in first
        and second operands.
        Will return an empty one if both are empty.
        Will not insert tuplicated items.
        Will return None if headers are different.
        It is possible to use projection and rename to make headers match.'''
        other = self._rearrange(other)  # Rearranges attributes' order
        newt = relation()
        newt.header = header(self.header)

        newt.content = self.content.union(other.content)
        return newt

    def thetajoin(self, other, expr):
        '''Defined as product and then selection with the given expression.'''
        return self.product(other).selection(expr)

    def outer(self, other):
        '''Does a left and a right outer join and returns their union.'''
        a = self.outer_right(other)
        b = self.outer_left(other)

        return a.union(b)

    def outer_right(self, other):
        '''Outer right join. Considers self as left and param as right. If the
        tuple has no corrispondence, empy attributes are filled with a "---"
        string. This is due to the fact that empty string or a space would cause
        problems when saving the relation.
        Just like natural join, it works considering shared attributes.'''
        return other.outer_left(self)

    def outer_left(self, other, swap=False):
        '''Outer left join. Considers self as left and param as right. If the
        tuple has no corrispondence, empty attributes are filled with a "---"
        string. This is due to the fact that empty string or a space would cause
        problems when saving the relation.
        Just like natural join, it works considering shared attributes.'''

        shared = self.header.intersection(other.header)

        newt = relation()  # Creates the new relation
        # Creating the header with all the fields, done like that because order is
        # needed
        h = (i for i in other.header if i not in shared)
        newt.header = header(chain(self.header, h))

        # Shared ids of self
        sid = self.header.getAttributesId(shared)
        # Shared ids of the other relation
        oid = other.header.getAttributesId(shared)

        # Non shared ids of the other relation
        noid = [i for i in range(len(other.header)) if i not in oid]

        for i in self.content:
            # Tuple partecipated to the join?
            added = False
            for j in other.content:
                match = True
                for k in range(len(sid)):
                    match = match and (i[sid[k]] == j[oid[k]])

                if match:
                    item = chain(i, (j[l] for l in noid))

                    newt.content.add(tuple(item))
                    added = True
            # If it didn't partecipate, adds it
            if not added:
                item = chain(i, repeat('---', len(noid)))
                newt.content.add(tuple(item))

        return newt

    def join(self, other):
        '''Natural join, joins on shared attributes (one or more). If there are no
        shared attributes, it will behave as cartesian product.'''

        # List of attributes in common between the relations
        shared = self.header.intersection(other.header)

        newt = relation()  # Creates the new relation

        # Creating the header with all the fields, done like that because order is
        # needed
        h = (i for i in other.header if i not in shared)
        newt.header = header(chain(self.header, h))

        # Shared ids of self
        sid = self.header.getAttributesId(shared)
        # Shared ids of the other relation
        oid = other.header.getAttributesId(shared)

        # Non shared ids of the other relation
        noid = [i for i in range(len(other.header)) if i not in oid]

        for i in self.content:
            for j in other.content:
                match = True
                for k in range(len(sid)):
                    match = match and (i[sid[k]] == j[oid[k]])

                if match:
                    item = chain(i, (j[l] for l in noid))
                    newt.content.add(tuple(item))

        return newt

    def __eq__(self, other):
        '''Returns true if the relations are the same, ignoring order of items.
        This operation is rather heavy, since it requires sorting and comparing.'''
        if not isinstance(other, relation):
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
        '''Returns a string representation of the relation, can be printed with
        monospaced fonts'''
        m_len = []  # Maximum lenght string
        for f in self.header:
            m_len.append(len(f))

        for f in self.content:
            col = 0
            for i in f:
                if len(i) > m_len[col]:
                    m_len[col] = len(i)
                col += 1

        res = ""
        for f, attr in enumerate(self.header):
            res += "%s" % (attr.ljust(2 + m_len[f]))

        for r in self.content:
            col = 0
            res += "\n"
            for i in r:
                res += "%s" % (i.ljust(2 + m_len[col]))
                col += 1

        return res

    def update(self, expr, dic):
        '''Update, expr must be a valid boolean expression, can contain field names,
        constant, math operations and boolean ones.
        This operation will change the relation itself instead of generating a new one,
        updating all the tuples that make expr true.
        Dic must be a dictionary that has the form field name:value. Every kind of value
        will be converted into a string.
        Returns the number of affected rows.'''
        self._make_writable()
        affected = 0
        attributes = {}
        keys = dic.keys()  # List of headers to modify
        f_ids = self.header.getAttributesId(keys)

        # new_content=[] #New content of the relation
        for i in self.content:
            for j, attr in enumerate(self.header):
                attributes[attr] = i[j].autocast()

            if eval(expr, attributes):  # If expr is true, changing the tuple
                affected += 1
                new_tuple = list(i)
                # Deleting the tuple, instead of changing it, so other
                # relations can still point to the same list without
                # being affected.
                self.content.remove(i)
                for k in range(len(keys)):
                    new_tuple[f_ids[k]] = rstring(dic[keys[k]])
                self.content.add(tuple(new_tuple))
        return affected

    def insert(self, values):
        '''Inserts a tuple in the relation.
        This function will not insert duplicate tuples.
        All the values will be converted in string.
        Will return the number of inserted rows.'''

        if len(self.header) != len(values):
            raise Exception(
                'Tuple has the wrong size. Expected %d, got %d' % (
                    len(self.header),
                    len(values)
                )
            )

        self._make_writable()

        prevlen = len(self.content)
        self.content.add(tuple(map(rstring, values)))
        return len(self.content) - prevlen

    def delete(self, expr):
        '''Delete, expr must be a valid boolean expression, can contain field names,
        constant, math operations and boolean ones.
        This operation will change the relation itself instead of generating a new one,
        deleting all the tuples that make expr true.
        Returns the number of affected rows.'''

        # Not necessary self._make_writable()

        l = len(self.content)
        self._readonly = False
        self.content = self.difference(self.selection(expr)).content
        return len(self.content) - l


class header(tuple):

    '''This class defines the header of a relation.
    It is used within relations to know if requested operations are accepted'''

    # Since relations are mutalbe we explicitly block hashing them
    def __new__(cls, fields):
        return super(header, cls).__new__(cls, tuple(fields))

    def __init__(self, *args, **kwargs):
        '''Accepts a list with attributes' names. Names MUST be unique'''

        for i in self:
            if not is_valid_relation_name(i):
                raise Exception('"%s" is not a valid attribute name' % i)

        if len(self) != len(set(self)):
            raise Exception('Attribute names must be unique')

    def __repr__(self):
        return "header(%s)" % super(header, self).__repr__()

    def rename(self, params):
        '''Returns a new header, with renamed fields.

        params is a dictionary of {old:new} names
        '''
        attrs = list(self)
        for old, new in params.items():
            if not is_valid_relation_name(new):
                raise Exception('%s is not a valid attribute name' % new)
            try:
                id_ = attrs.index(old)
                attrs[id_] = new
            except:
                raise Exception('Field not found: %s' % old)
        return header(attrs)

    def sharedAttributes(self, other):
        '''Returns how many attributes this header has in common with a given one'''
        return len(set(self).intersection(set(other)))

    def union(self, other):
        '''Returns the union of the sets of attributes with another header.'''
        return set(self).union(set(other))

    def intersection(self, other):
        '''Returns the set of common attributes with another header.'''
        return set(self).intersection(set(other))

    def getAttributesId(self, param):
        '''Returns a list with numeric index corresponding to field's name'''
        return [self.index(i) for i in param]
