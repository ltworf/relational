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

import compatibility
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
            self.setup_relation(self.rel)
    def setup_relation(self,rel):
        
        self.table.insertRow(0)
        
        for i in rel.header.attributes:
            item=QtGui.QTableWidgetItem()
            item.setText(i)
            self.table.insertColumn(self.table.columnCount())
            self.table.setItem(0,self.table.columnCount()-1,item)
            
        for i in rel.content:
            self.table.insertRow(self.table.rowCount())
            for j in range(len(i)):
                item=QtGui.QTableWidgetItem()
                item.setText(i[j])
                self.table.setItem(self.table.rowCount()-1,j,item)
            
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
    def create_relation(self):
        hlist=[]
        
        for i in range(self.table.columnCount()):
            hlist.append(compatibility.get_py_str(self.table.item(0,i).text()))
        try:
            header=relation.header(hlist)
        except Exception, e:
            QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Error"),"%s\n%s" % (QtGui.QApplication.translate("Form", "Header error!"),e.__str__())  )
            return None
        r=relation.relation()
        r.header=header
        
        for i in range(1,self.table.rowCount()):
            hlist=[]
            for j in range(self.table.columnCount()):
                try:
                    hlist.append(compatibility.get_py_str(self.table.item(i,j).text()))
                except:
                    QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Error"),QtGui.QApplication.translate("Form", "Unset value in %d,%d!"% (i+1,j+1))  )
                    return None
            r.content.add(tuple(hlist))
        return r
    
    def accept(self):
        
        self.result_relation=self.create_relation()
        
        #Doesn't close the window in case of errors
        if self.result_relation!=None:
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


def edit_relation(rel=None):
    '''Opens the editor for the given relation and returns a _new_ relation
    containing the new relation.
    If the user cancels, it returns None'''
    
    ui = rel_edit.Ui_Dialog()
    Form = creatorForm(rel)

    ui.setupUi(Form)
    Form.setUi(ui)
    
    Form.exec_()
    return Form.result_relation
    

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    r=relation.relation("/home/salvo/dev/relational/trunk/samples/people.csv")
    print edit_relation(r)
