# Relational
# Copyright (C) 2008-2017  Salvo "LtWorf" Tomaselli
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
import pickle
import base64
from typing import Optional, Tuple

from relational.relation import Relation
from relational import parser
from relational.rtypes import is_valid_relation_name


SWEARWORDS = {'fuck', 'shit', 'suck', 'merda', 'mierda', 'merde'}


def send_survey(data) -> int:
    '''Sends the survey. Data must be a dictionary.
    returns the http response.

    returns 0 in case of error
    returns -1 in case of swearwords'''

    post = ''
    for i in data.keys():
        post += '%s: %s\n' % (i, data[i].strip())

    lowpost = post.lower()
    for i in SWEARWORDS:
        if i in lowpost:
            return -1

    # sends the string
    params = urllib.parse.urlencode({'survey': post})
    headers = {"Content-type":
               "application/x-www-form-urlencoded", "Accept": "text/plain"}
    connection = http.client.HTTPConnection('feedback-ltworf.appspot.com')
    try:
        connection.request("POST", "/feedback/relational", params, headers)
        return connection.getresponse().status
    except:
        return 0


def check_latest_version() -> Optional[str]:
    '''Returns the latest version available.
    Heavely dependent on server and server configurations
    not granted to work forever.'''
    connection = http.client.HTTPConnection('feedback-ltworf.appspot.com')
    try:
        connection.request("GET", "/version/relational")
        r = connection.getresponse()
    except:
        return None

    # html
    s = r.read()
    if len(s) == 0:
        return None
    return s.decode().strip()


class UserInterface:

    '''It is used to provide services to the user interfaces, in order to
    reduce the amount of duplicated code present in different user interfaces.
    '''

    def __init__(self) -> None:
        self.session_reset()

    def load(self, filename: str, name: str) -> None:
        '''Loads a relation from file, and gives it a name to
        be used in subsequent queries.'''
        rel = Relation(filename)
        self.set_relation(name, rel)

    def unload(self, name: str) -> None:
        '''Unloads an existing relation.'''
        del self.relations[name]

    def store(self, filename: str, name: str) -> None:
        '''Stores a relation to file.'''
        raise Exception('Not implemented')

    def session_dump(self, filename: Optional[str] = None) -> Optional[str]:
        '''
        Dumps the session.

        If a filename is specified, the session is dumped
        inside the file, and None is returned.

        If no filename is specified, the session is returned
        as string.
        '''
        if filename:
            with open(filename, 'wb') as f:
                pickle.dump(self.relations, f)
                return None
        return base64.b64encode(pickle.dumps(self.relations)).decode()

    def session_restore(self, session: Optional[bytes] = None, filename: Optional[str] = None) -> None:
        '''
        Restores a session.

        Either from bytes or from a file.
        '''
        if session:
            try:
                self.relations = pickle.loads(base64.b64decode(session))
            except:
                pass
        elif filename:
            with open(filename, 'rb') as f:
                self.relations = pickle.load(f)

    def session_reset(self) -> None:
        '''
        Resets the session to a clean one
        '''
        self.relations = {}

    def get_relation(self, name: str) -> Relation:
        '''Returns the relation corresponding to name.'''
        return self.relations[name]

    def set_relation(self, name: str, rel: Relation) -> None:
        '''Sets the relation corresponding to name.'''
        if not is_valid_relation_name(name):
            raise Exception('Invalid name for destination relation')
        self.relations[name] = rel

    def suggest_name(self, filename: str) -> Optional[str]:
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

    def execute(self, query: str, relname: str = 'last_') -> Relation:
        '''Executes a query, returns the result and if
        relname is not None, adds the result to the
        dictionary, with the name given in relname.'''
        if not is_valid_relation_name(relname):
            raise Exception('Invalid name for destination relation')

        expr = parser.parse(query)
        result = expr(self.relations)
        self.relations[relname] = result
        return result

    @staticmethod
    def split_query(query: str, default_name='last_') -> Tuple[str, str]:
        '''
        Accepts a query which might have an initial value
        assignment
        a = query

        Returns a tuple with

        result_name, query
        '''
        sq = query.split('=', 1)
        if len(sq) == 2 and is_valid_relation_name(sq[0].strip()):
            default_name = sq[0].strip()
            query = sq[1].strip()
        return default_name, query

    def multi_execute(self, query: str) -> Relation:
        '''Executes multiple queries, separated by \n

        They can have a syntax of
        [varname =] query
        to assign the result to a new relation
        '''
        r = Relation()
        queries = query.split('\n')
        for query in queries:
            if query.strip() == '':
                continue

            relname, query = self.split_query(query)

            try:
                r = self.execute(query, relname)
            except Exception as e:
                raise Exception('Error in query: %s\n%s' % (
                    query,
                    str(e)
                ))
        return r
