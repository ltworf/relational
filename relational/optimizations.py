# -*- coding: utf-8 -*-
# Relational
# Copyright (C) 2009  Salvo "LtWorf" Tomaselli
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

'''This module contains functions to perform various optimizations on the expression trees.
The list general_optimizations contains pointers to general functions, so they can be called
within a cycle.'''

import optimizer

def duplicated_select(n):
    changes=0
    '''This function locates and deletes things like
    σ a ( σ a(C)) and the ones like σ a ( σ b(C))'''
    if n.name=='σ' and n.child.name=='σ':        
        if n.prop != n.child.prop: #Nested but different, joining them
            n.prop = n.prop + " and " + n.child.prop
        n.child=n.child.child
        changes=1
        changes+=duplicated_select(n)
        

    #recoursive scan
    if n.kind==optimizer.UNARY:
        changes+=duplicated_select(n.child)
    elif n.kind==optimizer.BINARY:
        changes+=duplicated_select(n.right)
        changes+=duplicated_select(n.left)
    return changes

def down_to_unions_subtractions_intersections(n):
    '''This funcion locates things like σ i==2 (c ᑌ d), where the union
    can be a subtraction and an intersection and replaces them with
    σ i==2 (c) ᑌ σ i==2(d).
    
    If the operator is not Union and the right expression is a relation, 
    the resulting expression will be: σ i==2 (c) - d.
    
    '''
    changes=0
    _o=('ᑌ','-','ᑎ')
    if n.name=='σ' and n.child.name in _o:
        
        left=optimizer.node()
        left.prop=n.prop
        left.name=n.name
        left.child=n.child.left
        left.kind=optimizer.UNARY
        if n.child.name=='ᑌ' or n.child.right.kind!=optimizer.RELATION:
            right=optimizer.node()
            right.prop=n.prop
            right.name=n.name
            right.child=n.child.right
            right.kind=optimizer.UNARY
        else:
            right=n.child.right
        
        n.name=n.child.name
        n.left=left
        n.right=right
        n.child=None
        n.prop=None
        n.kind=optimizer.BINARY
        changes+=1
    
    #recoursive scan
    if n.kind==optimizer.UNARY:
        changes+=down_to_unions_subtractions_intersections(n.child)
    elif n.kind==optimizer.BINARY:
        changes+=down_to_unions_subtractions_intersections(n.right)
        changes+=down_to_unions_subtractions_intersections(n.left)
    return changes
    

general_optimizations=[duplicated_select,down_to_unions_subtractions_intersections]
