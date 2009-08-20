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

def sql2relational(query):
    query=query.replace('\n',' ').replace(',',' , ')
    
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
if __name__=="__main__":
    print sql2relational('SELECT a,c AS q FROM from;')