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
#
#
#
# This module implements a parser for relational algebra, and can be used
# to convert expressions into python expressions and to get the parse-tree
# of the expression.
#
# The input must be provided in UTF-8
# 
#
# Language definition:
# Query := Ident
# Query := Query BinaryOp Query
# Query := (Query) 
# Query := σ PYExprWithoutParenthesis (Query) | σ (PYExpr) (Query) 
# Query := π FieldList (Query) 
# Query := ρ RenameList (Query) 
# FieldList := Ident | Ident , FieldList
# RenameList := Ident ➡ Ident | Ident ➡ Ident , RenameList
# BinaryOp := * | - | ᑌ | ᑎ | ÷ | ᐅᐊ | ᐅLEFTᐊ | ᐅRIGHTᐊ | ᐅFULLᐊ
#
# Language definition here:
# https://galileo.dmi.unict.it/wiki/relational/doku.php?id=language


RELATION=0
UNARY=1
BINARY=2

PRODUCT=u'*'
DIFFERENCE=u'-'
UNION=u'ᑌ'
INTERSECTION=u'ᑎ'
DIVISION=u'÷'
JOIN=u'ᐅᐊ'
JOIN_LEFT=u'ᐅLEFTᐊ'
JOIN_RIGHT=u'ᐅRIGHTᐊ'
JOIN_FULL=u'ᐅFULLᐊ'
PROJECTION=u'π'
SELECTION=u'σ'
RENAME=u'ρ'
ARROW=u'➡'

b_operators=(PRODUCT,DIFFERENCE,UNION,INTERSECTION,DIVISION,JOIN,JOIN_LEFT,JOIN_RIGHT,JOIN_FULL) # List of binary operators
u_operators=(PROJECTION,SELECTION,RENAME) # List of unary operators

op_functions={PRODUCT:'product',DIFFERENCE:'difference',UNION:'union',INTERSECTION:'intersection',DIVISION:'division',JOIN:'join',JOIN_LEFT:'outer_left',JOIN_RIGHT:'outer_right',JOIN_FULL:'outer',PROJECTION:'projection',SELECTION:'selection',RENAME:'rename'} # Associates operator with python method

class node (object):
    '''This class is a node of a relational expression. Leaves are relations and internal nodes are operations.
    
    The kind property says if the node is a binary operator, unary operator or relation.
    Since relations are leaves, a relation node will have no attribute for children.
    
    If the node is a binary operator, it will have left and right properties.
    
    If the node is a unary operator, it will have a child, pointing to the child node and a prop containing
    the string with the props of the operation.
    
    This class is used to convert an expression into python code.'''
    kind=None
    __hash__=None
    
    def __init__(self,expression=None):
        '''Generates the tree from the tokenized expression
        If no expression is specified then it will create an empty node'''
        if expression==None or len(expression)==0:
            return
        
        #If the list contains only a list, it will consider the lower level list.
        #This will allow things like ((((((a))))) to work
        while len(expression)==1 and isinstance(expression[0],list): 
                expression=expression[0]
        
        #The list contains only 1 string. Means it is the name of a relation
        if len(expression)==1 and isinstance(expression[0],unicode): 
            self.kind=RELATION
            self.name=expression[0]
            return
        
        '''Expression from right to left, searching for binary operators
        this means that binary operators have lesser priority than
        unary operators.
        It finds the operator with lesser priority, uses it as root of this
        (sub)tree using everything on its left as left parameter (so building
        a left subtree with the part of the list located on left) and doing 
        the same on right.
        Since it searches for strings, and expressions into parenthesis are
        within sub-lists, they won't be found here, ensuring that they will
        have highest priority.'''
        for i in range(len(expression)-1,-1,-1): 
            if expression[i] in b_operators: #Binary operator   
                self.kind=BINARY
                self.name=expression[i]
                self.left=node(expression[:i]) 
                self.right=node(expression[i+1:])
                return
        '''Searches for unary operators, parsing from right to left'''
        for i in range(len(expression)-1,-1,-1):
            if expression[i] in u_operators: #Unary operator
                self.kind=UNARY
                self.name=expression[i]
                self.prop=expression[1+i].strip()
                self.child=node(expression[2+i])
                
                return       
        pass
    def toPython(self):
        '''This method converts the expression into python code, which will require the
        relation module to be executed.'''
        if self.name in b_operators:
            return '%s.%s(%s)' % (self.left.toPython(),op_functions[self.name],self.right.toPython())
        elif self.name in u_operators:
            prop =self.prop
            
            #Converting parameters
            if self.name==PROJECTION:
                prop='\"%s\"' %  prop.replace(' ','').replace(',','\",\"')
            elif self.name==RENAME:
                prop='{\"%s\"}' % prop.replace(',','\",\"').replace(ARROW,'\":\"').replace(' ','')
            else: #Selection
                prop='\"%s\"' %  prop
                        
            return '%s.%s(%s)' % (self.child.toPython(),op_functions[self.name],prop)
        else:
            return self.name
        pass
    def printtree(self,level=0):
        '''returns a representation of the tree using indentation'''
        r=''
        for i in range(level):
            r+='  '
        r+=self.name
        if self.name in b_operators:
            r+=self.left.printtree(level+1)
            r+=self.right.printtree(level+1)
        elif self.name in u_operators:
            r+='\t%s\n' % self.prop
            r+=self.child.printtree(level+1)
            
        return '\n'+r
    def get_left_leaf(self):
        '''This function returns the leftmost leaf in the tree. It is needed by some optimizations.'''
        if self.kind==RELATION:
            return self
        elif self.kind==UNARY:
            return self.child.get_left_leaf()
        elif self.kind==BINARY:
            return self.left.get_left_leaf()
        
        
    def result_format(self,rels):
        '''This function returns a list containing the fields that the resulting relation will have.
        It requires a dictionary where keys are the names of the relations and the values are
        the relation objects.'''
        if rels==None:            
            return
        
        if self.kind==RELATION:
            return list(rels[self.name].header.attributes)
        elif self.kind==BINARY and self.name in (DIFFERENCE,UNION,INTERSECTION):
            return self.left.result_format(rels)
        elif self.kind==BINARY and self.name==DIVISION:
            return list(set(self.left.result_format(rels)) - set(self.right.result_format(rels)))
        elif self.name==PROJECTION:
            l=[]
            for i in self.prop.split(','):
                l.append(i.strip())
            return l
        elif self.name==PRODUCT:
            return self.left.result_format(rels)+self.right.result_format(rels)
        elif self.name==SELECTION:
            return self.child.result_format(rels)
        elif self.name==RENAME:
            _vars={}
            for i in self.prop.split(','):
                q=i.split(ARROW)
                _vars[q[0].strip()]=q[1].strip()
            
            _fields=self.child.result_format(rels)
            for i in range(len(_fields)):
                if _fields[i] in _vars:
                    _fields[i]=_vars[_fields[i]]
            return _fields
        elif self.name in (JOIN,JOIN_LEFT,JOIN_RIGHT,JOIN_FULL):
            return list(set(self.left.result_format(rels)).union(set(self.right.result_format(rels))))
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

