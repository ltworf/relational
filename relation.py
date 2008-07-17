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

class relation (object):
	'''This objects defines a relation (as a group of consistent tuples) and operations
	A relation can be represented using a table
	Calling an operation and providing a non relation parameter when it is expected will
	result in a None value'''	
	def __init__(self,filename=""):
		'''Creates a relation, accepts a filename and then it will load the relation from
		that file. If no parameter is supplied an empty relation is created. Empty
		relations are used in internal operations'''
		if len(filename)==0:#Empty relation
			self.content=[]
			self.header=header([])
			return
		fp=file(filename)
		self.header=header(fp.readline().replace("\n","").strip().split(" "))
		
		self.content=[]
		row=fp.readline()
		while len(row)!=0:#Reads the content of the relation
			self.content.append(row.replace("\n","").strip().split(" "))
			row=fp.readline()
		fp.close()
		
	
	def save(self,filename):
		'''Saves the relation in a file'''
		res=""
		for f in self.header.attributes:
			res+="%s "%(f)
		
		
		for r in self.content:
			res+="\n"
			for i in r:
				res+="%s "% (i)
		fp=file(filename,'w')
		fp.write(res)
		fp.close()
	def selection(self,expr):
		'''Selection, expr must be a valid boolean expression, can contain field names,
		constant, math operations and boolean ones.'''
		attributes={}
		newt=relation()
		newt.header=header(list(self.header.attributes))
		for i in self.content:
			for j in range(len(self.header.attributes)):
				if i[j].isdigit():
					attributes[self.header.attributes[j]]=int(i[j])
				else:
					attributes[self.header.attributes[j]]=i[j]
				
			
			
			if eval(expr,attributes):
				newt.content.append(i)
		return newt
	def product (self,other):
		'''Cartesian product, attributes must be different to avoid collisions
		Doing this operation on relations with colliding attributes will 
		cause the return of a None value.
		It is possible to use rename on attributes and then use the product'''
		
		if (self.__class__!=other.__class__)or(self.header.sharedAttributes(other.header)!=0):
			return None
		newt=relation()
		newt.header=header(self.header.attributes+other.header.attributes)
		
		for i in self.content:
			for j in other.content:
				newt.content.append(i+j)
		return newt
		
	
	def projection(self,* attributes):
		'''Projection operator, takes many parameters, for each field to use.
		Can also use a single parameter with a list.
		Will delete duplicate items
		If an empty list or no parameters are provided, returns None'''	
		#Parameters are supplied in a list, instead with multiple parameters
		if attributes[0].__class__ == list().__class__:
			attributes=attributes[0]
		
		#Avoiding duplicated attributes
		attributes1=[]
		for i in attributes:
			if i not in attributes1:
				attributes1.append(i)
		attributes=attributes1
		
		ids=self.header.getAttributesId(attributes)
		
		if len(ids)==0:
			return None
		newt=relation()
		#Create the header
		h=[]
		for i in ids:
			h.append(self.header.attributes[i])
		newt.header=header(h)
		
		#Create the body
		for i in self.content:
			row=[]
			for j in ids:
				row.append(i[j])
			if row not in newt.content:#Avoids duplicated items
				newt.content.append(row)
		return newt
		
		
	
	def rename(self,*params):
		'''Operation rename. Takes an even number of parameters: (old,new,old,new....)
		Will replace the 1st parameter with the 2nd, the 3rd with 4th, and so on...
		If an "old" field doesn't exist, None will be returned'''
		result=[]
		
		newt=relation()
		newt.header=header(list(self.header.attributes))
		
		for i in range(len(params)):
			if i%2==0:
				if (newt.header.rename(params[i],params[i+1])) == False:
					return None
		
		newt.content=list(self.content)
		return newt
		
	def intersection(self,other):
		'''Intersection operation. The result will contain items present in both
		operands.
		Will return an empty one if there are no common items.
		Will return None if headers are different.
		It is possible to use projection and rename to make headers match.'''
		if (self.__class__!=other.__class__)or(self.header!=other.header):
			return None
		newt=relation()
		newt.header=header(list(self.header.attributes))
		
		#Adds only element not in other, duplicating them
		for e in self.content:
			if e in other.content:
				newt.content.append(list(e))
		return newt
	
	def difference(self,other):
		'''Difference operation. The result will contain items present in first
		operand but not in second one.
		Will return an empty one if the second is a superset of first.
		Will return None if headers are different.
		It is possible to use projection and rename to make headers match.'''
		if (self.__class__!=other.__class__)or(self.header!=other.header):
			return None
		newt=relation()
		newt.header=header(list(self.header.attributes))
		
		#Adds only element not in other, duplicating them
		for e in self.content:
			if e not in other.content:
				newt.content.append(list(e))
		return newt
	
	def union(self,other):
		'''Union operation. The result will contain items present in first
		and second operands.
		Will return an empty one if both are empty.
		Will not insert tuplicated items.
		Will return None if headers are different.
		It is possible to use projection and rename to make headers match.'''
		if (self.__class__!=other.__class__)or(self.header!=other.header):
			return None
		newt=relation()
		newt.header=header(list(self.header.attributes))
		
		#Adds element from self, duplicating them all
		for e in self.content:
			newt.content.append(list(e))
		
		for e in other.content:
			if e not in newt.content:
				newt.content.append(list(e))
		return newt
		
	def join(self,other):
		'''Natural join, joins on shared attributes (one or more). If there are no
		shared attributes, it will behave as cartesian product.'''
		shared=[]
		for i in self.header.attributes:
			if i in other.header.attributes:
				shared.append(i)
		
		newt=relation() #Creates the new relation
		
		#Adds all the attributes of the 1st relation
		newt.header=header(list(self.header.attributes))
		
		#Adds all the attributes of the 2nd, when non shared
		for i in other.header.attributes:
			if i not in shared:
				newt.header.attributes.append(i)
		#Shared ids of self
		sid=self.header.getAttributesId(shared)
		#Shared ids of the other relation
		oid=other.header.getAttributesId(shared)
		
		#Non shared ids of the other relation
		noid=[]
		for i in range(len(other.header.attributes)):
			if i not in oid:
				noid.append(i)
		
		for i in self.content:
			for j in other.content:
				match=True
				for k in range(len(sid)):
					match=match and ( i[sid[k]]== j[oid[k]])
						
				if match:
					item=list(i)
					for l in noid:
						item.append(j[l])
					
					newt.content.append(item)
		
		return newt
		
	def __str__(self):
		'''Returns a string representation of the relation, can be printed with 
		monospaced fonts'''
		m_len=[] #Maximum lenght string
		for f in self.header.attributes:
			m_len.append(len(f))
		
		for f in self.content:
			col=0
			for i in f:
				if len(i)>m_len[col]:
					m_len[col]=len(i)
				col+=1
				
		
		res=""
		for f in range(len(self.header.attributes)):
			res+="%s"%(self.header.attributes[f].ljust(2+m_len[f]))
		
		
		for r in self.content:
			col=0
			res+="\n"
			for i in r:
				res+="%s"% (i.ljust(2+m_len[col]))
				col+=1
			
		return res
	
