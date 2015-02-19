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

import http.client
import urllib.parse

from relational import relation


def send_survey(data):
    '''Sends the survey. Data must be a dictionary.
    returns the http response'''

    post = ''
    for i in data.keys():
        post += '%s: %s\n' % (i, data[i])

    # sends the string
    params = urllib.parse.urlencode({'survey': post})
    headers = {"Content-type":
               "application/x-www-form-urlencoded", "Accept": "text/plain"}
    connection = http.client.HTTPConnection('feedback-ltworf.appspot.com')
    connection.request("POST", "/feedback/relational", params, headers)

    return connection.getresponse()


def check_latest_version():
    '''Returns the latest version available.
    Heavely dependent on server and server configurations
    not granted to work forever.'''
    connection = http.client.HTTPConnection('feedback-ltworf.appspot.com')
    connection.request("GET", "/version/relational")
    r = connection.getresponse()

    # html
    s = r.read()
    if len(s) == 0:
        return None
    return str(s.strip())


class interface (object):

    '''It is used to provide services to the user interfaces, in order to
    reduce the amount of duplicated code present in different user interfaces.
    '''

    def __init__(self):
        self.rels = {}

    def load(self, filename, name):
        '''Loads a relation from file, and gives it a name to
        be used in subsequent queries.'''
        pass

    def unload(self, name):
        '''Unloads an existing relation.'''
        pass

    def store(self, filename, name):
        '''Stores a relation to file.'''
        pass

    def get_relation(self, name):
        '''Returns the relation corresponding to name.'''
        pass

    def set_relation(self, name, rel):
        '''Sets the relation corresponding to name.'''
        pass

    def execute(self, query, relname='last_'):
        '''Executes a query, returns the result and if
        relname is not None, adds the result to the
        dictionary, with the name given in relname.'''
        pass