def _find_matching_parenthesis(expression,start=0,openpar=u'(',closepar=u')'):
    '''This function returns the position of the matching
    close parenthesis to the 1st open parenthesis found
    starting from start (0 by default)'''
    par_count=0 #Count of parenthesis
    for i in range(start,len(expression)):
        if expression[i]==openpar:
            par_count+=1
        elif expression[i]==closepar:
            par_count-=1
            if par_count==0:
                return i #Closing parenthesis of the parameter

def tokenize(expression):
    '''This function converts an expression into a list where
    every token of the expression is an item of a list. Expressions into
    parenthesis will be converted into sublists.'''
    if not isinstance(expression,unicode):
        raise Exception('expected unicode')
    
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
    
    expression=expression.strip() #Removes initial and endind spaces
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
            end=_find_matching_parenthesis(expression)
            #Appends the tokenization of the content of the parenthesis
            items.append(tokenize(expression[1:end]))
            #Removes the entire parentesis and content from the expression
            expression=expression[end+1:].strip()
        
        elif expression.startswith(u"σ") or expression.startswith(u"π") or expression.startswith(u"ρ"): #Unary 2 bytes
            items.append(expression[0:1]) #Adding operator in the top of the list
            expression=expression[1:].strip() #Removing operator from the expression
            
            if expression.startswith('('): #Expression with parenthesis, so adding what's between open and close without tokenization
                par=expression.find('(',_find_matching_parenthesis(expression)) 
            else: #Expression without parenthesis, so adding what's between start and parenthesis as whole  
                par=expression.find('(')
            
            items.append(expression[:par].strip()) #Inserting parameter of the operator
            expression=expression[par:].strip() #Removing parameter from the expression
        elif expression.startswith("*") or expression.startswith("-"): # Binary 1 byte
            items.append(expression[0])
            expression=expression[1:].strip() #1 char from the expression
            state=4
        elif expression.startswith(u"ᑎ") or expression.startswith(u"ᑌ"): #Binary short 3 bytes
            items.append(expression[0:1]) #Adding operator in the top of the list
            expression=expression[1:].strip() #Removing operator from the expression
            state=4
        elif expression.startswith(u"÷"): #Binary short 2 bytes
            items.append(expression[0:1]) #Adding operator in the top of the list
            expression=expression[1:].strip() #Removing operator from the expression
            state=4
        elif expression.startswith(u"ᐅ"): #Binary long
            i=expression.find(u"ᐊ")
            items.append(expression[:i+1])
            expression=expression[i+1:].strip()
            
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



def parse(expr):
    '''This function parses a relational algebra expression, converting it into python, 
    executable by eval function to get the result of the expression.
    It has 2 class of operators:
    without parameters
    *, -, ᑌ, ᑎ, ᐅᐊ, ᐅLEFTᐊ, ᐅRIGHTᐊ, ᐅFULLᐊ
    with parameters:
    σ, π, ρ
    
    Syntax for operators without parameters is:
    relation operator relation
    
    Syntax for operators with parameters is:
    operator parameters (relation)
    
    Since a*b is a relation itself, you can parse π a,b (a*b).
    And since π a,b (A) is a relation, you can parse π a,b (A) ᑌ B.
    
    You can use parenthesis to change priority: a ᐅᐊ (q ᑌ d).
    
    IMPORTANT: The encoding used by this module is UTF-8 (all strings must be UTF-8)
    
    EXAMPLES
    σage > 25 and rank == weight(A)
    Q ᐅᐊ π a,b(A) ᐅᐊ B
    ρid➡i,name➡n(A) - π a,b(π a,b(A)) ᑎ σage > 25 or rank = weight(A)
    π a,b(π a,b(A))
    ρid➡i,name➡n(π a,b(A))
    A ᐅᐊ B
    '''
    return tree(expr).toPython()
    
if __name__=="__main__":
    #while True:
    #    e=raw_input("Expression: ")
    #    print parse(e)
    b=u"σ age>1 and skill=='C' (peopleᐅᐊskills)"
    print b[0]
    parse(b)
    