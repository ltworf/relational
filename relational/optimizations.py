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
within a cycle.

It is possible to add new general optimizations by adding the function in the list
general_optimizations present in this module. And the optimization will be executed with the
other ones when optimizing.

A function will have one parameter, which is the root node of the tree describing the expression.
The class used is defined in optimizer module.
A function will have to return the number of changes performed on the tree.
'''

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
    '''
    changes=0
    _o=('ᑌ','-','ᑎ')
    if n.name=='σ' and n.child.name in _o:
        
        left=optimizer.node()
        left.prop=n.prop
        left.name=n.name
        left.child=n.child.left
        left.kind=optimizer.UNARY
        right=optimizer.node()
        right.prop=n.prop
        right.name=n.name
        right.child=n.child.right
        right.kind=optimizer.UNARY
        
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

def duplicated_projection(n):
    '''This function locates thing like π i ( π j (R)) and replaces
    them with π i (R)'''
    changes=0
    
    
    if n.name=='π' and n.child.name=='π':
        n.child=n.child.child
        changes+=1
    
    #recoursive scan
    if n.kind==optimizer.UNARY:
        changes+=duplicated_projection(n.child)
    elif n.kind==optimizer.BINARY:
        changes+=duplicated_projection(n.right)
        changes+=duplicated_projection(n.left)
    return changes

def selection_inside_projection(n):
    '''This function locates things like  σ j (π k(R)) and
    converts them into π k(σ j (R))'''    
    changes=0
    
    if n.name=='σ' and n.child.name=='π':
        changes=1
        temp=n.prop
        n.prop=n.child.prop
        n.child.prop=temp
        n.name='π'
        n.child.name='σ'
    
    #recoursive scan
    if n.kind==optimizer.UNARY:
        changes+=selection_inside_projection(n.child)
    elif n.kind==optimizer.BINARY:
        changes+=selection_inside_projection(n.right)
        changes+=selection_inside_projection(n.left)
    return changes

def subsequent_renames(n):
    '''This function removes redoundant subsequent renames'''
    changes=0
    
    if n.name=='ρ' and n.child.name==n.name:
        #Located two nested renames.
        changes=1
        
        #Joining the attribute into one
        n.prop+=','+n.child.prop
        n.child=n.child.child

        #Creating a dictionary with the attributes
        _vars={}
        for i in n.prop.split(','):
            q=i.split('➡')
            _vars[q[0].strip()]=q[1].strip()

        #Scans dictionary to locate things like "a->b,b->c" and replace them with "a->c"
        for i in list(_vars.keys()):
            if _vars[i] in _vars.keys():
                #Double rename on attribute
                _vars[i] =  _vars[_vars[i]] #Sets value
                _vars.pop(i) #Removes the unused one
        
        #Reset prop var
        n.prop=""
        
        #Generates new prop var
        for i in _vars.items():
            n.prop+="%s➡%s," % (i[0],i[1])
        n.prop=n.prop[:-1] #Removing ending comma     

    #recoursive scan
    if n.kind==optimizer.UNARY:        
        changes+=subsequent_renames(n.child)
    elif n.kind==optimizer.BINARY:
        changes+=subsequent_renames(n.right)
        changes+=subsequent_renames(n.left)
    return changes

def tokenize_select(expression):
    '''This function returns the list of tokens present in a
    selection. The expression can't contain parenthesis.'''
    op=('//=','**=','and','not','//','**','<<','>>','==','!=','>=','<=','+=','-=','*=','/=','%=','or','+','-','*','/','&','|','^','~','<','>','%','=')
    tokens=[]
    temp=''
    
    while len(expression)!=0:
        expression=expression.strip()
        if expression[0:3] in op:#3char op
            tokens.append(temp)
            temp=''
            tokens.append(expression[0:3])
            expression=expression[3:]
        elif expression[0:2] in op:#2char op
            tokens.append(temp)
            temp=''
            tokens.append(expression[0:2])
            expression=expression[2:]
        elif expression[0:1] in op:#1char op
            tokens.append(temp)
            temp=''
            tokens.append(expression[0:1])
            expression=expression[1:]
        elif expression[0:1]=="'":#String
            end=expression.index("'",1)
            while expression[end-1]=='\\':
                end=expression.index("'",end+1)
            
            #Add string to list
            tokens.append(expression[0:end+1])
            expression=expression[end+1:]
        else:
            temp+=expression[0:1]
            expression=expression[1:]
            pass
    if len(temp)!=0:
        tokens.append(temp)
    return tokens

