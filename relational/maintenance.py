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
import os.path

from relational.relation import relation
from relational import parser
from relational.rtypes import is_valid_relation_name


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
    return s.decode().strip()


class user_interface (object):

    '''It is used to provide services to the user interfaces, in order to
    reduce the amount of duplicated code present in different user interfaces.
    '''

    def __init__(self):
        self.relations = {}

    def load(self, filename, name):
        '''Loads a relation from file, and gives it a name to
        be used in subsequent queries.'''
        rel = relation(filename)
        self.set_relation(name, rel)

    def unload(self, name):
        '''Unloads an existing relation.'''
        del self.relations[name]

    def store(self, filename, name):
        '''Stores a relation to file.'''
        pass

    def get_relation(self, name):
        '''Returns the relation corresponding to name.'''
        return self.relations[name]

    def set_relation(self, name, rel):
        '''Sets the relation corresponding to name.'''
        if not is_valid_relation_name(name):
            raise Exception('Invalid name for destination relation')
        self.relations[name] = rel

    def suggest_name(self, filename):
        '''
        Returns a possible name for a relation, given
        a filename.

        If it is impossible to extract a possible name,
        returns None
        '''
        name = os.path.basename(filename).lower()
        if len(name) == 0:
            return None

        if (name.endswith(".csv")):  # removes the extension
            name = name[:-4]

        if not is_valid_relation_name(name):
            return None
        return name

    def execute(self, query, relname='last_'):
        '''Executes a query, returns the result and if
        relname is not None, adds the result to the
        dictionary, with the name given in relname.'''
        if not is_valid_relation_name(relname):
            raise Exception('Invalid name for destination relation')

        expr = parser.parse(query)
        result = expr(self.relations)
        self.relations[relname] = result
        return result

    def multi_execute(self, query):
        '''Executes multiple queries, separated by \n

        They can have a syntax of
        [varname =] query
        to assign the result to a new relation
        '''
        r = relation()
        queries = query.split('\n')
        for query in queries:
            if query.strip() == '':
                continue
            parts = query.split('=', 1)
            parts[0] = parts[0].strip()
            if len(parts) > 1 and is_valid_relation_name(parts[0]):
                relname, query = parts
            else:
                relname = 'last_'

            try:
                r = self.execute(query, relname)
            except Exception as e:
                raise Exception('Error in query: %s\n%s' % (
                    query,
                    str(e)
                ))
        return r
