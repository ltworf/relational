# coding=UTF-8
# Relation
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

def parse(expr):
	'''This function parses a relational algebra expression, converting it into python, 
	executable by eval function to get the result of the expression.'''
	
	#Selection σage > 25 Λ rank = weight(A)
	#Projection π a,b(A)
	#Rename ρid➡i,name➡n(A)
	#A ᑌ B
	#A ᐅᐊ B
	#A ᑎ B

	result=""
	symbols={}
	symbols["*"]=".product(%s)"
	symbols["-"]=".difference(%s)"
	symbols["ᑌ"]=".union(%s)"
	symbols["ᑎ"]=".intersection(%s)"
	symbols["ᐅᐊ"]=".join(%s)"
	symbols["ᐅᐊLEFT"]=".outer_left(%s)"
	symbols["ᐅᐊRIGHT"]=".outer_right(%s)"
	symbols["ᐅᐊFULL"]=".outer(%s)"
	
	tokens=expr.split(" ")
	
	i=0;
	tk_l=len(tokens)
	while i<tk_l:
		if tokens[i] not in symbols:
			result+=tokens[i]
		else:
			
			result+=symbols[tokens[i]] % (tokens[i+1])
			i+=1
		i+=1
	return result
		
if __name__=="__main__":
	while True:
		e=raw_input("Expression: ")
		print parse(e)
	