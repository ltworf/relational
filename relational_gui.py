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
import os.path
import getopt
from relational import relation, parser
version="1.1"


def printver(exit=True):
    print "Relational %s" % version
    print "Copyright (C) 2008 Salvo 'LtWorf' Tomaselli."
    print
    print "This program comes with ABSOLUTELY NO WARRANTY."
    print "This is free software, and you are welcome to redistribute it"
    print "under certain conditions."
    print "For details see the GPLv3 Licese."
    print
    print "Written by Salvo 'LtWorf' Tomaselli <tiposchi@tiscali.it>"
    print
    print "http://galileo.dmi.unict.it/wiki/relational/"
    if exit:
        sys.exit(0)

def printhelp(code=0):
    print "Relational"
    print
    print "Usage: %s [options] [files]" % sys.argv[0]
    print 
    print "  -v            Print version and exits"
    print "  -h            Print this help and exits"
    
    if sys.argv[0].endswith('relational-cli'):
        print "  -q            Uses QT user interface"
        print "  -r            Uses readline user interface (default)"
    else:
        print "  -q            Uses QT user interface (default)"
        print "  -r            Uses readline user interface"
    sys.exit(code)

if __name__ == "__main__":
    if sys.argv[0].endswith('relational-cli'):
        x11=False
    else:
        x11=True #Will try to use the x11 interface
    
    #Getting command line
    try:
        switches,files=getopt.getopt(sys.argv[1:],"vhqr")
    except:
        printhelp(1)
        
    for i in switches:
        if i[0]=='-v':
            printver()
        elif i[0]=='-h':
            printhelp()
        elif i[0]=='-q':
            x11=True
        elif i[0]=='-r':
            x11=False
    
    if x11:
        
        pyqt=True
        
        try:
            from PyQt4 import QtGui
        except:
            print >> sys.stderr, "PyQt seems to be missing, trying to use Pyside"
            from PySide import QtCore, QtGui
            pyqt=False
        
        
        if pyqt:
            try:
                from relational_gui import maingui,guihandler, about, surveyForm
            except:
                print >> sys.stderr, "Module relational_gui is missing.\nPlease install relational package."
                sys.exit(3)
        else:
            try:
                from relational_pyside import maingui,guihandler, about, surveyForm
            except:
                print >> sys.stderr, "Module relational_pyside is missing.\nPlease install relational package."
                sys.exit(3)
        
            
        about.version=version
        surveyForm.version=version
        guihandler.version=version

        app = QtGui.QApplication(sys.argv)
        
        ui = maingui.Ui_MainWindow()
        Form = guihandler.relForm(ui)
    
        #if os.name=='nt':
        Form.setFont(QtGui.QFont("Dejavu Sans Bold"))
        
        ui.setupUi(Form)
    
        for i in range(len(files)):
            if not os.path.isfile(files[i]):
                print >> sys.stderr, "%s is not a file" % files[i]
                printhelp(12)
            f=files[i].split('/')
            defname=f[len(f)-1].lower()
            if defname.endswith(".csv"): #removes the extension
                defname=defname[:-4]
            print 'Loading file "%s" with name "%s"' % (files[i],defname)
            Form.loadRelation(files[i],defname)

        Form.show()
        sys.exit(app.exec_())
    else:
        printver(False)
        try:
            import relational_readline.linegui
        except:
            print >> sys.stderr, "Module relational_readline is missing.\nPlease install relational-cli package."
            sys.exit(3)
        relational_readline.linegui.version=version
        relational_readline.linegui.main(files)

