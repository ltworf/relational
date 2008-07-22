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
	symbols=("σ","π","ρ")
	
	starts=[]#List with starts and ends
	parenthesis=0
	lexpr=list(expr)
	#Parses the string finding all 1st level parenthesis
	for i in range(len(lexpr)):
		if lexpr[i]=="(":
			if parenthesis==0:
				starts.append(i+1)
			parenthesis+=1
		elif lexpr[i]==")":
			parenthesis-=1
			if parenthesis==0:
				starts.append(i)
			
	
	if len(starts)==0: #No parenthesis: no operators with parameters
		return parse_op(expr)
	
	
	
	while len(starts)>0:
		
		#Converting the last complex operator into python
		
		end=starts.pop()
		start=starts.pop()
		
		internal=parse(expr[start:end])
		
		endp=start-1
		symbol=""
		for i in range(endp,-1,-1):
			if expr[i:i+2] in symbols:
				symbol=expr[i:i+2]
				start=i+2
				break
			elif expr[i:i+1] ==")":
				break #No symbol before
				
		parameters=expr[start:endp]
		
		res="" #String for result
		if symbol=="π":#Projection
			params=""
			count=0
			for i in parameters.split(","):
				if count!=0:
					params+=","
				else:
					count=1
				params+="\"%s\"" % (i.strip())
				
			res="%s.projection(%s)" % (internal,params)
			expr= ("%s%s%s") % (expr[0:start-2],res,expr[end+1:])
		elif symbol== "σ": #Selection
			res="%s.selection(\"%s\")" % (internal,parameters)
			expr= ("%s%s%s") % (expr[0:start-2],res,expr[end+1:])
		elif symbol=="ρ": #Rename
			params=parameters.replace(",","\",\"").replace("➡","\",\"").replace(" ","")
			res="%s.rename(\"%s\")" % (internal,params)
			expr= ("%s%s%s") % (expr[0:start-2],res,expr[end+1:])
		else:
			res="(%s)" % (internal)
			expr= ("%s%s%s") % (expr[0:start-1],res,expr[end+1:])
		#Last complex operator is replaced with it's python code
		#Next cycle will do the same to the new last unparsed complex operator
		#At the end, parse_op will convert operators without parameters
		
		
	return parse_op(expr)
	
def parse_op(expr):
	'''This function parses a relational algebra expression including only operators 
	without parameters, converting it into python.
	Executable by eval function to get the result of the expression.'''
	
	result=""
	symbols={}
	
	symbols["*"]=".product(%s)"
	symbols["-"]=".difference(%s)"
	symbols["ᑌ"]=".union(%s)"
	symbols["ᑎ"]=".intersection(%s)"
	symbols["ᐅLEFTᐊ"]=".outer_left(%s)"
	symbols["ᐅRIGHTᐊ"]=".outer_right(%s)"
	symbols["ᐅFULLᐊ"]=".outer(%s)"
	symbols["ᐅᐊ"]=".join(%s)"
	
	
	for i in symbols:
		expr=expr.replace(i,"_____%s_____"% (i))
	
	tokens=expr.split("_____")
	
	i=0;
	tk_l=len(tokens)
	while i<tk_l:
		if tokens[i] not in symbols:
			result+=tokens[i].strip()
		else:
			
			result+=symbols[tokens[i]] % (tokens[i+1].strip())
			i+=1
		i+=1
	return result
		
if __name__=="__main__":
	while True:
		e=raw_input("Expression: ")
		print parse(e)
	