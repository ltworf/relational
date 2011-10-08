# -*- coding: utf-8 -*-
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
# This module provides a classes to represent relations and to perform
# relational operations on them.

from rtypes import *
import csv

class relation (object):
    '''This objects defines a relation (as a group of consistent tuples) and operations
    A relation can be represented using a table
    Calling an operation and providing a non relation parameter when it is expected will
    result in a None value'''    
    __hash__=None
    
    def __init__(self,filename=""):
        '''Creates a relation, accepts a filename and then it will load the relation from
        that file. If no parameter is supplied an empty relation is created. Empty
        relations are used in internal operations.
        By default the file will be handled like a comma separated as described in
        RFC4180, but it can also be handled like a space separated file (previous
        default format) setting to false the 2nd parameter.
        The old format is no longer supported.'''
        
        self._readonly=False
        
        if len(filename)==0:#Empty relation
            self.content=set()
            self.header=header([])
            return
        #Opening file
        fp=file(filename)

        reader=csv.reader(fp) #Creating a csv reader
        self.header=header(reader.next()) # read 1st line
        self.content=set()
        
        for i in reader.__iter__(): #Iterating rows
            self.content.add(tuple(i))
        
        #Closing file
        fp.close()
        
    def _make_writable(self):
        '''If this relation is marked as readonly, this 
        method will copy the content to make it writable too'''
        
        if self._readonly:
            self.content=set(self.content)
            self._readonly=False
        
    def save(self,filename):
        '''Saves the relation in a file. By default will save using the csv
        format as defined in RFC4180, but setting comma_separated to False,
        it will use the old format with space separated values.
        The old format is no longer supported.'''
        
        fp=file(filename,'w') #Opening file in write mode
        
        writer=csv.writer(fp) #Creating csv writer
            
        #It wants an iterable containing iterables
        head=(self.header.attributes,)
        writer.writerows(head)
            
        #Writing content, already in the correct format
        writer.writerows(self.content)
        fp.close() #Closing file
                
    def _rearrange_(self,other):
        '''If two relations share the same attributes in a different order, this method
        will use projection to make them have the same attributes' order.
        It is not exactely related to relational algebra. Just a method used 
        internally.
        Will return None if they don't share the same attributes'''
        if (self.__class__!=other.__class__):
            return None
        if self.header.sharedAttributes(other.header) == len(self.header.attributes) == len(other.header.attributes):
            return other.projection(list(self.header.attributes))
        return None
    
    def _autocast(self,string):
        '''Depending on the regexp matched by the string,
        it will perform automatic casting'''
        tmpstring=rstring(string)
        if len(tmpstring)>0 and tmpstring.isInt():
            return int(tmpstring)
        elif len(tmpstring)>0 and tmpstring.isFloat():
            return float(tmpstring)
        elif len(tmpstring)>0 and tmpstring.isDate():
            return rdate(tmpstring)
        else:
            return tmpstring
    
    def selection(self,expr):
        '''Selection, expr must be a valid boolean expression, can contain field names,
        constant, math operations and boolean ones.'''
        attributes={}
        newt=relation()
        newt.header=header(list(self.header.attributes))
        for i in self.content:
	    #Fills the attributes dictionary with the values of the tuple
            for j in range(len(self.header.attributes)):
                attributes[self.header.attributes[j]]=self._autocast(i[j])
                
            try:
                if eval(expr,attributes):
                    newt.content.add(i)
            except Exception,e:
                raise Exception("Failed to evaluate %s\n%s" % (expr,e.__str__()))
        return newt
    def product (self,other):
        '''Cartesian product, attributes must be different to avoid collisions
        Doing this operation on relations with colliding attributes will 
        cause an exception.
        It is possible to use rename on attributes and then use the product'''
        
        if (self.__class__!=other.__class__)or(self.header.sharedAttributes(other.header)!=0):
            raise Exception('Unable to perform product on relations with colliding attributes')
        newt=relation()
        newt.header=header(self.header.attributes+other.header.attributes)
        
        for i in self.content:
            for j in other.content:
                newt.content.add(i+j)
        return newt
        
    
    def projection(self,* attributes):
        '''Projection operator, takes many parameters, for each field to use.
        Can also use a single parameter with a list.
        Will delete duplicate items
        If an empty list or no parameters are provided, returns None'''    
        #Parameters are supplied in a list, instead with multiple parameters
        if isinstance(attributes[0],list):
            attributes=attributes[0]
        
        #Avoiding duplicated attributes
        attributes1=[]
        for i in attributes:
            if i not in attributes1:
                attributes1.append(i)
        attributes=attributes1
        
        ids=self.header.getAttributesId(attributes)
        
        if len(ids)==0 or len(ids)!=len(attributes):
            raise Exception('Invalid attributes for projection')
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
            newt.content.add(tuple(row))
        return newt
    
    def rename(self,params):
        '''Operation rename. Takes a dictionary
        Will replace the itmem with its content.
        For example if you want to rename a to b, provide {"a":"b"}
        '''
        result=[]
        
        newt=relation()
        newt.header=header(list(self.header.attributes))
        
        for old,new in params.iteritems():
            if (newt.header.rename(old,new)) == False:
                raise Exception('Unable to find attribute: %s' % old)
        
        newt.content=self.content
        newt._readonly=True
        return newt
        
    def intersection(self,other):
        '''Intersection operation. The result will contain items present in both
        operands.
        Will return an empty one if there are no common items.
        Will return None if headers are different.
        It is possible to use projection and rename to make headers match.'''
        other=self._rearrange_(other) #Rearranges attributes' order
        if (self.__class__!=other.__class__)or(self.header!=other.header):
            raise Exception('Unable to perform intersection on relations with different attributes')
        newt=relation()
        newt.header=header(list(self.header.attributes))
        
        newt.content=self.content.intersection(other.content)
        return newt
    
    def difference(self,other):
        '''Difference operation. The result will contain items present in first
        operand but not in second one.
        Will return an empty one if the second is a superset of first.
        Will return None if headers are different.
        It is possible to use projection and rename to make headers match.'''
        other=self._rearrange_(other) #Rearranges attributes' order
        if (self.__class__!=other.__class__)or(self.header!=other.header):
            raise Exception('Unable to perform difference on relations with different attributes')
        newt=relation()
        newt.header=header(list(self.header.attributes))
        
        newt.content=self.content.difference(other.content)
        return newt
    def division(self,other):
        '''Division operator
        The division is a binary operation that is written as R ÷ S. The
        result consists of the restrictions of tuples in R to the
        attribute names unique to R, i.e., in the header of R but not in the
        header of S, for which it holds that all their combinations with tuples
        in S are present in R. 
        '''
        
        #d_headers are the headers from self that aren't also headers in other
        d_headers=list(set(self.header.attributes) - set(other.header.attributes))
        
        
        '''
        Wikipedia defines the division as follows:
        
        a1,....,an are the d_headers
        
        T := πa1,...,an(R) × S
        U := T - R
        V := πa1,...,an(U)
        W := πa1,...,an(R) - V
        
        W is the result that we want
        '''
        
        t=self.projection(d_headers).product(other)
        return self.projection(d_headers).difference(t.difference(self).projection(d_headers))
        
    def union(self,other):
        '''Union operation. The result will contain items present in first
        and second operands.
        Will return an empty one if both are empty.
        Will not insert tuplicated items.
        Will return None if headers are different.
        It is possible to use projection and rename to make headers match.'''
        other=self._rearrange_(other) #Rearranges attributes' order
        if (self.__class__!=other.__class__)or(self.header!=other.header):
            raise Exception('Unable to perform union on relations with different attributes')
        newt=relation()
        newt.header=header(list(self.header.attributes))
        
        newt.content=self.content.union(other.content)
        return newt
    def thetajoin(self,other,expr):
        '''Defined as product and then selection with the given expression.'''
        return self.product(other).selection(expr)
    
    def outer(self,other):
        '''Does a left and a right outer join and returns their union.'''
        a=self.outer_right(other)
        b=self.outer_left(other)
        
        return a.union(b)
        
    def outer_right(self,other):
        '''Outer right join. Considers self as left and param as right. If the
        tuple has no corrispondence, empy attributes are filled with a "---"
        string. This is due to the fact that empty string or a space would cause
        problems when saving the relation.
        Just like natural join, it works considering shared attributes.'''
        return other.outer_left(self)
    
    def outer_left(self,other,swap=False):
        '''Outer left join. Considers self as left and param as right. If the 
        tuple has no corrispondence, empty attributes are filled with a "---" 
        string. This is due to the fact that empty string or a space would cause
        problems when saving the relation.
        Just like natural join, it works considering shared attributes.'''
        
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
            #Tuple partecipated to the join?
            added=False
            for j in other.content:
                match=True
                for k in range(len(sid)):
                    match=match and ( i[sid[k]]== j[oid[k]])
                        
                if match:
                    item=list(i)
                    for l in noid:
                        item.append(j[l])
                    
                    newt.content.add(tuple(item))
                    added=True
            #If it didn't partecipate, adds it
            if not added:
                item=list(i)
                for l in range(len(noid)):
                    item.append("---")
                newt.content.add(tuple(item))
        
        return newt
    
    def join(self,other):
        '''Natural join, joins on shared attributes (one or more). If there are no
        shared attributes, it will behave as cartesian product.'''
        
        #List of attributes in common between the relations
        shared=list(set(self.header.attributes).intersection(set(other.header.attributes)))
        
        newt=relation() #Creates the new relation
        
        #Adding to the headers all the fields, done like that because order is needed
        newt.header=header(list(self.header.attributes))
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
                    
                    newt.content.add(tuple(item))
        
        return newt
    def __eq__(self,other):
        '''Returns true if the relations are the same, ignoring order of items.
        This operation is rather heavy, since it requires sorting and comparing.'''
        other=self._rearrange_(other) #Rearranges attributes' order so can compare tuples directly
        
        if (self.__class__!=other.__class__)or(self.header!=other.header):
            return False #Both parameters must be a relation

        if set(self.header.attributes)!=set(other.header.attributes):
            return False
        
        
        
        #comparing content
        return self.content==other.content
        
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

    def update(self,expr,dic):
        '''Update, expr must be a valid boolean expression, can contain field names,
        constant, math operations and boolean ones.
        This operation will change the relation itself instead of generating a new one,
        updating all the tuples that make expr true.
        Dic must be a dictionary that has the form field name:value. Every kind of value
        will be converted into a string.
        Returns the number of affected rows.'''
        self._make_writable()
        affected=0
        attributes={}
        keys=dic.keys() #List of headers to modify
        f_ids=self.header.getAttributesId(keys) #List of indexes corresponding to keys
        
        #new_content=[] #New content of the relation
        for i in self.content:
            for j in range(len(self.header.attributes)):
                attributes[self.header.attributes[j]]=self._autocast(i[j])
                
            if eval(expr,attributes): #If expr is true, changing the tuple
                affected+=1
                new_tuple=list(i)
                #Deleting the tuple, instead of changing it, so other
                #relations can still point to the same list without
                #being affected.
                self.content.remove(i) 
                for k in range(len(keys)):
                    new_tuple[f_ids[k]]=str(dic[keys[k]])
                self.content.add(tuple(new_tuple))
        return affected
        
    def insert(self,values):
        '''Inserts a tuple in the relation.
        This function will not insert duplicate tuples.
        All the values will be converted in string.
        Will return the number of inserted rows.'''
        
        #Returns if tuple doesn't fit the number of attributes
        if len(self.header.attributes) != len(values):
            return 0
            
        self._make_writable()
            
        #Creating list containing only strings
        t=[]
        for i in values:
            t.append(str(i))
        
        prevlen=len(self.content)
        self.content.add(tuple(t))
        return len(self.content)-prevlen
    
    def delete(self,expr):
        '''Delete, expr must be a valid boolean expression, can contain field names,
        constant, math operations and boolean ones.
        This operation will change the relation itself instead of generating a new one,
        deleting all the tuples that make expr true.
        Returns the number of affected rows.'''
        self._make_writable()
        attributes={}
        affected=len(self.content)
        new_content=set() #New content of the relation
        for i in self.content:
            for j in range(len(self.header.attributes)):
                attributes[self.header.attributes[j]]=self._autocast(i[j])
                
                
            if not eval(expr,attributes):
                affected-=1
                new_content.add(i)
        self.content=new_content
        return affected
    
class header (object):
    '''This class defines the header of a relation.
    It is used within relations to know if requested operations are accepted'''
    
    #Since relations are mutalbe we explicitly block hashing them
    __hash__=None
    
    def __init__(self,attributes):
        '''Accepts a list with attributes' names. Names MUST be unique'''
        self.attributes=attributes
        
        for i in attributes:
            if not is_valid_relation_name(i):
                raise Exception('"%s" is not a valid attribute name'% i)
        
    def __repr__(self):
        return "header(%s)" % (self.attributes.__repr__())
        
    
    def rename(self,old,new):
        '''Renames a field. Doesn't check if it is a duplicate.
        Returns True if the field was renamed, False otherwise'''
        
        if not is_valid_relation_name(new):
            raise Exception('%s is not a valid attribute name'% new)
        
        try:
            id_=self.attributes.index(old)
            self.attributes[id_]=new
        except:
            return False
        return True
    
    def sharedAttributes(self,other):
        '''Returns how many attributes this header has in common with a given one'''
        return len(set(self.attributes).intersection(set(other.attributes)))
    
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
        