def swap_rename_select(n):
    '''This function locates things like σ k(ρ j(R)) and replaces
    them with ρ j(σ k(R)). Renaming the attributes used in the
    selection, so the operation is still valid.'''
    changes=0
    
    if n.name=='σ' and n.child.name=='ρ':
        changes=1
        #Dictionary containing attributes of rename
        _vars={}
        for i in n.child.prop.split(','):
            q=i.split('➡')
            _vars[q[1].strip()]=q[0].strip()
        
        #tokenizes expression in select
        _tokens=tokenize_select(n.prop)
        
        #Renaming stuff
        for i in range(len(_tokens)):
            splitted=_tokens[i].split('.',1)
            if splitted[0] in _vars:
                if len(splitted)==1:
                    _tokens[i]=_vars[_tokens[i].split('.')[0]]
                else:
                    _tokens[i]=_vars[_tokens[i].split('.')[0]]+'.'+splitted[1]
        
        #Swapping operators
        n.name='ρ'
        n.child.name='σ'
        
        n.prop=n.child.prop
        n.child.prop=''
        for i in _tokens:
            n.child.prop+=i+ ' '
        
    #recoursive scan
    if n.kind==optimizer.UNARY:        
        changes+=swap_rename_select(n.child)
    elif n.kind==optimizer.BINARY:
        changes+=swap_rename_select(n.right)
        changes+=swap_rename_select(n.left)
    return changes

def selection_and_product(n,rels):
    '''This function locates things like σ k (R*Q) and converts them into
    σ l (σ j (R) * σ i (Q)). Where j contains only attributes belonging to R,
    i contains attributes belonging to Q and l contains attributes belonging to both'''
    changes=0
    
    if n.name=='σ' and n.child.name in ('*','ᐅᐊ','ᐅLEFTᐊ','ᐅRIGHTᐊ','ᐅFULLᐊ'):
        l_attr=n.child.left.result_format(rels)
        r_attr=n.child.right.result_format(rels)
        
        tokens=tokenize_select(n.prop)
        
        groups=[]
        temp=[]
        
        for i in tokens:
            if i=='and':
                groups.append(temp)
                temp=[]
            else:
                temp.append(i)
        if len(temp)!=0:
            groups.append(temp)
            temp=[]
        
        left=[]
        right=[]
        both=[]
        
        for i in groups:
            l_fields=False #has fields in left?
            r_fields=False #has fields in left?
            
            for j in i:
                j=j.split('.')[0]
                if j in l_attr:#Field in left
                    l_fields=True
                if j in r_attr:#Field in right
                    r_fields=True
            
            if l_fields and r_fields:#Fields in both
                both.append(i)
            elif l_fields:
                left.append(i)
            elif r_fields:
                right.append(i)
            else:#Unknown.. adding in both
                both.append(i)
        
        #Preparing left selection
        if len(left)>0:
            changes=1
            l_node=optimizer.node()
            l_node.name='σ'
            l_node.kind=optimizer.UNARY
            l_node.child=n.child.left
            l_node.prop=''
            n.child.left=l_node
            while len(left)>0:
                c=left.pop(0)
                for i in c:
                    l_node.prop+=i+ ' '
                if len(left)>0:
                    l_node.prop+=' and '
        
        #Preparing right selection
        if len(right)>0:
            changes=1
            r_node=optimizer.node()
            r_node.name='σ'
            r_node.prop=''
            r_node.kind=optimizer.UNARY
            r_node.child=n.child.right
            n.child.right=r_node
            while len(right)>0:
                c=right.pop(0)
                for i in c:
                    r_node.prop+=i+ ' '
                if len(right)>0:
                    r_node.prop+=' and '
                    
        #Changing main selection
        n.prop=''
        if len(both)!=0:
            while len(both)>0:
                c=both.pop(0)
                for i in c:
                    n.prop+=i+ ' '
                if len(both)>0:
                    n.prop+=' and '                    
        else:#No need for general select
            n.name=n.child.name
            n.kind=n.child.kind
            n.left=n.child.left
            n.right=n.child.right
            
    #recoursive scan
    if n.kind==optimizer.UNARY:        
        changes+=selection_and_product(n.child,rels)
    elif n.kind==optimizer.BINARY:
        changes+=selection_and_product(n.right,rels)
        changes+=selection_and_product(n.left,rels)
    return changes
        
general_optimizations=[duplicated_select,down_to_unions_subtractions_intersections,duplicated_projection,selection_inside_projection,subsequent_renames,swap_rename_select]
specific_optimizations=[selection_and_product]