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

import optimizer

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
    
    IMPORTANT: The encoding used by this module is UTF-8
    
    EXAMPLES
    σage > 25 and rank == weight(A)
    Q ᐅᐊ π a,b(A) ᐅᐊ B
    ρid➡i,name➡n(A) - π a,b(π a,b(A)) ᑎ σage > 25 or rank = weight(A)
    π a,b(π a,b(A))
    ρid➡i,name➡n(π a,b(A))
    A ᐅᐊ B
    '''
    return optimizer.tree(expr).toPython()
    
if __name__=="__main__":
    while True:
        e=raw_input("Expression: ")
        print parse(e)
        