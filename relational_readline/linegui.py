# Relational
# Copyright (C) 2010-2020  Salvo "LtWorf" Tomaselli
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
# Initial readline code from
# http://www.doughellmann.com/PyMOTW/readline/index.html

import readline
import logging
import os.path
import os
import sys
from typing import Optional

from relational import relation, parser, rtypes
from relational import maintenance
from xtermcolor import colorize

PROMPT_COLOR = 0xffff00
ERROR_COLOR = 0xff0000
COLOR_GREEN = 0x00ff00

TTY = os.isatty(0) and os.isatty(1)

version = ''


def printtty(*args, **kwargs):
    '''
    Prints only if stdout and stdin are a tty
    '''
    if TTY:
        print(*args, **kwargs)


class SimpleCompleter:

    '''Handles completion'''

    def __init__(self, options) -> None:
        '''Takes a list of valid completion options'''
        self.options = sorted(options)

    def add_completion(self, option):
        '''Adds one string to the list of the valid completion options'''
        if option not in self.options:
            self.options.append(option)
            self.options.sort()

    def remove_completion(self, option):
        '''Removes one completion from the list of the valid completion options'''
        if option in self.options:
            self.options.remove(option)

    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s
                                for s in self.options
                                if s and s.startswith(text)]

                # Add the completion for files here
                try:
                    d = os.path.dirname(text)
                    listf = os.listdir(d)

                    d += "/"
                except:
                    d = ""
                    listf = os.listdir('.')

                for i in listf:
                    i = (d + i).replace('//', '/')
                    if i.startswith(text):
                        if os.path.isdir(i):
                            i = i + "/"
                        self.matches.append(i)

                logging.debug('%s matches: %s', repr(text), self.matches)
            else:
                self.matches = self.options[:]
                logging.debug('(empty input) matches: %s', self.matches)

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        logging.debug('complete(%s, %s) => %s',
                      repr(text), state, repr(response))
        return response


relations = {}
completer = SimpleCompleter(
    ['SURVEY', 'LIST', 'LOAD ', 'UNLOAD ', 'HELP ', 'QUIT', 'SAVE ', '_PRODUCT ', '_UNION ', '_INTERSECTION ',
     '_DIFFERENCE ', '_JOIN ', '_LJOIN ', '_RJOIN ', '_FJOIN ', '_PROJECTION ', '_RENAME_TO ', '_SELECTION ', '_RENAME ', '_DIVISION '])


def load_relation(filename: str, defname:Optional[str]=None) -> Optional[str]:
    '''
    Loads a relation into the set. Defname is the given name
    to the relation.

    Returns the name to the relation, or None if it was
    not loaded.
    '''
    if not os.path.isfile(filename):
        print(colorize(
            "%s is not a file" % filename, ERROR_COLOR), file=sys.stderr)
        return None

    if defname is None:
        f = filename.split('/')
        defname = f[-1].lower()
        if defname.endswith(".csv"):  # removes the extension
            defname = defname[:-4]

    if not rtypes.is_valid_relation_name(defname):
        print(colorize(
            "%s is not a valid relation name" % defname, ERROR_COLOR), file=sys.stderr)
        return None
    try:
        relations[defname] = relation.Relation(filename)

        completer.add_completion(defname)
        printtty(colorize("Loaded relation %s" % defname, COLOR_GREEN))
        return defname
    except Exception as e:
        print(colorize(str(e), ERROR_COLOR), file=sys.stderr)
        return None


def survey() -> None:
    '''performs a survey'''
    post = {'software': 'Relational algebra (cli)', 'version': version}

    fields = ('System', 'Country', 'School', 'Age', 'How did you find',
              'email (only if you want a reply)', 'Comments')
    for i in fields:
        a = input('%s: ' % i)
        post[i] = a
    response = maintenance.send_survey(post)
    if response == -1:
        print('Yeah, not sending that.')


def help(command: str) -> None:
    '''Prints help on the various functions'''
    p = command.split(' ', 1)
    if len(p) == 1:
        print(
            'HELP command\n'
            'To execute a query:\n'
            '[relation =] query\n'
            'If the 1st part is omitted, the result will be stored in the relation last_.\n'
            'To prevent from printing the relation, append a ; to the end of the query.\n'
            'To insert relational operators, type _OPNAME, they will be internally replaced with the correct symbol.\n'
            'Rember: completion is enabled and can be very helpful if you can\'t remember something.'
        )
        return
    cmd = p[1]

    cmdhelp = {
        'QUIT': 'Quits the program',
        'LIST': 'Lists the relations loaded',
        'LOAD': 'LOAD filename [relationame]\nLoads a relation into memory',
        'UNLOAD': 'UNLOAD relationame\nUnloads a relation from memory',
        'SAVE': 'SAVE filename relationame\nSaves a relation in a file',
        'HELP': 'Prints the help on a command',
        'SURVEY': 'Fill and send a survey',
    }
    print(cmdhelp.get(cmd, 'Unknown command: %s' % cmd))


