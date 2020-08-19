# Relational
# Copyright (C) 2008-2020  Salvo "LtWorf" Tomaselli
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
from typing import Union, Set, Any, Callable


RELATION_NAME_REGEXP = re.compile(r'^[_a-z][_a-z0-9]*$', re.IGNORECASE)
_date_regexp = re.compile(
        r'^([0-9]{1,4})(\\|-|/)([0-9]{1,2})(\\|-|/)([0-9]{1,2})$'
    )
CastValue = Union[str, int, float, 'Rdate']


def guess_type(value: str) -> Set[Callable[[Any], Any]]:
    r: Set[Callable[[Any], Any]] = {str}
    if _date_regexp.match(value) is not None:
        r.add(Rdate)

    try:
        int(value)
        r.add(int)
    except ValueError:
        pass

    try:
        float(value)
        r.add(float)
    except ValueError:
        pass
    return r


def cast(value: str, guesses: Set) -> CastValue:
    if int in guesses:
        return int(value)
    if Rdate in guesses:
        return Rdate(value)
    if float in guesses:
        return float(value)
    return value


class Rdate:
    '''Represents a date'''

    def __init__(self, date):
        '''date: A string representing a date'''
        r = _date_regexp.match(date)
        if not r:
            raise ValueError(f'{date} is not a valid date')

        year = int(r.group(1))
        month = int(r.group(3))
        day = int(r.group(5))
        d = datetime.date(year, month, day)

        self.intdate = d
        self.day = d.day
        self.month = d.month
        self.weekday = d.weekday()
        self.year = d.year

    def __hash__(self):
        return self.intdate.__hash__()

    def __str__(self):
        return self.intdate.__str__()

    def __eq__(self, other):
        if not isinstance(other, Rdate):
            return False
        return self.intdate == other.intdate

    def __ge__(self, other):
        return self.intdate >= other.intdate

    def __gt__(self, other):
        return self.intdate > other.intdate

    def __le__(self, other):
        return self.intdate <= other.intdate

    def __lt__(self, other):
        return self.intdate < other.intdate


def is_valid_relation_name(name: str) -> bool:
    '''Checks if a name is valid for a relation.
    Returns boolean'''
    return re.match(RELATION_NAME_REGEXP, name) != None and not keyword.iskeyword(name)