class header (object):
	'''This class defines the header of a relation.
	It is used within relations to know if requested operations are accepted'''
	
	def __init__(self,attributes):
		'''Accepts a list with attributes' names. Names MUST be unique'''
		self.attributes=attributes
	def __repr__(self):
		return "header(%s)" % (self.attributes.__repr__())
		
	
	def rename(self,old,new):
		'''Renames a field. Doesn't check if it is a duplicate.
		Returns True if the field was renamed, False otherwise'''
		for i in range(len(self.attributes)):
			if self.attributes[i]==old:
				self.attributes[i]=new
				return True
		return False #Requested field was not found	
		
	
	def sharedAttributes(self,other):
		'''Returns how many attributes this header has in common with a given one'''
		res=0
		for i in self.attributes:
			if i in other.attributes:
				res+=1
		return res
	
	def __str__(self):
		'''Returns String representation of the field's list'''
		return self.attributes.__str__()
	
	def __eq__(self,other):
		return self.attributes==other.attributes
	def __ne__(self,other):
		return self.attributes!=other.attributes
	
	def getAttributesId(self,param):
		'''Returns a list with numeric index corresponding to field's name'''	
		res=[]
		for i in param:
			for j in range(len(self.attributes)):
				if i==self.attributes[j]:
					res.append(j)
		return res
		
if __name__=="__main__":
	a=["id","nome","cognome"]
	
	b=header(a)
	print "b=", b.__repr__()
	b.rename("nome","nick")
	
	a=["id","nome","cognome"]
	c=header(a)
	print b, c
	print b==c
	