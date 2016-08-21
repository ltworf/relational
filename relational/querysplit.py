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
