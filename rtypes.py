# Relational
# Copyright (C) 2008  Salvo "LtWorf" Tomaselli
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

'''Custom types for relational algebra'''
class rstring (str):
	'''String subclass with some custom methods'''
	def isFloat(self):
		'''True if the string is a float number, false otherwise'''
		lst=['0','1','2','3','4','5','6','7','8','9','.']
		for i in self:
			if i not in lst:
				return False;
		return True;