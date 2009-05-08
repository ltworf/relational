# -*- coding: utf-8 -*-
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

'''This module optimizes relational expressions into ones that require less time to be executed
For now it is highly experimental, and it shouldn't be used in 3rd party applications.'''

import optimizations

RELATION=0
UNARY=1
BINARY=2
b_operators=('*','-','ᑌ','ᑎ','ᐅᐊ','ᐅLEFTᐊ','ᐅRIGHTᐊ','ᐅFULLᐊ')
u_operators=('π','σ','ρ')


class node (object):
    '''This class is a node of a relational expression. Leaves are relations and internal nodes are operations.'''
    kind=None
    
    def __init__(self,expression=None):
        if expression==None or len(expression)==0:
            return
        '''Generates the tree from the tokenized expression'''
        while len(expression)==1 and isinstance(expression[0],list): #We have a list, removing
                expression=expression[0]
        
        if len(expression)==1 and isinstance(expression[0],str): #We have a string (relation name)
            self.kind=RELATION
            self.name=expression[0]
            return
        for i in range(len(expression)-1,-1,-1): #Expression from right to left
            if expression[i] in b_operators: #Binary operator              
                self.kind=BINARY
                self.name=expression[i]
                self.left=node(expression[:i]) 
                self.right=node(expression[i+1:])
                return
        for i in range(len(expression)-1,-1,-1): #Expression from right to left
            if expression[i] in u_operators: #Unary operator
                self.kind=UNARY
                self.name=expression[i]
                self.prop=expression[1+i].strip()
                self.child=node(expression[2+i])
                
                return       
        pass
    def __eq__(self,other):
        if not (isinstance(other,node) and self.name==other.name and self.kind==other.kind):
            return False
        
        if self.kind==UNARY:
            if other.prop!=self.prop:
                return False
            return self.child==other.child
        if self.kind==BINARY:
            return self.left==other.left and self.right==other.right
        return True
    def __str__(self):
        if (self.kind==RELATION):
            return self.name
        elif (self.kind==UNARY):
            return self.name + " "+ self.prop+ " (" + self.child.__str__() +")"
        elif (self.kind==BINARY):
            if self.left.kind==RELATION:
                le=self.left.__str__()
            else:
                le="("+self.left.__str__()+")"
            if self.right.kind==RELATION:
                re=self.right.__str__()
            else:
                re="("+self.right.__str__()+")"
                
            return (le+ self.name +re)

def tokenize(expression):
    '''This function converts an expression into a list where
    every token of the expression is an item of a list. Expressions into
    parenthesis will be converted into sublists.'''
    items=[] #List for the tokens
    
    '''This is a state machine. Initial status is determined by the starting of the
    expression. There are the following statuses:
    
    relation: this is the status if the expressions begins with something else than an
        operator or a parenthesis.
    binary operator: this is the status when parsing a binary operator, nothing much to say
    unary operator: this status is more complex, since it will be followed by a parameter AND a
        sub-expression.
    sub-expression: this status is entered when finding a '(' and will be exited when finding a ')'.
        means that the others open must be counted to determine which close is the right one.'''
    
    expression=expression.strip()
    state=0
    '''
    0 initial and useless
    1 previous stuff was a relation
    2 previous stuff was a sub-expression
    3 previous stuff was a unary operator
    4 previous stuff was a binary operator
    '''

    while len(expression)>0:
        if expression.startswith('('): #Parenthesis state
            state=2
            par_count=0 #Count of parenthesis
            end=0
            
            for i in range(len(expression)):
                if expression[i]=='(':
                    par_count+=1
                elif expression[i]==')':
                    par_count-=1
                    if par_count==0:
                        end=i
                        break
            items.append(tokenize(expression[1:end]))
            expression=expression[end+1:].strip()
        
        elif expression.startswith("σ") or expression.startswith("π") or expression.startswith("ρ"): #Unary 2 bytes
            items.append(expression[0:2]) #Adding operator in the top of the list
            expression=expression[2:].strip() #Removing operator from the expression
            par=expression.find('(')
        
            items.append(expression[:par]) #Inserting parameter of the operator
            expression=expression[par:].strip() #Removing parameter from the expression
        elif expression.startswith("*") or expression.startswith("-"): # Binary 1 byte
            items.append(expression[0])
            expression=expression[1:].strip() #1 char from the expression
            state=4
        elif expression.startswith("ᑎ") or expression.startswith("ᑌ"): #Binary short 3 bytes
            items.append(expression[0:3]) #Adding operator in the top of the list
            expression=expression[3:].strip() #Removing operator from the expression

            state=4
        elif expression.startswith("ᐅ"): #Binary long
            i=expression.find("ᐊ")
            items.append(expression[:i+3])
            expression=expression[i+3:].strip()
            
            state=4
        else: #Relation (hopefully)
            if state==1: #Previous was a relation, appending to the last token
                i=items.pop()
                items.append(i+expression[0])
                expression=expression[1:].strip() #1 char from the expression
            else:
                state=1
                items.append(expression[0])
                expression=expression[1:].strip() #1 char from the expression
    
    return items

def tree(expression):
    '''This function parses a relational algebra expression into a tree and returns
    the root node using the Node class defined in this module.'''
    return node(tokenize(expression))

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
    #n=node(u"((((((((((((2)))))))))))) - (3 * 5) - 2")
    #n=node(u"π a,b (d-a*b)")
    
    #print n.__str__()
    #a= tokenize("(a - (a ᑌ b) * π a,b (a-b)) - ρ 123 (a)")
    #a= tokenize(u"π a,b (a*b)")
    #a=tokenize("(a-b*c)*(b-c)")
    print tree("σ i==2 (c ᑌ d - (aᑎb))") == tree("σ i==3 (c ᑌ d - (aᑎb))")
    a=general_optimize("π age➡a(π ciccio➡age(R))")
    #a=general_optimize("σ i==2 (σ b>5 (d))")
    print '=========',a
    #print node(a)
    #print tokenize("(a)")