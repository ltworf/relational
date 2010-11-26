# -*- coding: utf-8 -*-
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

'''Custom types for relational algebra.
Purpose of this module is having the isFloat function and
implementing dates to use in selection.'''

import datetime

class rstring (str):
    '''String subclass with some custom methods'''
    def isFloat(self):
        '''True if the string is a float number, false otherwise'''
        lst=('0','1','2','3','4','5','6','7','8','9','.')
        for i in self:
            if i not in lst:
                return False;
        return True;

class rdate (object):
    '''Represents a date'''
    def __init__(self,date):
        sep=('-','/','\\')
        splitter=None
        for i in sep:
            if i in date:
                splitter=i
                break;
        elems=date.split(splitter)
        
        year=int(elems[0])
        month=int(elems[1])
        day=int(elems[2])
        
        self.intdate=datetime.date(year,month,day)
        self.day= self.intdate.day
        self.month=self.intdate.month
        self.weekday=self.intdate.weekday()
        self.year=self.intdate.year
    
    def __hash__(self):
        return self.intdate.__hash__()
    def __str__(self):
        return self.intdate.__str__()
    def __add__(self,days):
        res=self.intdate+datetime.timedelta(days)
        return rdate(res.__str__())
    def __eq__(self,other):
        return self.intdate==other.intdate
    def __ge__(self,other):
        return self.intdate>=other.intdate
    def __gt__ (self,other):
        return self.intdate>other.intdate
    def __le__ (self,other):
        return self.intdate<=other.intdate
    def __lt__ (self,other):
        return self.intdate<other.intdate
    def __ne__(self,other):
        return self.intdate!=other.intdate
    def __sub__ (self,other):
        return (self.intdate-other.intdate).days
def isDate(date):
    sep=('-','/','\\')
    splitter=None
    for i in sep:
        if i in date:
            splitter=i
            break;
    elems=date.split(splitter)
    if len(elems)!=3:
        return False #Wrong number of elements
    year=elems[0]
    month=elems[1]
    day=elems[2]
    if not (year.isdigit() and month.isdigit() and day.isdigit()):
        return False
    year=int(year)
    month=int(month)
    day=int(day)
    
    if year<datetime.MINYEAR or year>datetime.MAXYEAR:
        return False
    if month<1 or month>12:
        return False
    if day<1 or day >31:
        return False
    return True