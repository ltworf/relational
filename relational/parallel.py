# -*- coding: utf-8 -*-
# Relational
# Copyright (C) 2009  Salvo "LtWorf" Tomaselli
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

'''This module offers capability of executing relational queries in parallel.'''

import optimizer

def weight (n,rels):
    '''This function returns a weight that tries to give an approssimation of the
    time that will be required to execute the expression'''
    if n.kind==optimizer.RELATION: #Weight of a relation is its size
        r=rels[n.name]
        return len(r.content) * len(r.header.attributes)
    elif n.kind==optimizer.BINARY and n.name=='ρ':
        pass
    elif n.kind==optimizer.BINARY and n.name=='σ':
        pass
    elif n.kind==optimizer.BINARY and n.name=='π':
        pass
    
        
    pass