def exec_line(command: str) -> None:
    '''
    Executes a line.

    If it's a command, runs it, if it's a query runs it too
    '''
    command = command.strip()

    if command.startswith(';'):
        return
    elif command == 'QUIT':
        sys.exit(0)
    elif command.startswith('HELP'):
        help(command)
    elif command == 'LIST':  # Lists all the loaded relations
        for i in relations:
            if not i.startswith('_'):
                print(i)
    elif command == 'SURVEY':
        survey()
    elif command.startswith('LOAD '):  # Loads a relation
        pars = command.split(' ')
        if len(pars) == 1:
            print(colorize("Missing parameter", ERROR_COLOR))
            return

        filename = pars[1]
        if len(pars) > 2:
            defname = pars[2]
        else:
            defname = None
        load_relation(filename, defname)

    elif command.startswith('UNLOAD '):
        pars = command.split(' ')
        if len(pars) < 2:
            print(colorize("Missing parameter", ERROR_COLOR))
            return
        if pars[1] in relations:
            del relations[pars[1]]
            completer.remove_completion(pars[1])
        else:
            print(colorize("No such relation %s" % pars[1], ERROR_COLOR))
    elif command.startswith('SAVE '):
        pars = command.split(' ')
        if len(pars) != 3:
            print(colorize("Missing parameter", ERROR_COLOR))
            return

        filename = pars[1]
        defname = pars[2]

        if defname not in relations:
            print(colorize("No such relation %s" % defname, ERROR_COLOR))
            return
        try:
            relations[defname].save(filename)
        except Exception as e:
            print(colorize(e, ERROR_COLOR))
    else:
        exec_query(command)


def replacements(query: str) -> str:
    '''This funcion replaces ascii easy operators with the correct ones'''
    rules = (
        ('_PRODUCT', parser.PRODUCT),
        ('_UNION', parser.UNION),
        ('_INTERSECTION', parser.INTERSECTION),
        ('_DIFFERENCE', parser.DIFFERENCE),
        ('_JOIN', parser.JOIN),
        ('_LJOIN', parser.JOIN_LEFT),
        ('_RJOIN', parser.JOIN_RIGHT),
        ('_FJOIN', parser.JOIN_FULL),
        ('_PROJECTION', parser.PROJECTION),
        ('_RENAME_TO', parser.ARROW),
        ('_SELECTION', parser.SELECTION),
        ('_RENAME', parser.RENAME),
        ('_DIVISION', parser.DIVISION),
    )
    for asciiop, op in rules:
        query = query.replace(asciiop, op)
    return query


def exec_query(command: str) -> None:
    '''
    Executes a query and prints the result on the screen
    if the command terminates with ";" the result will not be printed.

    Updates the set of relations.
    '''

    # If it terminates with ; doesn't print the result
    if command.endswith(';'):
        command = command[:-1]
        printrel = False
    else:
        printrel = True

    # Performs replacements for weird operators
    command = replacements(command)

    # Finds the name in where to save the query
    parts = command.split('=', 1)
    relname,query = maintenance.UserInterface.split_query(command)

    # Execute query
    try:
        pyquery = parser.parse(query)
        result = pyquery(relations)

        printtty(colorize("-> query: %s" % pyquery, COLOR_GREEN))

        if printrel:
            print()
            print(result)

        relations[relname] = result

        completer.add_completion(relname)
    except Exception as e:
        print(colorize(str(e), ERROR_COLOR))


def main(files=[]):
    printtty(colorize('> ', PROMPT_COLOR) + "; Type HELP to get the HELP")
    printtty(colorize('> ', PROMPT_COLOR) +
           "; Completion is activated using the tab (if supported by the terminal)")

    for i in files:
        load_relation(i)

    readline.set_completer(completer.complete)

    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode emacs')
    readline.set_completer_delims(" ")

    while True:
        try:
            line = input(colorize('> ' if TTY else '', PROMPT_COLOR))
            if isinstance(line, str) and len(line) > 0:
                exec_line(line)
        except KeyboardInterrupt:
            if TTY:
                print('^C\n')
                continue
            else:
                break
        except EOFError:
            printtty()
            sys.exit(0)


if __name__ == "__main__":
    main()
