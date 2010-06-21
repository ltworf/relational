# -*- coding: utf-8 -*-
# coding=UTF-8
# Relational
# Copyright (C) 2010  Salvo "LtWorf" Tomaselli
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
# Initial readline code from http://www.doughellmann.com/PyMOTW/readline/index.html

import readline
import logging
import os.path
import os
import sys

from relational import relation, parser, optimizer

class SimpleCompleter(object):
    '''Handles completion'''
    
    def __init__(self, options):
        '''Takes a list of valid completion options'''
        self.options = sorted(options)
        return
    
    def add_completion(self,option):
        '''Adds one string to the list of the valid completion options'''
        if option not in self.options:
            self.options.append(option)
            self.options.sort()
    
    def remove_completion(self,option):
        '''Removes one completion from the list of the valid completion options'''
        #//TODO
        pass
        
    def complete(self, text, state):
        #print test, state
        
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s 
                                for s in self.options
                                if s and s.startswith(text)]
                                
                #Add the completion for files here
                try:
                    listf=os.listdir(os.path.dirname(text))
                except:
                    listf=os.listdir('.')
                
                for i in listf:
                    if i.startswith(text):
                        if os.path.isdir(i):
                            i+="/"
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


relations={}
completer=SimpleCompleter(['LIST','LOAD ','UNLOAD ','HELP ','QUIT','SAVE ','_PRODUCT ','_UNION ','_INTERSECTION ','_DIFFERENCE ','_JOIN ','_LJOIN ','_RJOIN ','_FJOIN ','_PROJECTION ','_RENAME_TO ','_SELECTION ','_RENAME '])


def load_relation(filename,defname=None):
    if not os.path.isfile(filename):
        print >> sys.stderr, "%s is not a file" % filename
        return None

    f=filename.split('/')
    if defname==None:
        defname=f[len(f)-1].lower()
        if (defname.endswith(".csv") or defname.endswith(".tlb")): #removes the extension
            defname=defname[:-4]

    try:
        relations[defname]=relation.relation(filename)
        
        completer.add_completion(defname)
        print "Loaded relation %s"% defname
        return defname
    except Exception, e:
        print e
        return None

def help(command):
    '''Prints help on the various functions'''
    p=command.split(' ',1)
    if len(p)==1:
        print 'HELP command'
        print 'To execute a query:\n[relation =] query\nIf the 1st part is omitted, the result will be stored in the relation last_.'
        print 'To prevent from printing the relation, append a ; to the end of the query.'
        print 'To insert relational operators, type _OPNAME, they will be internally replaced with the correct symbol.'
        return
    cmd=p[1]
    
    if cmd=='QUIT':
        print 'Quits the program'
    elif cmd=='LIST':
        print "Lists the relations loaded"
    elif cmd=='LOAD':
        print "LOAD filename [relationame]"
        print "Loads a relation into memory"
    elif cmd=='UNLOAD':
        print "UNLOAD relationame"
        print "Unloads a relation from memory"
    elif cmd=='SAVE':
        print "SAVE filename relationame"
        print "Saves a relation in a file"
    elif cmd=='HELP':
        print "Prints the help on a command"
    else:
        print "Unknown command: %s" %cmd
        

def exec_line(command):
    command=command.strip()
    if command=='QUIT':
        sys.exit(0)
    elif command.startswith('HELP'):
        help(command)
    elif command=='LIST':         #Lists all the loaded relations
        for i in relations:
            if not i.startswith('_'):
                print i
    elif command.startswith('LOAD '):      #Loads a relation
        pars=command.split(' ')
        filename=pars[1]
        if len(pars)>2:
            defname=pars[2]
        else:
            defname=None
        load_relation(filename,defname)
         
    elif command=='UNLOAD ':
        #//TODO
        pass
    #elif command=='SAVE': //TODO
    else:
        exec_query( command)

def replacements(query):
    '''This funcion replaces ascii easy operators with the correct ones'''
    query=query.replace(    '_PRODUCT'          ,   '*')
    query=query.replace(    '_UNION'            ,   'ᑌ')
    query=query.replace(    '_INTERSECTION'     ,   'ᑎ')
    query=query.replace(    '_DIFFERENCE'       ,   '-')
    query=query.replace(    '_JOIN'             ,   'ᐅᐊ')
    query=query.replace(    '_LJOIN'            ,   'ᐅLEFTᐊ')
    query=query.replace(    '_RJOIN'            ,   'ᐅRIGHTᐊ')
    query=query.replace(    '_FJOIN'            ,   'ᐅFULLᐊ')
    query=query.replace(    '_PROJECTION'       ,   'π')
    query=query.replace(    '_RENAME_TO'        ,   '➡')
    query=query.replace(    '_SELECTION'        ,   'σ')
    query=query.replace(    '_RENAME'           ,   'ρ')
    return query

def exec_query(command):
    '''This function executes a query and prints the result on the screen'''
    
    #If it terminates with ; doesn't print the result
    if command.endswith(';'):
        command=command[:-1]
        printrel=False
    else:
        printrel=True
    
    #Performs replacements for weird operators
    command=replacements(command)
    
    #Finds the name in where to save the query
    parts=command.split('=',1)
    
    if len(parts)>1:
        assignment=True
        for i in parser.op_functions:
            if i in parts[0]:
                #If we are here, there is no explicit assignment
                assignment=False
        if assignment:
            relname=parts[0]
            query=parts[1]
        else:
            relname='last_'
            query=command
    else:
        relname='last_'
        query=command
    
    #Execute query
    try:
        pyquery=parser.parse(query)
        result=eval(pyquery,relations)
        print "-> query: %s" % pyquery
        
        if printrel:
            print
            print result
    
        relations[relname]=result
    
        completer.add_completion(relname)
    except Exception, e:
        print e
    
def main(files=[]):
    
    for i in files:
        load_relation(i)
    
    readline.set_completer(completer.complete)

    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set editing-mode emacs')

    while True:
        try:
            line = raw_input('> ')
            if isinstance(line,str) and len(line)>0:
                exec_line(line)
        except EOFError:
            print
            sys.exit(0)



if __name__ == "__main__":
    main()