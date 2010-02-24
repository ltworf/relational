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

'''This module converts SQL queries into relational algebra expressions'''

def stub():
    "NATURAL JOIN"
    "CROSS JOIN" ,
def extract_select(query,internal=''):
    

    #Handling select *
    if len(query)==1 and query[0]=='*':
        return ''
    #Create dictionary for projection and rename        .
    #Keys are fields to project. Value is none if no rename is needed
    pr_dic={}
    key=None
    for i in query:
        if i.lower() ==',':
            key=None
        elif key==None:
            pr_dic[i]=None
            key=i
        else:
            pr_dic[key]=i
    
    #Preparing string for projection and rename
    ren=''
    proj=''
    for i in pr_dic.iterkeys():
        proj+=',%s'%i
        if pr_dic[i]!=None:
            ren+=',%s➡%s'%(i,pr_dic[i])
    #Removes starting commas
    ren=ren[1:]
    proj=proj[1:]
    
    result='π %s (%s)' % (proj,internal)
    if len(ren)!=0:
        result='ρ %s (%s)' % (ren,result)
    return result
def extract_from(query):
    return query

def sql2relational(query):
    query=query.replace('\n',' ').replace(',',' , ')

    tokens=[]
    
    t=query.split(' ')
    escape=False
    for i in range(len(t)):
        tok=t[i].lower().strip()
        if tok=='from' and not escape:
            break
            
        if tok in ('select','as',','):
            escape=True
        else:
            escape=False
    
    return extract_select(t[1:i])
















class table(object):
    def __init__(self):
        self.attr=[]
        self.realname=None
        pass
    




sqlops=('SELECT','FROM','WHERE',',',';')

import optimizations


if __name__=="__main__":
    
    query="SELECT * FROM a AS b,a WHERE a.id!= b.id and a.age<12 or b.sucation==4 or d=3;"
            
    query=query.replace(',',' , ').replace(';',' ; ')
    print query
    parts=query.split(' ')
    tokens=[]
    
    temp=''
    lastop=None
    for i in parts:
        if i in sqlops:
            # TODO must tokenize (blabla(bla)) as a single token
            if lastop == 'WHERE': #Where is a special case, must tokenize all the stuff
                for j in optimizations.tokenize_select(temp):
                    tokens.append(j.strip())
            else:
                tokens.append(temp.strip())
            tokens.append(i.strip())
            temp=''
            lastop=i
        else:
            temp+=i+' '
    
    tokens=tokens[1:]   #Removes futile 1st empty element
    print tokens
    
    
    
    rels={}
    
    from_=[]
    where_=[]
    select_=[]
    
    
    for i in tokens:
        if i in ('SELECT','FROM','WHERE'):
            last=i
            continue
        
        
        if last=='FROM':
            if ' AS ' in i:
                parts=i.split(' AS ')
                rels[parts[1].strip()]=table()
                rels[parts[1].strip()].realname=parts[0].strip()
                from_.append(parts[1].strip())
                pass
            else:
                if i!=',':
                    rels[i.strip()]=table()
                from_.append(i.strip())
                pass
                
        elif last=='WHERE':
            where_.append(i)
            if i in optimizations.sel_op:
                continue
            if '.' in i:
                parts=i.split('.',1)
                if parts[1] not in rels[parts[0]].attr:
                    rels[parts[0]].attr.append(parts[1])
        elif last=='SELECT':
            # TODO should do like the same of WHERE but supporting AS too
            pass
    
    
    
    for i in rels.keys():
        print "========" + i + "========"
        print rels[i].attr
        print rels[i].realname
    
    print from_
    for i in from_:
        if i in rels.keys():
            print i
    
    #print sql2relational('SELECT a,c AS q FROM from;')