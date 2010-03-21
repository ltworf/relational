#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding=UTF-8
# Relational
# Copyright (C) 2008  Salvo "LtWorf" Tomaselli
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

import sys
import os
import getopt
from relational import relation, parser
version="0.11"


def printver():
    print "Relational"
    print "This program comes with ABSOLUTELY NO WARRANTY."
    print "This is free software, and you are welcome to redistribute it"
    print "under certain conditions."
    print "For details see the GPLv3 Licese."
    print
    print "Version: %s"%version
    sys.exit(0)

def printhelp(code=0):
    print "Relational"
    print
    print "Usage: %s [options] [files]" % sys.argv[0]
    print 
    print "  -v            Print version and exits"
    print "  -h            Print this help and exits"
    print "  -q            Uses QT user interface (default)"
    print "  -c            Uses curses user interface"
    sys.exit(code)

if __name__ == "__main__":
    x11=True #Will try to use the x11 interface
    
    #Try to run the psyco optimizer
    try:
        import psyco
        psyco.full()
    except:
        pass

        
    #Getting command line
    try:
        switches,files=getopt.getopt(sys.argv[1:],"vhqc")
    except:
        printhelp(1)
        
    for i in switches:
        if i[0]=='-v':
            printver()
        elif i[0]=='-h':
            printhelp()
        elif i[0]=='-q':
            x11=True
        elif i[0]=='-c':
            x11=False
    
    
    if x11:
        import sip
        from PyQt4 import QtCore, QtGui
        from relational_gui import maingui, about
        about.version=version

        app = QtGui.QApplication(sys.argv)
        Form = QtGui.QWidget()
    
        if os.name=='nt':
            Form.setFont(QtGui.QFont("Dejavu Sans Bold"))
    
        ui = maingui.Ui_Form()
        ui.setupUi(Form)
    
        for i in range(len(files)):
            f=files[i].split('/')
            defname=f[len(f)-1].lower()
            if (defname.endswith(".csv") or defname.endswith(".tlb")): #removes the extension
                defname=defname[:-4]
            print 'Loading file "%s" with name "%s"' % (files[i],defname)
            ui.loadRelation(files[i],defname)

        Form.show()
        sys.exit(app.exec_())
    else: #TODO load with curses interface
        pass
