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
import sip
from PyQt4 import QtCore, QtGui
from relational_gui import maingui, about
from relational import relation, parser

version="0.11"
about.version=version

if __name__ == "__main__":
    if len (sys.argv) > 1 and sys.argv[1] == "-v":
        
        print "Relational"
        print "This program comes with ABSOLUTELY NO WARRANTY."
        print "This is free software, and you are welcome to redistribute it"
        print "under certain conditions."
        print "For details see the GPLv3 Licese."
        print
        print "Version: %s"%version
        sys.exit(0)
        
    try:
        import psyco
        psyco.full()
    except:
        pass
    
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    
    if os.name=='nt':
        Form.setFont(QtGui.QFont("Dejavu Sans Bold"))
    
    ui = maingui.Ui_Form()
    ui.setupUi(Form)
    
    for i in range(1,len(sys.argv)):        
        f=sys.argv[i].split('/')
        defname=f[len(f)-1].lower()
        if (defname.endswith(".csv") or defname.endswith(".tlb")): #removes the extension
            defname=defname[:-4]
        print 'Loading file "%s" with name "%s"' % (sys.argv[i],defname)
        ui.loadRelation(sys.argv[i],defname)

    
    Form.show()
    
    sys.exit(app.exec_())
