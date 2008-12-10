# coding=UTF-8
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

'''This module optimizes relational expressions into ones that require less time to be executed'''

RELATION=0
UNARY=1
BINARY=2

class node (object):
    '''This class is a node of a relational expression. Leaves are relations and internal nodes are operations.'''
    def __init__(self,expression):
        '''expression must be a valid relational algrbra expression that would be accepted by the parser
        and must be utf16'''
        self.kind=0
        self.name="a"
        self.prop=""
        '''*-ᑌᑎᐅᐊᐅLEFTᐊᐅRIGHTᐊᐅFULLᐊπσρ'''
        
        '''(a ᑌ (a ᑌ b ᑌ c ᑌ d)) ᑎ c - σ i==3(πa,b(aᑌ b ᑎ c))'''
        
        for i in list(expression):
            print i
        
        
    def __str__(self):
        if (self.kind==RELATION):
            return self.name
        elif (self.kind==UNARY):
            return self.name + " "+ self.prop+ " (" + self.child +")"
        elif (self.kind==BINARY):
            return "("+ self.left + ") " + self.name + " (" + self.right+ ")"





n=node(u"(a ᑌ b) ᑌ c ᑌ d")
print n