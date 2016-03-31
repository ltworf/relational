# Relational
# Copyright (C) 2008-2015  Salvo "LtWorf" Tomaselli
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

from PyQt5 import QtGui, QtWidgets

from relational_gui import rel_edit
from relational import relation


class creatorForm(QtWidgets.QDialog):

    def __init__(self, rel=None):
        QtWidgets.QDialog.__init__(self)

        self.setSizeGripEnabled(True)
        self.result_relation = None
        self.rel = rel

    def setUi(self, ui):
        self.ui = ui
        self.table = self.ui.table

        if self.rel == None:
            self.setup_empty()
        else:
            self.setup_relation(self.rel)

    def setup_relation(self, rel):

        self.table.insertRow(0)

        for i in rel.header:
            item = QtWidgets.QTableWidgetItem()
            item.setText(i)
            self.table.insertColumn(self.table.columnCount())
            self.table.setItem(0, self.table.columnCount() - 1, item)

        for i in rel.content:
            self.table.insertRow(self.table.rowCount())
            for j in range(len(i)):
                item = QtWidgets.QTableWidgetItem()
                item.setText(i[j])
                self.table.setItem(self.table.rowCount() - 1, j, item)

        pass

    def setup_empty(self):
        self.table.insertColumn(0)
        self.table.insertColumn(0)
        self.table.insertRow(0)
        self.table.insertRow(0)

        i00 = QtWidgets.QTableWidgetItem()
        i01 = QtWidgets.QTableWidgetItem()
        i10 = QtWidgets.QTableWidgetItem()
        i11 = QtWidgets.QTableWidgetItem()
        i00.setText('Field name 1')
        i01.setText('Field name 2')
        i10.setText('Value 1')
        i11.setText('Value 2')

        self.table.setItem(0, 0, i00)
        self.table.setItem(0, 1, i01)
        self.table.setItem(1, 0, i10)
        self.table.setItem(1, 1, i11)

    def create_relation(self):
        h = (self.table.item(0, i).text()
             for i in range(self.table.columnCount()))

        try:
            header = relation.header(h)
        except Exception as e:
            QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("Form", "Error"), "%s\n%s" % (
                QtWidgets.QApplication.translate("Form", "Header error!"), e.__str__()))
            return None
        r = relation.relation()
        r.header = header

        for i in range(1, self.table.rowCount()):
            hlist = []
            for j in range(self.table.columnCount()):
                try:
                    hlist.append(self.table.item(i, j).text())
                except:
                    QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate(
                        "Form", "Error"), QtWidgets.QApplication.translate("Form", "Unset value in %d,%d!" % (i + 1, j + 1)))
                    return None
            r.insert(hlist)
        return r

    def accept(self):

        self.result_relation = self.create_relation()

        # Doesn't close the window in case of errors
        if self.result_relation != None:
            QtWidgets.QDialog.accept(self)

    def reject(self):
        self.result_relation = None
        QtWidgets.QDialog.reject(self)

    def addColumn(self):
        self.table.insertColumn(self.table.columnCount())

    def addRow(self):
        self.table.insertRow(1)

    def deleteColumn(self):
        if self.table.columnCount() > 1:
            self.table.removeColumn(self.table.currentColumn())

    def deleteRow(self):
        if self.table.rowCount() > 2:
            self.table.removeRow(self.table.currentRow())


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
    r = relation.relation(
        "/home/salvo/dev/relational/trunk/samples/people.csv")
    print (edit_relation(r))
