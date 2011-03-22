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
#
# Custom types for relational algebra.
# Purpose of this module is having the isFloat function and
# implementing dates to use in selection.

import datetime
import re

class rstring (str):
    '''String subclass with some custom methods'''
    def isInt(self):
        '''Returns true if the string represents an int number
        it only considers as int numbers the strings matching
        the following regexp:
        r'^[\+\-]{0,1}[0-9]+$'
        '''
        if re.match(r'^[\+\-]{0,1}[0-9]+$',self)==None:
            return False
        else:
            return True
    def isFloat(self):
        '''Returns true if the string represents a float number
        it only considers as float numbers, the strings matching
        the following regexp:
            r'^[\+\-]{0,1}[0-9]+(\.([0-9])+)?$'
        '''
        if re.match(r'^[\+\-]{0,1}[0-9]+(\.([0-9])+)?$',self)==None:
            return False
        else:
            return True
    
    def isDate(self):
        '''Returns true if the string represents a date,
        in the format YYYY-MM-DD. as separators '-' , '\', '/' are allowed.
        As side-effect, the date object will be stored for future usage, so
        no more parsings are needed
        '''
        try:
            return self._isdate
        except:
            pass
        
        r= re.match(r'^([0-9]{1,4})(\\|-|/)([0-9]{1,2})(\\|-|/)([0-9]{1,2})$',self)
        if r==None:
            self._isdate=False
            self._date=None
            return False
    
        try: #Any of the following operations can generate an exception, if it happens, we aren't dealing with a date
            year=int(r.group(1))
            month=int(r.group(3))
            day=int(r.group(5))
            d=datetime.date(year,month,day)
            self._isdate=True
            self._date=d
            return True
        except:
            self._isdate=False
            self._date=None
            return False

    def getDate(self):
        '''Returns the datetime.date object or None'''
        try:
            return self._date
        except:
            self.isDate()
            return self._date
class rdate (object):
    '''Represents a date'''
    def __init__(self,date):
        '''date: A string representing a date'''
        if not isinstance(date,rstring):
            date=rstring(date)
        
        self.intdate=date.getDate()
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


def is_valid_relation_name(name):
    '''Checks if a name is valid for a relation.
    Returns boolean'''
    if re.match(r'^[_a-zA-Z]+[_a-zA-Z0-9]*$',name)==None:
        return False
    else:
        return True