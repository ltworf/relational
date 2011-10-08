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
# Stuff non-related to relational algebra, but used for maintenance.

import httplib
import urllib

def send_survey(data):
    '''Sends the survey. Data must be a dictionary.
    returns the http response'''
    
    post=''
    for i in data.keys():
        post+='%s: %s\n' %(i,data[i])

    #sends the string
    params = urllib.urlencode({'survey':post})
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    connection = httplib.HTTPConnection('galileo.dmi.unict.it')
    connection.request("POST","/~ltworf/survey.php",params,headers)
    return connection.getresponse()


def check_latest_version():
    '''Returns the latest version available.
    Heavely dependent on server and server configurations
    not granted to work forever.'''
    connection = httplib.HTTPConnection('galileo.dmi.unict.it')
    connection.request("GET","/svn/relational/tags/")
    r=connection.getresponse()
    
    #html
    s=r.read()
    if len(s)==0:
        return None
    
    l= s[s.find('<ul>')+4:s.find('</ul>')].split('\n')
    l.sort()
    a=l[len(l)-1]
    
    s=a.find('"')+1
    return a[s:a.find('"',s)-1]