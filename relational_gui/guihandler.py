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
from PyQt4 import QtCore, QtGui
from relational import relation, parser, optimizer

import sys
import about
import survey
import os
import surveyForm
import maingui

class relForm(QtGui.QMainWindow):
    
    def __init__(self,ui):
        QtGui.QMainWindow.__init__(self)
        self.About=None
        self.Survey=None
        self.relations={} #Dictionary for relations
        self.undo=None #UndoQueue for queries
        self.selectedRelation=None
        self.ui=ui
        self.qcounter=1
        
    def load_query(self,*index):
        self.ui.txtQuery.setText(self.savedQ.itemData(index[0]).toString())
        
    def undoOptimize(self):
        '''Undoes the optimization on the query, popping one item from the undo list'''
        if self.undo!=None:
            self.ui.txtQuery.setText(self.undo)

    def optimize(self):
        '''Performs all the possible optimizations on the query'''
        self.undo=self.ui.txtQuery.text() #Storing the query in undo list
        
        result=optimizer.optimize_all(str(self.ui.txtQuery.text().toUtf8()),self.relations)
        self.ui.txtQuery.setText(QtCore.QString.fromUtf8(result))
        
        #self.txtQuery.setText(result)
    def resumeHistory(self,item):
        itm=str(item.text().toUtf8()).split(' = ',1)
        self.ui.txtResult.setText(QtCore.QString.fromUtf8(itm[0]))
        self.ui.txtQuery.setText(QtCore.QString.fromUtf8(itm[1]))
        
        
    def execute(self):
        '''Executes the query'''
        
        query=str(self.ui.txtQuery.text().toUtf8())
        res_rel=str(self.ui.txtResult.text())#result relation's name
        if len(res_rel)==0: #If no name is set use the default last_
            QtGui.QMessageBox.information(self,QtGui.QApplication.translate("Form", "Error"),QtGui.QApplication.translate("Form", "Missing destination relation."))
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
        #Query was executed normally
        history_item=QtCore.QString()
        history_item.append(self.ui.txtResult.text())
        history_item.append(u' = ')
        history_item.append(self.ui.txtQuery.text())
        hitem=QtGui.QListWidgetItem(None,0)
        hitem.setText(history_item)
        self.ui.lstHistory.addItem (hitem)
        self.ui.lstHistory.setCurrentItem(hitem)
        
        self.qcounter+=1
        self.ui.txtResult.setText(QtCore.QString(u"_last%d"% self.qcounter)) #Sets the result relation name to none
        
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
        self.selectedRelation=self.relations[str(item.text().toUtf8())]
        self.showRelation(self.selectedRelation)
            
    def showAttributes(self,item):
        '''Shows the attributes of the selected relation'''
        rel=str(item.text().toUtf8())
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
      
        filename=str(filename.toUtf8()) #Converts QString to string
        if (len(filename)==0):#Returns if no file was selected
            return
        self.selectedRelation.save(filename)
        return
    def unloadRelation(self):
        for i in self.ui.lstRelations.selectedItems():
            del self.relations[str(i.text().toUtf8())]
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
            filename = QtGui.QFileDialog.getOpenFileName(self,QtGui.QApplication.translate("Form", "Load Relation"),"",QtGui.QApplication.translate("Form", "Relations (*.csv);;Old Relations (*.tlb);;Text Files (*.txt);;All Files (*)"))
                
            #Default relation's name
            f=str(filename.toUtf8()).split('/') #Split the full path
            defname=f[len(f)-1].lower() #Takes only the lowercase filename
            
        else:
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
            self.relations[str(res[0].toUtf8())]=relation.relation(str(filename.toUtf8()))            
        else: #name was decided by caller
            self.relations[name]=relation.relation(filename)
                
        self.updateRelations()
    def insertTuple(self):
        '''Shows an input dialog and inserts the inserted tuple into the selected relation'''
        res=QtGui.QInputDialog.getText(self, QtGui.QApplication.translate("Form", "New relation"),QtGui.QApplication.translate("Form", "Insert the values, comma separated"),
        QtGui.QLineEdit.Normal,"")
        if res[1]==False:
            return
        
        t=[]
        for i in str(res[0].toUtf8()).split(","):
            t.append(i.strip())
        
        if self.selectedRelation!=None and self.selectedRelation.insert(t) > 0:
            self.showRelation(self.selectedRelation)
            
        return
    def deleteTuple(self):
        '''Shows an input dialog and removes the tuples corresponding to the condition.'''
        res=QtGui.QInputDialog.getText(self, QtGui.QApplication.translate("Form", "New relation"),QtGui.QApplication.translate("Form", "Remove tuples: insert where condition"),
        QtGui.QLineEdit.Normal,"")
        if res[1]==False:
            return
        
        if self.selectedRelation!=None and self.selectedRelation.delete(str(res[0].toUtf8())) > 0:
            self.showRelation(self.selectedRelation)
            
        return

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
        
def q_main():
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = RelForm()
    ui = maingui.Ui_MainWindow()
    ui.setupUi(Form)
    Form.setupUi(ui)
    Form.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    q_main()