# -*- coding: utf-8 -*-
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

try:
    from PyQt4 import QtCore, QtGui
except:
    from PySide import QtCore, QtGui
    
from relational import relation
import rel_edit


class creatorForm(QtGui.QDialog):
    def __init__(self,ui,rel=None):
        QtGui.QDialog.__init__(self)
        self.setSizeGripEnabled(True)
        self.result_relation=None
    
    
    
    def accept(self):
        
        QtGui.QDialog.accept(self)
        pass
    def reject(self):
        pass




def editRelation(rel=None):
    ui = rel_edit.Ui_Dialog()
    Form = creatorForm(ui)


    ui.setupUi(Form)
    Form.exec_()
    return Form.result_relation
    

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    print editRelation()
