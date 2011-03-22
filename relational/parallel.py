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
# 
# This module offers capability of executing relational queries in parallel.

import optimizer
import multiprocessing
import parser

def execute(tree,rels):
    '''This funcion executes a query in parallel.
    Tree is the tree describing the query (usually obtained with
    parser.tree(querystring)
    rels is a dictionary containing the relations associated with the names'''

    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=__p_exec__, args=(tree,rels,q,))
    p.start()
    result= q.get()
    p.join()
    return result

def __p_exec__(tree,rels,q):
    '''q is the queue used for communication'''
    if tree.kind==parser.RELATION:
        q.put(rels[tree.name])
    elif tree.kind==parser.UNARY:
        
        #Obtain the relation
        temp_q = multiprocessing.Queue()
        __p_exec__(tree.child,rels,temp_q)
        rel=temp_q.get()
        
        #Execute the query
        result=__p_exec_unary__(tree,rel)
        q.put(result)
    elif tree.kind==parser.BINARY:
        left_q = multiprocessing.Queue()
        left_p = multiprocessing.Process(target=__p_exec__, args=(tree.left,rels,left_q,))
        right_q = multiprocessing.Queue()
        right_p = multiprocessing.Process(target=__p_exec__, args=(tree.right,rels,right_q,))
        
        
        #Spawn the children
        left_p.start()
        right_p.start()
                
        #Get the left and right relations
        left= left_q.get()
        right= right_q.get()
        
        #Wait for the children to terminate
        left_p.join()
        right_p.join()
        
        result = __p_exec_binary__(tree,left,right)
        q.put(result)
    return
def __p_exec_binary__(tree,left,right):
    if tree.name=='*':
        return left.product(right)
    elif tree.name=='-':
        return left.difference(right)
    elif tree.name=='ᑌ':
        return left.union(right)
    elif tree.name=='ᑎ':
        return left.intersection(right)
    elif tree.name=='÷':
        return left.division(right)
    elif tree.name=='ᐅᐊ':
        return left.join(right)
    elif tree.name=='ᐅLEFTᐊ':
        return left.outer_left(right)
    elif tree.name=='ᐅRIGHTᐊ':
        return left.outer_right(right)
    else: # tree.name=='ᐅFULLᐊ':
        return left.outer(right)
    
def __p_exec_unary__(tree,rel):
    if tree.name=='π':#Projection
        tree.prop=tree.prop.replace(' ','').split(',')
        result= rel.projection(tree.prop)
    elif tree.name=="ρ": #Rename
        #tree.prop='{\"%s\"}' % tree.prop.replace(',','\",\"').replace('➡','\":\"').replace(' ','')
        d={}
        tree.prop=tree.prop.replace(' ','')
        for i in tree.prop.split(','):
            rename_=i.split('➡')
            d[rename_[0]]=rename_[1]
        
        result= rel.rename(d)
    else: #Selection
        result= rel.selection(tree.prop)       
    return result
    