# Relational
# Copyright (C) 2008-2020  Salvo "LtWorf" Tomaselli
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

from PyQt5 import QtCore, QtWidgets, QtGui

from relational import parser, optimizer, rtypes
from relational.maintenance import UserInterface

from relational_gui import about
from relational_gui import survey
from relational_gui import surveyForm
from relational_gui import maingui


version = ''


class relForm(QtWidgets.QMainWindow):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.About = None
        self.Survey = None
        self.undo = None  # UndoQueue for queries
        self.undo_program = None
        self.selectedRelation = None
        self.ui = maingui.Ui_MainWindow()
        self.user_interface = UserInterface()
        self.history_current_line = None

        # Creates the UI
        self.ui.setupUi(self)

        # Setting fonts for symbols
        f = QtGui.QFont()
        size = f.pointSize()
        if sys.platform.startswith('win'):
            winFont = 'Cambria'
            symbolFont = 'Segoe UI Symbol'
            increment = 4
        else:
            winFont = f.family()
            symbolFont = f.family()
            increment = 2
        font = QtGui.QFont(winFont, size + increment)
        sfont = QtGui.QFont(symbolFont)
        self.ui.lstHistory.setFont(font)
        self.ui.txtMultiQuery.setFont(font)
        self.ui.txtQuery.setFont(font)
        self.ui.groupOperators.setFont(font)
        self.ui.cmdClearMultilineQuery.setFont(sfont)
        self.ui.cmdClearQuery.setFont(sfont)

        self.settings = QtCore.QSettings()
        self._restore_settings()


        # Shortcuts
        shortcuts = (
            (self.ui.lstRelations, QtGui.QKeySequence.Delete, self.unloadRelation),
            (self.ui.lstRelations, 'Space', lambda: self.printRelation(self.ui.lstRelations.currentItem())),
            (self.ui.txtQuery, QtGui.QKeySequence.MoveToNextLine, self.next_history),
            (self.ui.txtQuery, QtGui.QKeySequence.MoveToPreviousLine, self.prev_history),
        )

        self.add_shortcuts(shortcuts)

    def next_history(self):
        if self.ui.lstHistory.currentRow() + 1 == self.ui.lstHistory.count() and self.history_current_line:
            self.ui.txtQuery.setText(self.history_current_line)
            self.history_current_line = None
        elif self.history_current_line:
            self.ui.lstHistory.setCurrentRow(self.ui.lstHistory.currentRow()+1)
            self.resumeHistory(self.ui.lstHistory.currentItem())

    def prev_history(self):
        if self.history_current_line is None:
            self.history_current_line = self.ui.txtQuery.text()

            if self.ui.lstHistory.currentItem() is None:
                return
            if not self.ui.lstHistory.currentItem().text() != self.ui.txtQuery.text():
                self.ui.lstHistory.setCurrentRow(self.ui.lstHistory.currentRow()-1)
        elif self.ui.lstHistory.currentRow() > 0:
            self.ui.lstHistory.setCurrentRow(self.ui.lstHistory.currentRow()-1)
        self.resumeHistory(self.ui.lstHistory.currentItem())

    def add_shortcuts(self, shortcuts):
        for widget,shortcut,slot in shortcuts:
            action = QtWidgets.QAction(self)
            action.triggered.connect(slot)
            action.setShortcut(QtGui.QKeySequence(shortcut))
            # I couldn't find the constant
            action.setShortcutContext(0)
            widget.addAction(action)

    def checkVersion(self):
        from relational import maintenance
        online = maintenance.check_latest_version()

        if online is None:
            r = QtWidgets.QApplication.translate("Form", "Network error")
        elif online > version:
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

    def setHistoryShown(self, history_shown):
        self.history_shown = history_shown
        self.settings.setValue('history_shown', history_shown)
        self.ui.lstHistory.setVisible(history_shown)
        self.ui.actionShow_history.setChecked(history_shown)

    def setMultiline(self, multiline):
        self.multiline = multiline
        self.settings.setValue('multiline', multiline)
        if multiline:
            index = 0
        else:
            index = 1
        self.ui.stackedWidget.setCurrentIndex(index)
        self.ui.actionMulti_line_mode.setChecked(multiline)

    def load_query(self, *index):
        self.ui.txtQuery.setText(self.savedQ.itemData(index[0]).toString())

    def undoOptimize(self):
        '''Undoes the optimization on the query, popping one item from the undo list'''
        if self.undo != None:
            self.ui.txtQuery.setText(self.undo)

    def undoOptimizeProgram(self):
        if self.undo_program:
            self.ui.txtMultiQuery.setPlainText(self.undo_program)

    def optimizeProgram(self):
        self.undo_program = self.ui.txtMultiQuery.toPlainText()
        result = optimizer.optimize_program(
            self.ui.txtMultiQuery.toPlainText(),
            self.user_interface.relations
        )
        self.ui.txtMultiQuery.setPlainText(result)


    def optimize(self):
        '''Performs all the possible optimizations on the query'''
        self.undo = self.ui.txtQuery.text()  # Storing the query in undo list

        res_rel,query = self.user_interface.split_query(self.ui.txtQuery.text(),None)
        try:
            trace = []
            result = optimizer.optimize_all(
                query,
                self.user_interface.relations,
                debug=trace
            )
            print('==== Optimization steps ====')
            print(query)
            print('\n'.join(trace))
            print('========')

            if res_rel:
                result = '%s = %s' % (res_rel, result)
            self.ui.txtQuery.setText(result)
        except Exception as e:
            self.error(e)

    def resumeHistory(self, item):
        if item is None:
            return
        itm = item.text()
        self.ui.txtQuery.setText(itm)

    def execute(self):

        # Show the 'Processing' frame
        self.ui.stackedWidget.setCurrentIndex(2)
        QtCore.QCoreApplication.processEvents()

        try:
            '''Executes the query'''
            if self.multiline:
                query = self.ui.txtMultiQuery.toPlainText()
                self.settings.setValue('multiline/query', query)
            else:
                query = self.ui.txtQuery.text()

            if not query.strip():
                return

            try:
                self.selectedRelation = self.user_interface.multi_execute(query)
            except Exception as e:
                return self.error(e)
            finally:
                self.updateRelations()  # update the list
                self.showRelation(self.selectedRelation)

            if not self.multiline:
                # Last in history
                item = self.ui.lstHistory.item(self.ui.lstHistory.count() - 1)

                if item is None or item.text() != query:
                    # Adds to history if it is not already the last
                    hitem = QtWidgets.QListWidgetItem(None, 0)
                    hitem.setText(query)
                    self.ui.lstHistory.addItem(hitem)
                    self.ui.lstHistory.setCurrentItem(hitem)
        finally:
            # Restore the normal frame
            self.setMultiline(self.multiline)


    def showRelation(self, rel):
        '''Shows the selected relation into the table'''
        self.ui.table.clear()

        if rel is None:  # No relation to show
            self.ui.table.setColumnCount(1)
            self.ui.table.headerItem().setText(0, "Empty relation")
            return
        self.ui.table.setColumnCount(len(rel.header))

        # Set content
        for i in rel.content:
            item = QtWidgets.QTreeWidgetItem()
            for j,k in enumerate(i):
                if k is None:
                    item.setBackground(j, QtGui.QBrush(QtCore.Qt.darkRed, QtCore.Qt.Dense4Pattern))
                elif isinstance(k, (int, float)):
                    item.setForeground(j, QtGui.QPalette().link())
                elif not isinstance(k, str):
                    item.setBackground(j, QtGui.QBrush(QtCore.Qt.darkGreen, QtCore.Qt.Dense4Pattern))
                item.setText(j, str(k))
            self.ui.table.addTopLevelItem(item)

        # Sets columns
        for i, attr in enumerate(rel.header):
            self.ui.table.headerItem().setText(i, attr)
            self.ui.table.resizeColumnToContents(i)

    def printRelation(self, item):
        self.selectedRelation = self.user_interface.relations[item.text()]
        self.showRelation(self.selectedRelation)

    def showAttributes(self, item):
        '''Shows the attributes of the selected relation'''
        rel = item.text()
        self.ui.lstAttributes.clear()
        for j in self.user_interface.relations[rel].header:
            self.ui.lstAttributes.addItem(j)

    def updateRelations(self):
        self.ui.lstRelations.clear()
        for i in self.user_interface.relations:
            if i != "__builtins__":
                self.ui.lstRelations.addItem(i)

    def saveRelation(self):
        if not self.ui.lstRelations.selectedItems():
            r = QtWidgets.QApplication.translate(
                "Form", "Select a relation first."
            )
            QtWidgets.QMessageBox.information(
                self, QtWidgets.QApplication.translate("Form", "Error"), r
            )
            return
        filename = QtWidgets.QFileDialog.getSaveFileName(
            self, QtWidgets.QApplication.translate("Form", "Save Relation"),
            "",
            QtWidgets.QApplication.translate("Form", "Json relations (*.json);;CSV relations (*.csv)")
        )[0]
        if (len(filename) == 0):  # Returns if no file was selected
            return

        relname = self.ui.lstRelations.selectedItems()[0].text()
        self.user_interface.store(filename, relname)

    def unloadRelation(self):
        for i in self.ui.lstRelations.selectedItems():
            del self.user_interface.relations[i.text()]
        self.updateRelations()

    def newSession(self):
        self.user_interface.session_reset()
        self.updateRelations()

    def editRelation(self):
        from relational_gui import creator
        for i in self.ui.lstRelations.selectedItems():
            try:
                result = creator.edit_relation(
                    self.user_interface.get_relation(i.text())
                )
            except Exception as e:
                QtWidgets.QMessageBox.warning(
                    self, QtWidgets.QApplication.translate("Form", "Error"), str(e)
                )
                return
            if result != None:
                self.user_interface.set_relation(i.text(), result)
        self.updateRelations()

    def error(self, exception):
        print (exception)
        QtWidgets.QMessageBox.information(
            None, QtWidgets.QApplication.translate("Form", "Error"),
            str(exception)
        )

    def promptRelationName(self):
        while True:
            res = QtWidgets.QInputDialog.getText(
                self,
                QtWidgets.QApplication.translate("Form", "New relation"),
                QtWidgets.QApplication.translate(
                    "Form", "Insert the name for the new relation"),
                QtWidgets.QLineEdit.Normal, ''
            )
            if res[1] == False:  # or len(res[0]) == 0:
                return None
            name = res[0]
            if not rtypes.is_valid_relation_name(name):
                r = QtWidgets.QApplication.translate(
                    "Form", str(
                        "Wrong name for destination relation: %s." % name)
                )
                QtWidgets.QMessageBox.information(
                    self, QtWidgets.QApplication.translate("Form", "Error"), r
                )
                continue
            return name

    def newRelation(self):
        from relational_gui import creator
        result = creator.edit_relation()

        if result is None:
            return
        name = self.promptRelationName()

        try:
            self.user_interface.relations[name] = result
            self.updateRelations()
        except Exception as e:
            self.error(e)

    def closeEvent(self, event):
        self.save_settings()
        event.accept()

    def save_settings(self):
        self.settings.setValue('maingui/geometry', self.saveGeometry())
        self.settings.setValue('maingui/windowState', self.saveState())
        self.settings.setValue('maingui/splitter', self.ui.splitter.saveState())
        self.settings.setValue('maingui/relations', self.user_interface.session_dump())

    def _restore_settings(self):
        self.user_interface.session_restore(self.settings.value('maingui/relations'))
        self.updateRelations()

        self.setMultiline(self.settings.value('multiline', 'false') == 'true')
        self.setHistoryShown(self.settings.value('history_shown', 'true') == 'true')
        self.ui.txtMultiQuery.setPlainText(
            self.settings.value('multiline/query', ''))
        try:
            self.restoreGeometry(self.settings.value('maingui/geometry'))
            self.restoreState(self.settings.value('maingui/windowState'))
            self.ui.splitter.restoreState(self.settings.value('maingui/splitter'))
        except:
            pass

    def showSurvey(self):
        if self.Survey is None:
            self.Survey = surveyForm.surveyForm()
            ui = survey.Ui_Form()
            self.Survey.setUi(ui)
            ui.setupUi(self.Survey)
            self.Survey.setDefaultValues()
        self.Survey.show()

    def showAbout(self):
        if self.About is None:
            self.About = QtWidgets.QDialog()
            ui = about.Ui_Dialog()
            ui.setupUi(self.About)
        self.About.show()

    def loadRelation(self, filenames=None):
        '''Loads a relation. Without parameters it will ask the user which relation to load,
        otherwise it will load filename, giving it name.
        It shouldn't be called giving filename but not giving name.'''
        # Asking for file to load
        if not filenames:
            f = QtWidgets.QFileDialog.getOpenFileNames(
                self,
                QtWidgets.QApplication.translate("Form", "Load Relation"),
                "",
                QtWidgets.QApplication.translate(
                    "Form",
                    "Relations (*.json *.csv);;Text Files (*.txt);;All Files (*)"
                )
            )
            filenames = f[0]

        for f in filenames:
            # Default relation's name
            name = self.user_interface.suggest_name(f)
            if name is None:
                name = self.promptRelationName()
            if name is None:
                continue

            try:
                self.user_interface.load(f, name)
            except Exception as e:
                self.error(e)
                continue

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
