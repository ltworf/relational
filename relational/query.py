# -*- coding: utf-8 -*-
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
# This module provides a classes to represent queries

from relational import


class TypeException(Exception):
    pass


class Query(object):

    def __init__(self, query):
        self.query = query
        self.tree = parser.tree(query)
        # TODO self.query_code = parser

        self.optimized = None
        self.optimized_query = None
        self.optimized_code = None
