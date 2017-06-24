# Relational
# Copyright (C) 2008-2017  Salvo "LtWorf" Tomaselli
#
# Relation is free software: you can redistribute it and/or modify
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
# Custom types for relational algebra.
# Purpose of this module is having the isFloat function and
# implementing dates to use in selection.

import datetime
import keyword
import re
from typing import Union

RELATION_NAME_REGEXP = re.compile(r'^[_a-z][_a-z0-9]*$', re.IGNORECASE)


class Rstring(str):

    '''String subclass with some custom methods'''

    int_regexp = re.compile(r'^[\+\-]{0,1}[0-9]+$')
    float_regexp = re.compile(r'^[\+\-]{0,1}[0-9]+(\.([0-9])+)?$')
    date_regexp = re.compile(
        r'^([0-9]{1,4})(\\|-|/)([0-9]{1,2})(\\|-|/)([0-9]{1,2})$'
    )

    def autocast(self) -> Union[int, float, 'Rdate', 'Rstring']:
        '''
        Returns the automatic cast for this
        value.
        '''
        try:
            return self._autocast
        except:
            pass

        self._autocast = self #  type: Union[int, float, 'Rdate', 'Rstring']
        if len(self) > 0:
            if self.isInt():
                self._autocast = int(self)
            elif self.isFloat():
                self._autocast = float(self)
            elif self.isDate():
                self._autocast = rdate(self)
        return self._autocast

    def isInt(self) -> bool:
        '''Returns true if the string represents an int number
        it only considers as int numbers the strings matching
        the following regexp:
        r'^[\+\-]{0,1}[0-9]+$'
        '''
        return Rstring.int_regexp.match(self) is not None

    def isFloat(self) -> bool:
        '''Returns true if the string represents a float number
        it only considers as float numbers, the strings matching
        the following regexp:
            r'^[\+\-]{0,1}[0-9]+(\.([0-9])+)?$'
        '''
        return Rstring.float_regexp.match(self) is not None

    def isDate(self) -> bool:
        '''Returns true if the string represents a date,
        in the format YYYY-MM-DD. as separators '-' , '\', '/' are allowed.
        As side-effect, the date object will be stored for future usage, so
        no more parsings are needed
        '''
        try:
            return self._isdate #  type: ignore
        except:
            pass

        r = Rstring.date_regexp.match(self)
        if r is None:
            self._isdate = False
            self._date = None
            return False

        try:  # Any of the following operations can generate an exception, if it happens, we aren't dealing with a date
            year = int(r.group(1))
            month = int(r.group(3))
            day = int(r.group(5))
            d = datetime.date(year, month, day)
            self._isdate = True
            self._date = d
            return True
        except:
            self._isdate = False
            self._date = None
            return False

    def getDate(self):
        '''Returns the datetime.date object or None'''
        try:
            return self._date
        except:
            self.isDate()
            return self._date


class Rdate (object):

    '''Represents a date'''

    def __init__(self, date):
        '''date: A string representing a date'''
        if not isinstance(date, rstring):
            date = rstring(date)

        self.intdate = date.getDate()
        self.day = self.intdate.day
        self.month = self.intdate.month
        self.weekday = self.intdate.weekday()
        self.year = self.intdate.year

    def __hash__(self):
        return self.intdate.__hash__()

    def __str__(self):
        return self.intdate.__str__()

    def __add__(self, days):
        res = self.intdate + datetime.timedelta(days)
        return rdate(res.__str__())

    def __eq__(self, other):
        return self.intdate == other.intdate

    def __ge__(self, other):
        return self.intdate >= other.intdate

    def __gt__(self, other):
        return self.intdate > other.intdate

    def __le__(self, other):
        return self.intdate <= other.intdate

    def __lt__(self, other):
        return self.intdate < other.intdate

    def __ne__(self, other):
        return self.intdate != other.intdate

    def __sub__(self, other):
        return (self.intdate - other.intdate).days


def is_valid_relation_name(name: str) -> bool:
    '''Checks if a name is valid for a relation.
    Returns boolean'''
    return re.match(RELATION_NAME_REGEXP, name) != None and not keyword.iskeyword(name)


# Backwards compatibility
rdate = Rdate
rstring = Rstring
