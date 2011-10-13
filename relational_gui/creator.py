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
    def __init__(self,rel=None):
        QtGui.QDialog.__init__(self)
        
        self.setSizeGripEnabled(True)
        self.result_relation=None
        self.rel=rel
    def setUi(self,ui):
        self.ui=ui
        self.table=self.ui.table
        
        if self.rel==None:
            self.setup_empty()
        else:
            self.setup_replation(rel)
    def setup_relation(rel):
        pass
    def setup_empty(self):
        self.table.insertColumn(0)
        self.table.insertColumn(0)
        self.table.insertRow(0)
        self.table.insertRow(0)
        
        i00=QtGui.QTableWidgetItem()
        i01=QtGui.QTableWidgetItem()
        i10=QtGui.QTableWidgetItem()
        i11=QtGui.QTableWidgetItem()
        i00.setText('Field name 1')
        i01.setText('Field name 2')
        i10.setText('Value 1')
        i11.setText('Value 2')
        
        self.table.setItem (0,0,i00)
        self.table.setItem (0,1,i01)
        self.table.setItem (1,0,i10)
        self.table.setItem (1,1,i11)

    
    
    
    def accept(self):
        QtGui.QDialog.accept(self)
        pass
    def reject(self):
        self.result_relation=None
        QtGui.QDialog.reject(self)
        pass
    def addColumn(self):
        self.table.insertColumn(self.table.columnCount())
        pass
    def addRow(self):
        self.table.insertRow(1)
        pass
    def deleteColumn(self):
        if self.table.columnCount()>1:
            self.table.removeColumn(self.table.currentColumn())
        pass
    def deleteRow(self):
        if self.table.rowCount()>2:
            self.table.removeRow(self.table.currentRow())
        pass



def editRelation(rel=None):
    ui = rel_edit.Ui_Dialog()
    Form = creatorForm(rel)

    ui.setupUi(Form)
    Form.setUi(ui)
    
    Form.exec_()
    return Form.result_relation
    

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    print editRelation()
