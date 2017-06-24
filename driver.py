#!/usr/bin/env python3
# Relational
# Copyright (C) 2010-2017  Salvo "LtWorf" Tomaselli
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

import os
from sys import exit
import sys
import traceback

from relational import relation, parser, optimizer
from xtermcolor import colorize


COLOR_RED = 0xff0000
COLOR_GREEN = 0x00ff00
COLOR_MAGENTA = 0xff00ff
COLOR_CYAN = 0x00ffff

print(relation)

rels = {}
examples_path = 'samples/'
tests_path = 'tests_dir/'


def readfile(fname):
    '''Reads a file as string and returns its content'''
    with open(fname, encoding='utf-8') as fd:
        expr = fd.read()
        return expr


def load_relations():
    '''Loads all the relations present in the directory indicated in the
    examples_path variable and stores them in the rels dictionary'''
    print("Loading relations")
    for i in os.listdir(examples_path):
        if i.endswith('.csv'):  # It's a relation, loading it

            # Naming the relation
            relname = i[:-4]

            print ("Loading relation %s with name %s..." % (i, relname))

            rels[relname] = relation.relation('%s%s' % (examples_path, i))
            print('done')


def execute_tests():

    py_bad = 0
    py_good = 0
    py_tot = 0
    q_bad = 0
    q_good = 0
    q_tot = 0
    ex_bad = 0
    ex_good = 0
    ex_tot = 0
    f_tot = 0
    f_good = 0
    f_bad = 0

    for i in os.listdir(tests_path):
        if i.endswith('.query'):
            q_tot += 1
            if run_test(i[:-6]):
                q_good += 1
            else:
                q_bad += 1
        elif i.endswith('.python'):
            py_tot += 1
            if run_py_test(i[:-7]):
                py_good += 1
            else:
                py_bad += 1
        elif i.endswith('.py'):
            ex_tot += 1
            if run_exec_test(i[:-3]):
                ex_good += 1
            else:
                ex_bad += 1
        elif i.endswith('.fail'):
            f_tot += 1
            if run_fail_test(i[:-5]):
                f_good += 1
            else:
                f_bad += 1

    print (colorize("Resume of the results", COLOR_CYAN))

    print (colorize("Query tests", COLOR_MAGENTA))
    print ("Total test count: %d" % q_tot)
    print ("Passed tests: %d" % q_good)
    if q_bad > 0:
        print (colorize("Failed tests count: %d" % q_bad, COLOR_RED))

    print (colorize("Python tests", COLOR_MAGENTA))
    print ("Total test count: %d" % py_tot)
    print ("Passed tests: %d" % py_good)
    if py_bad > 0:
        print (colorize("Failed tests count: %d" % py_bad, COLOR_RED))

    print (colorize("Execute Python tests", COLOR_MAGENTA))
    print ("Total test count: %d" % ex_tot)
    print ("Passed tests: %d" % ex_good)
    if ex_bad > 0:
        print (colorize("Failed tests count: %d" % ex_bad, COLOR_RED))

    print (colorize("Execute fail tests", COLOR_MAGENTA))
    print ("Total test count: %d" % f_tot)
    print ("Passed tests: %d" % f_good)
    if f_bad > 0:
        print (colorize("Failed tests count: %d" % f_bad, COLOR_RED))

    print (colorize("Total results", COLOR_CYAN))
    if f_bad + q_bad + py_bad + ex_bad == 0:
        print (colorize("No failed tests", COLOR_GREEN))
        return 0
    else:
        print (colorize("There are %d failed tests" %
               (f_bad + py_bad + q_bad + ex_bad), COLOR_RED))
        return 1


