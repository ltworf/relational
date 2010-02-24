# -*- coding: utf-8 -*-
# coding=UTF-8
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

'''This module optimizes relational expressions into ones that require less time to be executed
For now it is highly experimental, and it shouldn't be used in 3rd party applications.'''

import optimizations
import parser


#Stuff that was here before, keeping it for compatibility
RELATION=parser.RELATION
UNARY=parser.UNARY
BINARY=parser.BINARY
b_operators=parser.b_operators
u_operators=parser.u_operators
op_functions=parser.op_functions
node=parser.node
tokenize=parser.tokenize
tree=parser.tree
#End of the stuff

def optimize_all(expression,rels):
    '''This function performs all the available optimizations'''
    n=tree(expression) #Gets the tree
    total=1
    while total!=0:
        total=0
        for i in optimizations.specific_optimizations:
            total+=i(n,rels) #Performs the optimization
        for i in optimizations.general_optimizations:
            total+=i(n) #Performs the optimization
    return n.__str__()
            

def specific_optimize(expression,rels):
    '''This function performs specific optimizations. Means that it will need to
    know the fields used by the relations'''
    n=tree(expression) #Gets the tree
    total=1
    while total!=0:
        total=0
        for i in optimizations.specific_optimizations:
            total+=i(n,rels) #Performs the optimization
    return n.__str__()
            
def general_optimize(expression):
    '''This function performs general optimizations. Means that it will not need to
    know the fields used by the relations'''
    n=tree(expression) #Gets the tree
    total=1
    while total!=0:
        total=0
        for i in optimizations.general_optimizations:
            total+=i(n) #Performs the optimization
    return n.__str__()

if __name__=="__main__":
    #n=node(u"((a ᑌ b) - c ᑌ d) - b")
    #n=node(u"π a,b (d-a*b)")
    
    #print n.__str__()
    #a= tokenize("(a - (a ᑌ b) * π a,b (a-b)) - ρ 123 (a)")
    #a= tokenize(u"π a,b (a*b)")
    #a=tokenize("(a-b*c)*(b-c)")
    
    import relation,optimizations
    
    '''rels={}
    rels["P1"]= relation.relation("/home/salvo/dev/relational/trunk/samples/people.csv")
    rels["P2"]= relation.relation("/home/salvo/dev/relational/trunk/samples/people.csv")
    rels["R1"]= relation.relation("/home/salvo/dev/relational/trunk/samples/person_room.csv")
    rels["R2"]= relation.relation("/home/salvo/dev/relational/trunk/samples/person_room.csv")
    rels["D1"]= relation.relation("/home/salvo/dev/relational/trunk/samples/dates.csv")
    rels["S1"]= relation.relation("/home/salvo/dev/relational/trunk/samples/skillo.csv")
    print rels'''
    n=tree("π indice,qq,name (ρ age➡qq,id➡indice (P1-P2))")
    #n=tree("σ id==3 and indice==2 and name==5 or name<2(P1 * S1)")
    print n
    print n.toPython()
    
    #print optimizations.selection_and_product(n,rels)
    
    '''
    σ skill=='C' (π id,name,chief,age (σ chief==i and age>a (ρ id➡i,age➡a(π id,age(people))*people)) ᐅᐊ skills)
    (π id,name,chief,age (σ chief == i  and age > a  ((ρ age➡a,id➡i (π id,age (people)))*people)))ᐅᐊ(σ skill == 'C'  (skills))    
    '''
    
    #print specific_optimize("σ name==skill and age>21 and id==indice and skill=='C'(P1ᐅᐊS1)",rels)
    
    #print n
    #print n.result_format(rels)
    '''σ k (r) ᑌ r with r
    σ k (r) ᑎ r with σ k (r)'''
    
    #a=general_optimize('π indice,qq,name (ρ age➡qq,id➡indice (P1-P2))')
    #a=general_optimize("σ i==2 (σ b>5 (d))")
    #print a
    #print node(a)
    #print tokenize("(a)")