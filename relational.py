#!/usr/bin/env python
# coding=UTF-8
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

import sys
from PyQt4 import QtCore, QtGui
import parser
import relation
import maingui

version="0.8"

if __name__ == "__main__":
    if len (sys.argv) > 1 and sys.argv[1] == "-v":
        print version
        sys.exit(0)
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    
    ui = maingui.Ui_Form()
    ui.setupUi(Form)
    Form.show()
    
    sys.exit(app.exec_())