def run_exec_test(testname):
    '''Runs a python test, which executes code directly rather than queries'''
    print ("Running python test: " + colorize(testname, COLOR_MAGENTA))

    glob = rels.copy()
    exp_result = {}

    expr = readfile('%s%s.py' % (tests_path, testname))

    try:
        exec(expr, glob)  # Evaluating the expression
        print (colorize('Test passed', COLOR_GREEN))
        return True
    except Exception as e:
        print (colorize('ERROR', COLOR_RED))
        print (colorize('=====================================', COLOR_RED))
        traceback.print_exc(file=sys.stdout)
        print (colorize('=====================================', COLOR_RED))
        return False


def run_py_test(testname):
    '''Runs a python test, which evaluates expressions directly rather than queries'''
    print ("Running expression python test: " +
           colorize(testname, COLOR_MAGENTA))

    try:

        expr = readfile('%s%s.python' % (tests_path, testname))
        result = eval(expr, rels)

        expr = readfile('%s%s.result' % (tests_path, testname))
        exp_result = eval(expr, rels)

        if result == exp_result:
            print (colorize('Test passed', COLOR_GREEN))
            return True
    except:
        pass

    print (colorize('ERROR', COLOR_RED))
    print (colorize('=====================================', COLOR_RED))
    print ("Expected %s" % exp_result)
    print ("Got %s" % result)
    print (colorize('=====================================', COLOR_RED))
    return False

def run_fail_test(testname):
    '''Runs a test, which executes a query that is supposed to fail'''
    print ("Running fail test: " + colorize(testname, COLOR_MAGENTA))

    query = readfile('%s%s.fail' % (tests_path, testname)).strip()
    test_succeed = True

    try:
        expr = parser.parse(query)
        expr(rels)
        test_succeed = False
    except:
        pass

    try:
        o_query = optimizer.optimize_all(query, rels)
        o_expr = parser.parse(o_query)
        o_expr(rels)
        test_succeed = False
    except:
        pass

    try:
        c_expr = parser.tree(query).toCode()
        eval(c_expr, rels)
        test_succeed = False
    except:
        pass

    if test_succeed:
        print (colorize('Test passed', COLOR_GREEN))
    else:
        print (colorize('Test failed (by not raising any exception)', COLOR_RED))
    return test_succeed

def run_test(testname):
    '''Runs a specific test executing the file
    testname.query
    and comparing the result with
    testname.result
    The query will be executed both unoptimized and
    optimized'''
    print ("Running test: " + colorize(testname, COLOR_MAGENTA))

    query = None
    expr = None
    o_query = None
    o_expr = None
    result_rel = None
    result = None
    o_result = None

    try:
        result_rel = relation.relation('%s%s.result' % (tests_path, testname))

        query = readfile('%s%s.query' % (tests_path, testname)).strip()
        o_query = optimizer.optimize_all(query, rels)

        expr = parser.parse(query)
        result = expr(rels)

        o_expr = parser.parse(o_query)
        o_result = o_expr(rels)

        c_expr = parser.tree(query).toCode()
        c_result = eval(c_expr, rels)

        if (o_result == result_rel) and (result == result_rel) and (c_result == result_rel):
            print (colorize('Test passed', COLOR_GREEN))
            return True
    except Exception as inst:
        traceback.print_exc(file=sys.stdout)
        print (inst)
        pass
    print (colorize('ERROR', COLOR_RED))
    print ("Query: %s -> %s" % (query, expr))
    print ("Optimized query: %s -> %s" % (o_query, o_expr))
    print (colorize('=====================================', COLOR_RED))
    print (colorize("Expected result", COLOR_GREEN))
    print (result_rel)
    print (colorize("Result", COLOR_RED))
    print (result)
    print (colorize("Optimized result", COLOR_RED))
    print (o_result)
    print (colorize("optimized result match %s" %
           str(result_rel == o_result), COLOR_MAGENTA))
    print (colorize("result match %s" %
           str(result == result_rel), COLOR_MAGENTA))
    print (colorize('=====================================', COLOR_RED))
    return False


if __name__ == '__main__':
    print ("-> Starting testsuite for relational")
    load_relations()
    print ("-> Starting tests")
    exit(execute_tests())
