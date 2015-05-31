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
import sys
import os

from PyQt5 import QtCore, QtWidgets, QtWidgets

from relational import relation, parser, optimizer, rtypes

from relational_gui import about
from relational_gui import survey
from relational_gui import surveyForm
from relational_gui import maingui
from relational_gui import compatibility


class relForm(QtWidgets.QMainWindow):

    def __init__(self, ui):
        QtWidgets.QMainWindow.__init__(self)
        self.About = None
        self.Survey = None
        self.relations = {}  # Dictionary for relations
        self.undo = None  # UndoQueue for queries
        self.selectedRelation = None
        self.ui = ui
        self.qcounter = 1  # Query counter

        self.settings = QtCore.QSettings()

    def checkVersion(self):
        from relational import maintenance
        online = maintenance.check_latest_version()

        if online > version:
            r = QtWidgets.QApplication.translate(
                "Form", "New version available online: %s." % online)
        elif online == version:
            r = QtWidgets.QApplication.translate(
                "Form", "Latest version installed.")
        else:
            r = QtWidgets.QApplication.translate(
                "Form", "You are using an unstable version.")

        QtWidgets.QMessageBox.information(
            self, QtWidgets.QApplication.translate("Form", "Version"), r)

    def setMultiline(self, multiline):
        self.multiline = multiline
        self.settings.setValue('multiline', multiline)
        self.ui.lineExpressionFrame.setVisible(not multiline)
        self.ui.frmOptimizations.setVisible(not multiline)
        self.ui.frmMultiLine.setVisible(multiline)
        self.ui.actionMulti_line_mode.setChecked(multiline)

    def load_query(self, *index):
        self.ui.txtQuery.setText(self.savedQ.itemData(index[0]).toString())

    def undoOptimize(self):
        '''Undoes the optimization on the query, popping one item from the undo list'''
        if self.undo != None:
            self.ui.txtQuery.setText(self.undo)

    def optimize(self):
        '''Performs all the possible optimizations on the query'''
        self.undo = self.ui.txtQuery.text()  # Storing the query in undo list

        query = compatibility.get_py_str(self.ui.txtQuery.text())
        try:
            result = optimizer.optimize_all(query, self.relations)
            compatibility.set_utf8_text(self.ui.txtQuery, result)
        except Exception as e:
            QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("Form", "Error"), "%s\n%s" %
                                              (QtWidgets.QApplication.translate("Form", "Check your query!"), e.__str__()))

    def resumeHistory(self, item):
        itm = compatibility.get_py_str(item.text()).split(' = ', 1)
        compatibility.set_utf8_text(self.ui.txtResult, itm[0])
        compatibility.set_utf8_text(self.ui.txtQuery, itm[1])

    def _run_multiline(self):
        query = compatibility.get_py_str(self.ui.txtMultiQuery.toPlainText())
        self.settings.setValue('multiline/query', query)

        queries = query.split('\n')

        for query in queries:
            if query.strip() == '':
                continue

            parts = query.split('=', 1)
            parts[0] = parts[0].strip()
            if len(parts) > 1 and rtypes.is_valid_relation_name(parts[0].strip()):
                relname = parts[0].strip()
                query = parts[1]
            else:
                relname = 'last_'

            try:
                expr = parser.parse(query)
                result = eval(expr, self.relations)
                self.relations[relname] = result
            except Exception as e:
                print(str(e))
                QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("Form", "Error"), u"%s\n%s" %
                                              (QtWidgets.QApplication.translate("Form", "Check your query!"), str(e)))
                break
        self.updateRelations()  # update the list
        self.selectedRelation = result
        self.showRelation(self.selectedRelation)

    def execute(self):
        '''Executes the query'''
        if self.multiline:
            return self._run_multiline()

        #Single line query
        query = compatibility.get_py_str(self.ui.txtQuery.text())
        res_rel = compatibility.get_py_str(
            self.ui.txtResult.text())  # result relation's name

        if not rtypes.is_valid_relation_name(res_rel):
            QtWidgets.QMessageBox.information(self, QtWidgets.QApplication.translate(
                "Form", "Error"), QtWidgets.QApplication.translate("Form", "Wrong name for destination relation."))
            return

        try:
            # Converting string to utf8 and then from qstring to normal string
            expr = parser.parse(query)  # Converting expression to python code
            print (query, "-->", expr)  # Printing debug
            result = eval(expr, self.relations)  # Evaluating the expression

            self.relations[
                res_rel] = result  # Add the relation to the dictionary
            self.updateRelations()  # update the list
            self.selectedRelation = result
            self.showRelation(self.selectedRelation)
                              # Show the result in the table
        except Exception as e:
            print (str(e))
            QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("Form", "Error"), u"%s\n%s" %
                                              (QtWidgets.QApplication.translate("Form", "Check your query!"), str(e)))
            return

        # Adds to history
        item = u'%s = %s' % (compatibility.get_py_str(
            self.ui.txtResult.text()), compatibility.get_py_str(self.ui.txtQuery.text()))
        # item=item.decode('utf-8'))
        compatibility.add_list_item(self.ui.lstHistory, item)

        self.qcounter += 1
        compatibility.set_utf8_text(self.ui.txtResult, u"_last%d" %
                                    self.qcounter)  # Sets the result relation name to none

    def showRelation(self, rel):
        '''Shows the selected relation into the table'''
        self.ui.table.clear()

        if rel == None:  # No relation to show
            self.ui.table.setColumnCount(1)
            self.ui.table.headerItem().setText(0, "Empty relation")
            return
        self.ui.table.setColumnCount(len(rel.header.attributes))

        # Set content
        for i in rel.content:
            item = QtWidgets.QTreeWidgetItem()
            for j in range(len(i)):
                item.setText(j, i[j])
            self.ui.table.addTopLevelItem(item)

        # Sets columns
        for i in range(len(rel.header.attributes)):
            self.ui.table.headerItem().setText(i, rel.header.attributes[i])
            self.ui.table.resizeColumnToContents(
                i)  # Must be done in order to avoid  too small columns

    def printRelation(self, item):
        self.selectedRelation = self.relations[
            compatibility.get_py_str(item.text())]
        self.showRelation(self.selectedRelation)

    def showAttributes(self, item):
        '''Shows the attributes of the selected relation'''
        rel = compatibility.get_py_str(item.text())
        self.ui.lstAttributes.clear()
        for j in self.relations[rel].header.attributes:
            self.ui.lstAttributes.addItem(j)

    def updateRelations(self):
        self.ui.lstRelations.clear()
        for i in self.relations:
            if i != "__builtins__":
                self.ui.lstRelations.addItem(i)

    def saveRelation(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, QtWidgets.QApplication.translate(
            "Form", "Save Relation"), "", QtWidgets.QApplication.translate("Form", "Relations (*.csv)"))

        filename = compatibility.get_filename(filename)
        if (len(filename) == 0):  # Returns if no file was selected
            return
        self.selectedRelation.save(filename)
        return

    def unloadRelation(self):
        for i in self.ui.lstRelations.selectedItems():
            del self.relations[compatibility.get_py_str(i.text())]
        self.updateRelations()

    def editRelation(self):
        from relational_gui import creator
        for i in self.ui.lstRelations.selectedItems():
            result = creator.edit_relation(
                self.relations[compatibility.get_py_str(i.text())])
            if result != None:
                self.relations[compatibility.get_py_str(i.text())] = result
        self.updateRelations()

    def newRelation(self):
        from relational_gui import creator
        result = creator.edit_relation()

        if result == None:
            return
        while True:
            res = QtWidgets.QInputDialog.getText(
                self,
                QtWidgets.QApplication.translate("Form", "New relation"),
                QtWidgets.QApplication.translate(
                    "Form", "Insert the name for the new relation"),
                QtWidgets.QLineEdit.Normal, ''
            )
            if res[1] == False:# or len(res[0]) == 0:
                return
            name = compatibility.get_py_str(res[0])

            if not rtypes.is_valid_relation_name(name):
                r = QtWidgets.QApplication.translate(
                    "Form", str("Wrong name for destination relation: %s." % name)
                )
                QtWidgets.QMessageBox.information(
                    self, QtWidgets.QApplication.translate("Form", "Error"), r
                )
                continue

            try:
                self.relations[name] = result
                self.updateRelations()
            except Exception as e:
                print (e)
                QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("Form", "Error"), "%s\n%s" %
                                                (QtWidgets.QApplication.translate("Form", "Check your query!"), e.__str__()))
            finally:
                return

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    def save_settings(self):
        # self.settings.setValue("width",)
        pass

    def restore_settings(self):
        # self.settings.value('session_name','default').toString()
        self.setMultiline(self.settings.value('multiline','false')=='true')
        self.ui.txtMultiQuery.setPlainText(self.settings.value('multiline/query',''))

    def showSurvey(self):
        if self.Survey == None:
            self.Survey = surveyForm.surveyForm()
            ui = survey.Ui_Form()
            self.Survey.setUi(ui)
            ui.setupUi(self.Survey)
            self.Survey.setDefaultValues()
        self.Survey.show()

    def showAbout(self):
        if self.About == None:
            self.About = QtWidgets.QDialog()
            ui = about.Ui_Dialog()
            ui.setupUi(self.About)
        self.About.show()

    def loadRelation(self, filename=None, name=None):
        '''Loads a relation. Without parameters it will ask the user which relation to load,
        otherwise it will load filename, giving it name.
        It shouldn't be called giving filename but not giving name.'''
        # Asking for file to load
        if filename == None:
            filename = QtWidgets.QFileDialog.getOpenFileName(self, QtWidgets.QApplication.translate(
                "Form", "Load Relation"), "", QtWidgets.QApplication.translate("Form", "Relations (*.csv);;Text Files (*.txt);;All Files (*)"))
            filename = compatibility.get_filename(filename)

        # Default relation's name
        f = filename.split('/')  # Split the full path
        defname = f[len(f) - 1].lower()  # Takes only the lowercase filename

        if len(defname) == 0:
            return

        if (defname.endswith(".csv")):  # removes the extension
            defname = defname[:-4]

        if name == None:  # Prompt dialog to insert name for the relation
            res = QtWidgets.QInputDialog.getText(
                self, QtWidgets.QApplication.translate("Form", "New relation"), QtWidgets.QApplication.translate(
                    "Form", "Insert the name for the new relation"),
                QtWidgets.QLineEdit.Normal, defname)
            if res[1] == False or len(res[0]) == 0:
                return

            name = compatibility.get_py_str(res[0])

        if not rtypes.is_valid_relation_name(name):
            r = QtWidgets.QApplication.translate(
                "Form", str("Wrong name for destination relation: %s." % name))
            QtWidgets.QMessageBox.information(
                self, QtWidgets.QApplication.translate("Form", "Error"), r)
            return

        try:
            self.relations[name] = relation.relation(filename)
        except Exception as e:
            print (e)
            QtWidgets.QMessageBox.information(None, QtWidgets.QApplication.translate("Form", "Error"), "%s\n%s" %
                                              (QtWidgets.QApplication.translate("Form", "Check your query!"), e.__str__()))
            return

        self.updateRelations()

    def addProduct(self):
        self.addSymbolInQuery(parser.PRODUCT)

    def addDifference(self):
        self.addSymbolInQuery(parser.DIFFERENCE)

    def addUnion(self):
        self.addSymbolInQuery(parser.UNION)

    def addIntersection(self):
        self.addSymbolInQuery(parser.INTERSECTION)

    def addDivision(self):
        self.addSymbolInQuery(parser.DIVISION)

    def addOLeft(self):
        self.addSymbolInQuery(parser.JOIN_LEFT)

    def addJoin(self):
        self.addSymbolInQuery(parser.JOIN)

    def addORight(self):
        self.addSymbolInQuery(parser.JOIN_RIGHT)

    def addOuter(self):
        self.addSymbolInQuery(parser.JOIN_FULL)

    def addProjection(self):
        self.addSymbolInQuery(parser.PROJECTION)

    def addSelection(self):
        self.addSymbolInQuery(parser.SELECTION)

    def addRename(self):
        self.addSymbolInQuery(parser.RENAME)

    def addArrow(self):
        self.addSymbolInQuery(parser.ARROW)

    def addSymbolInQuery(self, symbol):
        if self.multiline:
            self.ui.txtMultiQuery.insertPlainText(symbol)
            self.ui.txtMultiQuery.setFocus()
        else:
            self.ui.txtQuery.insert(symbol)
            self.ui.txtQuery.setFocus()
