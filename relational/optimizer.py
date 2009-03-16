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

RELATION=0
UNARY=1
BINARY=2

class node (object):
    '''This class is a node of a relational expression. Leaves are relations and internal nodes are operations.'''
    def __init__(self,expression):
        expression=expression.strip()
            
        print "Parsing: ",expression
        '''expression must be a valid relational algrbra expression that would be accepted by the parser
        and must be utf16'''
        self.kind=0
        self.name="a"
        self.prop=""
        '''*-ᑌᑎᐅᐊᐅLEFTᐊᐅRIGHTᐊᐅFULLᐊπσρ'''
        
        binary=(u"*",u"-",u"ᑌ",u"ᑎ")
        unary=(u"π",u"σ",u"ρ")
        '''(a ᑌ (a ᑌ b ᑌ c ᑌ d)) ᑎ c - σ i==3(πa,b(aᑌ b ᑎ c))'''
        level=0 #Current parentesis level
        start=-1 #Start of the parentesis
        end=-1 #End of the parentesis.
        tokens=list(expression) #Splitted expression
        r=range(len(tokens))
        r.reverse()
        lev_non_zero_chars=0 #Number of chars inside parentesis
        for i in r: #Parses expression from end to begin, to preserve operation's order
            if tokens[i]==u"(":
                if level==0:
                    start=i
                    print start
                level+=1
            elif tokens[i]==u")":
                level-=1
                if level==0:
                    end=i
                    print end
            
            if level!=0:
                lev_non_zero_chars+=1
            
            if i==0 and level==0 and tokens[i] in unary: #Unary operator found, must grab its parameters and its child relation they
                child=""
                for q in tokens[start+1:end]:
                    child+=q
                self.name= tokens[i]
                print "-----",tokens[i]
                print "---",start,end,lev_non_zero_chars
                print child
                #print prop
                #self.child=node(child)
                
            if level==0 and tokens[i] in binary: #Binary operator found, everything on left will go in the left subree and everhthing on the right will go in the right subtree
                self.kind=BINARY
                left=""
                right=""
                
                if start==end==-1:#No parentesis before
                    end=i
                
                for q in tokens[start+1:end]:
                    left+=q
                self.name= tokens[i]
                for q in tokens[i+1:]:
                    right+=q
                print "self: ",tokens[i]
                print "left: ",left
                print "right:" ,right
                self.left=node(left)
                self.right=node(right)

                return
        
        if lev_non_zero_chars!=0 and lev_non_zero_chars+1==len(expression):#Expression is entirely contained in parentesis, removing them
            n=node(expression[1:-1])
            self.name=n.name
            self.kind=n.kind
            if n.kind==UNARY:
                self.child=n.child
            elif n.kind==BINARY:
                self.left=n.left
                self.right=n.right
            self.prop=n.prop
            return
                
        self.kind=RELATION
        self.name=expression
        
    def __str__(self):
        if (self.kind==RELATION):
            return self.name
        elif (self.kind==UNARY):
            return self.name + " "+ self.prop+ " (" + self.child +")"
        elif (self.kind==BINARY):
            if self.left.kind==RELATION:
                left=self.left.__str__()
            else:
                left=u"("+self.left.__str__()+u")"
            if self.right.kind==RELATION:
                right=self.right.__str__()
            else:
                right=u"("+self.right.__str__()+u")"
                
            return (left+ self.name +right)

def parseList(expression):
    '''This function converts an expression into a list where
    every token of the expression is an item of a list. Expressions into
    parenthesis will be converted into sublists.'''
    items=[] #List for the tokens
    par_count=0 #Count of parenthesis
    
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
    
    if expression.startswith('('): #Parenthesis state
        pass
    elif expression.startswith("σ"): or expression.startswith("π") or expression.startswith("ρ"): #Unary
        items.append(expression[0:2]) #Adding operator in the top of the list
        
        expression=expression[2:].strip() #Removing operator from the expression
        par=expression.find('(')
        
        items.append(expression[:par]) #Inserting parameter of the operator
        expression=expression[par:].strip() #Removing parameter from the expression
        pass
    elif expression.startswith("*") or expression.startswith("-") or  expression.startswith("ᑎ") or expression.startswith("ᑌ"): #Binary short
        pass
    elif expression.startswith("ᐅ"): #Binary long
        pass
    else:
        pass
    
    return items


if __name__=="__main__":
    #n=node(u"((a ᑌ b) - c ᑌ d) - b")
    #n=node(u"((((((((((((2)))))))))))) - (3 * 5) - 2")
    n=node(u"π a,b (d-a*b)")
    print n.__str__()