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
    
from relational import relation, parser, optimizer,rtypes

import sys
import about
import survey
import os
import surveyForm
import maingui
import compatibility

class relForm(QtGui.QMainWindow):
    
    def __init__(self,ui):
        QtGui.QMainWindow.__init__(self)
        self.About=None
        self.Survey=None
        self.relations={} #Dictionary for relations
        self.undo=None #UndoQueue for queries
        self.selectedRelation=None
        self.ui=ui
        self.qcounter=1 #Query counter
    def checkVersion(self):
        from relational import maintenance
        online=maintenance.check_latest_version()
        
        if online>version:
            r=QtGui.QApplication.translate("Form", "New version available online: %s." % online)
        elif online==version:
            r=QtGui.QApplication.translate("Form", "Latest version installed.")
        else:
            r=QtGui.QApplication.translate("Form", "You are using an unstable version.")
        
        QtGui.QMessageBox.information(self,QtGui.QApplication.translate("Form", "Version"),r)
        
        
    def load_query(self,*index):
        self.ui.txtQuery.setText(self.savedQ.itemData(index[0]).toString())
        
    def undoOptimize(self):
        '''Undoes the optimization on the query, popping one item from the undo list'''
        if self.undo!=None:
            self.ui.txtQuery.setText(self.undo)

    def optimize(self):
        '''Performs all the possible optimizations on the query'''
        self.undo=self.ui.txtQuery.text() #Storing the query in undo list
        
        query=compatibility.get_py_str(self.ui.txtQuery.text())
        try:
            result=optimizer.optimize_all(query,self.relations)
            compatibility.set_utf8_text(self.ui.txtQuery,result)
        except Exception, e:
            QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Error"),"%s\n%s" % (QtGui.QApplication.translate("Form", "Check your query!"),e.__str__())  )
            
        
        
    def resumeHistory(self,item):
        itm=compatibility.get_py_str(item.text()).split(' = ',1)
        compatibility.set_utf8_text(self.ui.txtResult,itm[0])
        compatibility.set_utf8_text(self.ui.txtQuery,itm[1])        
        
    def execute(self):
        '''Executes the query'''
        
        query=compatibility.get_py_str(self.ui.txtQuery.text())
        res_rel=compatibility.get_py_str(self.ui.txtResult.text())#result relation's name
        
        if not rtypes.is_valid_relation_name(res_rel):
            QtGui.QMessageBox.information(self,QtGui.QApplication.translate("Form", "Error"),QtGui.QApplication.translate("Form", "Wrong name for destination relation."))
            return
        
        try:
            #Converting string to utf8 and then from qstring to normal string
            expr=parser.parse(query)#Converting expression to python code
            print query,"-->" , expr #Printing debug
            result=eval(expr,self.relations) #Evaluating the expression
            
            self.relations[res_rel]=result #Add the relation to the dictionary
            self.updateRelations() #update the list
            self.selectedRelation=result
            self.showRelation(self.selectedRelation) #Show the result in the table
        except Exception, e:
            print e
            QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Error"),"%s\n%s" % (QtGui.QApplication.translate("Form", "Check your query!"),e.__str__())  )
            return

        #Adds to history
        item=u'%s = %s' % (compatibility.get_py_str(self.ui.txtResult.text()),compatibility.get_py_str(self.ui.txtQuery.text()))
        #item=item.decode('utf-8'))
        compatibility.add_list_item(self.ui.lstHistory,item)
        
        self.qcounter+=1
        compatibility.set_utf8_text(self.ui.txtResult,u"_last%d"% self.qcounter) #Sets the result relation name to none
        
    def showRelation(self,rel):
        '''Shows the selected relation into the table'''
        self.ui.table.clear()
        
        if rel==None: #No relation to show
            self.ui.table.setColumnCount(1)
            self.ui.table.headerItem().setText(0,"Empty relation")
            return
        self.ui.table.setColumnCount(len(rel.header.attributes))
        
        #Set content
        for i in rel.content:
            item = QtGui.QTreeWidgetItem()
            for j in range(len(i)):
                item.setText(j, i[j])
            self.ui.table.addTopLevelItem(item)
        
        #Sets columns
        for i in range(len(rel.header.attributes)):
            self.ui.table.headerItem().setText(i,rel.header.attributes[i])
            self.ui.table.resizeColumnToContents(i) #Must be done in order to avoid  too small columns
        
        
    def printRelation(self,item):
        self.selectedRelation=self.relations[compatibility.get_py_str(item.text())]
        self.showRelation(self.selectedRelation)
            
    def showAttributes(self,item):
        '''Shows the attributes of the selected relation'''
        rel=compatibility.get_py_str(item.text())
        self.ui.lstAttributes.clear()
        for j in self.relations[rel].header.attributes:
            self.ui.lstAttributes.addItem (j)
            
    def updateRelations(self):
        self.ui.lstRelations.clear()
        for i in self.relations:
            if i != "__builtins__":
                self.ui.lstRelations.addItem(i)
    def saveRelation(self):
        filename = QtGui.QFileDialog.getSaveFileName(self,QtGui.QApplication.translate("Form", "Save Relation"),"",QtGui.QApplication.translate("Form", "Relations (*.csv)"))
        
        filename=compatibility.get_filename(filename)        
        if (len(filename)==0):#Returns if no file was selected
            return
        self.selectedRelation.save(filename)
        return
    def unloadRelation(self):
        for i in self.ui.lstRelations.selectedItems():
            del self.relations[compatibility.get_py_str(i.text())]
        self.updateRelations()
    def editRelation(self):
        import creator
        for i in self.ui.lstRelations.selectedItems():
            result=creator.edit_relation(self.relations[compatibility.get_py_str(i.text())])
            if result!=None:
                self.relations[compatibility.get_py_str(i.text())]=result
        self.updateRelations()
    def newRelation(self):
        import creator
        result=creator.edit_relation()
        
        if result==None:
            return
        res=QtGui.QInputDialog.getText(
                self, 
                QtGui.QApplication.translate("Form", "New relation"),
                QtGui.QApplication.translate("Form", "Insert the name for the new relation"),
                QtGui.QLineEdit.Normal,'')
        if res[1]==False or len(res[0])==0:
            return
            
        #Patch provided by Angelo 'Havoc' Puglisi
        name=compatibility.get_py_str(res[0])
        
        if not rtypes.is_valid_relation_name(name):
            r=QtGui.QApplication.translate("Form", str("Wrong name for destination relation: %s." % name))
            QtGui.QMessageBox.information(self,QtGui.QApplication.translate("Form", "Error"),r)
            return
        
        try:
            self.relations[name]=result
        except Exception, e:
            print e
            QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Error"),"%s\n%s" % (QtGui.QApplication.translate("Form", "Check your query!"),e.__str__())  )
            return
            
        
        self.updateRelations()

            
    def showSurvey(self):
      if self.Survey==None:
        self.Survey=surveyForm.surveyForm()
        ui = survey.Ui_Form()
        self.Survey.setUi(ui)
        ui.setupUi(self.Survey)
        self.Survey.setDefaultValues()
      self.Survey.show()
    def showAbout(self):
        if self.About==None:
            self.About = QtGui.QDialog()
            ui = about.Ui_Dialog()
            ui.setupUi(self.About)
        self.About.show()

    def loadRelation(self,filename=None,name=None):
        '''Loads a relation. Without parameters it will ask the user which relation to load,
        otherwise it will load filename, giving it name.
        It shouldn't be called giving filename but not giving name.'''
        #Asking for file to load
        if filename==None:
            filename = QtGui.QFileDialog.getOpenFileName(self,QtGui.QApplication.translate("Form", "Load Relation"),"",QtGui.QApplication.translate("Form", "Relations (*.csv);;Text Files (*.txt);;All Files (*)"))
            filename=compatibility.get_filename(filename)

        #Default relation's name
        f=filename.split('/') #Split the full path
        defname=f[len(f)-1].lower() #Takes only the lowercase filename
        
        if len(defname)==0:
            return

        if (defname.endswith(".csv")): #removes the extension
            defname=defname[:-4]
        
        if name==None: #Prompt dialog to insert name for the relation
            res=QtGui.QInputDialog.getText(self, QtGui.QApplication.translate("Form", "New relation"),QtGui.QApplication.translate("Form", "Insert the name for the new relation"),
            QtGui.QLineEdit.Normal,defname)
            if res[1]==False or len(res[0])==0:
                return
            
            #Patch provided by Angelo 'Havoc' Puglisi
            name=compatibility.get_py_str(res[0])
        
        if not rtypes.is_valid_relation_name(name):
            r=QtGui.QApplication.translate("Form", str("Wrong name for destination relation: %s." % name))
            QtGui.QMessageBox.information(self,QtGui.QApplication.translate("Form", "Error"),r)
            return
        
        try:
            self.relations[name]=relation.relation(filename)
        except Exception, e:
            print e
            QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Error"),"%s\n%s" % (QtGui.QApplication.translate("Form", "Check your query!"),e.__str__())  )
            return
            
        
        self.updateRelations()

    def addProduct(self):
        self.addSymbolInQuery(u"*")
    def addDifference(self):
        self.addSymbolInQuery(u"-")
    def addUnion(self):
        self.addSymbolInQuery(u"ᑌ")
    def addIntersection(self):
        self.addSymbolInQuery(u"ᑎ")
    def addDivision(self):
        self.addSymbolInQuery(u"÷")
    def addOLeft(self):
        self.addSymbolInQuery(u"ᐅLEFTᐊ")
    def addJoin(self):
        self.addSymbolInQuery(u"ᐅᐊ")
    def addORight(self):
        self.addSymbolInQuery(u"ᐅRIGHTᐊ")
    def addOuter(self):
        self.addSymbolInQuery(u"ᐅFULLᐊ")
    def addProjection(self):
        self.addSymbolInQuery(u"π")
    def addSelection(self):
        self.addSymbolInQuery(u"σ")
    def addRename(self):
        self.addSymbolInQuery(u"ρ")
    def addArrow(self):
        self.addSymbolInQuery(u"➡")
    
    def addSymbolInQuery(self,symbol):
        self.ui.txtQuery.insert(symbol)
        self.ui.txtQuery.setFocus()
        