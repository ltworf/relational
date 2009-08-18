# -*- coding: utf-8 -*-
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
from PyQt4 import QtCore, QtGui
from relational import relation, parser, optimizer

import sys
import about
import survey
import os
import surveyForm

class Ui_Form(object):
    def __init__(self):
        self.About=None
        self.Survey=None
        self.relations={} #Dictionary for relations
        self.undo=[] #UndoQueue for queries
        self.selectedRelation=None
    def load_query(self,*index):
        self.txtQuery.setText(self.savedQ.itemData(index[0]).toString())
        
    def save_query(self):
        defname=""
        res=QtGui.QInputDialog.getText(self.Form, QtGui.QApplication.translate("Form", "New query"),QtGui.QApplication.translate("Form", "Insert the name for the query"),
        QtGui.QLineEdit.Normal,defname)
        if res[1]==False:
            return
            
        self.savedQ.addItem(res[0],QtCore.QVariant(self.txtQuery.text()))
    def toggle_advanced(self):
        '''Hides or shows the advanced frame'''
        if self.advancedBox.isVisible():
            self.advancedBox.hide()
        else:
            self.advancedBox.show()
        
    def undo_optimize(self):
        '''Undoes the optimization on the query, popping one item from the undo list'''
        try:
            self.txtQuery.setText(self.undo.pop())
        except:#Nothing to restore
            pass
    def optimize(self):
        '''Performs all the possible optimizations on the query'''
        self.undo.insert(len(self.undo),self.txtQuery.text()) #Storing the query in undo list
        
        result=optimizer.optimize_all(str(self.txtQuery.text().toUtf8()),self.relations)
        self.txtQuery.setText(QtCore.QString.fromUtf8(result))
        
        #self.txtQuery.setText(result)
    def execute(self):
        '''Executes the query'''
        try:
            #Converting string to utf8 and then from qstring to normal string
            query=str(self.txtQuery.text().toUtf8())
            expr=parser.parse(query)#Converting expression to python code
            print query,"-->" , expr #Printing debug
            result=eval(expr,self.relations) #Evaluating the expression
            
            #self.undo.insert(len(self.undo),self.txtQuery.text()) #Storing the query in undo list
            
            res_rel=str(self.txtResult.text())#result relation's name
            self.txtResult.setText("") #Sets the result relation name to none
            if len(res_rel)==0: #If no name is set use the default last_
                res_rel="last_"
            
            self.relations[res_rel]=result #Add the relation to the dictionary
            self.updateRelations() #update the list
            self.selectedRelation=result
            self.showRelation(self.selectedRelation) #Show the result in the table
        except:
            QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Error"),QtGui.QApplication.translate("Form", "Check your query!")  )
    def showRelation(self,rel):
        '''Shows the selected relation into the table'''
        self.table.clear()
        
        if rel==None: #No relation to show
            self.table.setColumnCount(1)
            self.table.headerItem().setText(0,"Empty relation")
            return
        self.table.setColumnCount(len(rel.header.attributes))
        
        #Set content
        for i in rel.content:
            item = QtGui.QTreeWidgetItem()
            for j in range(len(i)):
                item.setText(j, i[j])
            self.table.addTopLevelItem(item)
        
        #Sets columns
        for i in range(len(rel.header.attributes)):
            self.table.headerItem().setText(i,rel.header.attributes[i])
            self.table.resizeColumnToContents(i) #Must be done in order to avoid  too small columns
        
        
    def printRelation(self,*rel):
        for i in rel:
            self.selectedRelation=self.relations[str(i.text().toUtf8())]
            self.showRelation(self.selectedRelation)
            
    def showAttributes(self,*other):
        '''Shows the attributes of the selected relation'''
        for i in other:
            rel=str(i.text().toUtf8())
            self.lstAttributes.clear()
            for j in self.relations[rel].header.attributes:
                self.lstAttributes.addItem (j)
            
    def updateRelations(self):
        self.lstRelations.clear()
        for i in self.relations:
            if i != "__builtins__":
                self.lstRelations.addItem(i)
    def saveRelation(self):
      filename = QtGui.QFileDialog.getSaveFileName(self.Form,QtGui.QApplication.translate("Form", "Save Relation"),"",QtGui.QApplication.translate("Form", "Relations (*.csv)"))
      
      filename=str(filename.toUtf8()) #Converts QString to string
      if (len(filename)==0):#Returns if no file was selected
        return
      if (not filename.endswith(".csv")):#Adds extension if needed
        filename+=".csv"
      
      for i in self.lstRelations.selectedItems():
            self.relations[str(i.text().toUtf8())].save(filename)
      return
    def unloadRelation(self):
        for i in self.lstRelations.selectedItems():
            del self.relations[str(i.text().toUtf8())]
        self.updateRelations()
    def showSurvey(self):
      if self.Survey==None:
        self.Survey=surveyForm.surveyForm()
        ui = survey.Ui_Form()
        self.Survey.setUi(ui)
        ui.setupUi(self.Survey)
      self.Survey.show()
    def showAbout(self):
        if self.About==None:
            self.About = QtGui.QDialog()
            ui = about.Ui_Dialog()
            ui.setupUi(self.About)
        self.About.show()

    def loadRelation(self,filename=None,name=None):
        '''Loads a relation. Without parameters it will ask the user which relation to load,
        otherwise it will load filename, giving it name'''
        #Asking for file to load
        if filename==None:
            filename = QtGui.QFileDialog.getOpenFileName(None,QtGui.QApplication.translate("Form", "Load Relation"),"",QtGui.QApplication.translate("Form", "Relations (*.csv);;Old Relations (*.tlb);;Text Files (*.txt);;All Files (*)"))
                
            #Default relation's name
            f=str(filename.toUtf8()).split('/') #Split the full path
            defname=f[len(f)-1].lower() #Takes only the lowercase filename
            
        else:
            f=filename.split('/') #Split the full path
            defname=f[len(f)-1].lower() #Takes only the lowercase filename
        
        if len(defname)==0:
            return
        use_csv=True
        
        if defname.endswith(".tlb"):
            defname=defname[:-4]
            use_csv=False #Old format, not using csv
            
        if (defname.endswith(".csv")): #removes the extension
            defname=defname[:-4]
        
        if name==None:
            res=QtGui.QInputDialog.getText(self.Form, QtGui.QApplication.translate("Form", "New relation"),QtGui.QApplication.translate("Form", "Insert the name for the new relation"),
            QtGui.QLineEdit.Normal,defname)
            if res[1]==False or len(res[0])==0:
                return
            self.relations[str(res[0].toUtf8())]=relation.relation(filename,use_csv)
        else:
            self.relations[name]=relation.relation(filename,use_csv)
                
        self.updateRelations()
    def insertTuple(self):
        '''Shows an input dialog and inserts the inserted tuple into the selected relation'''
        res=QtGui.QInputDialog.getText(self.Form, QtGui.QApplication.translate("Form", "New relation"),QtGui.QApplication.translate("Form", "Insert the values, comma separated"),
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
        res=QtGui.QInputDialog.getText(self.Form, QtGui.QApplication.translate("Form", "New relation"),QtGui.QApplication.translate("Form", "Remove tuples: insert where condition"),
        QtGui.QLineEdit.Normal,"")
        if res[1]==False:
            return
        
        if self.selectedRelation!=None and self.selectedRelation.delete(str(res[0].toUtf8())) > 0:
            self.showRelation(self.selectedRelation)
            
        return
    def addProduct(self):
        self.txtQuery.insert(u"*")
        self.txtQuery.setFocus()
    def addDifference(self):
        self.txtQuery.insert(u"-")
        self.txtQuery.setFocus()
    def addUnion(self):
        self.txtQuery.insert(u"ᑌ")
        self.txtQuery.setFocus()
    def addIntersection(self):
        self.txtQuery.insert(u"ᑎ")
        self.txtQuery.setFocus()
    def addOLeft(self):
        self.txtQuery.insert(u"ᐅLEFTᐊ")
        self.txtQuery.setFocus()
    def addJoin(self):
        self.txtQuery.insert(u"ᐅᐊ")
        self.txtQuery.setFocus()
    def addORight(self):
        self.txtQuery.insert(u"ᐅRIGHTᐊ")
        self.txtQuery.setFocus()
    def addOuter(self):
        self.txtQuery.insert(u"ᐅFULLᐊ")
        self.txtQuery.setFocus()
    def addProjection(self):
        self.txtQuery.insert(u"π")
        self.txtQuery.setFocus()
    def addSelection(self):
        self.txtQuery.insert(u"σ")
        self.txtQuery.setFocus()
    def addRename(self):
        self.txtQuery.insert(u"ρ")
        self.txtQuery.setFocus()
    def addArrow(self):
        self.txtQuery.insert(u"➡")
        self.txtQuery.setFocus()
        
    def setupUi(self, Form):
        self.Form=Form
        Form.setObjectName("Form")
        Form.resize(932,592)
        Form.setMinimumSize(QtCore.QSize(100,50))
        self.verticalLayout_7 = QtGui.QVBoxLayout(Form)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.verticalLayout_4 = QtGui.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_4 = QtGui.QGroupBox(Form)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_8 = QtGui.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.cmdAbout = QtGui.QPushButton(self.groupBox_4)
        self.cmdSurvey = QtGui.QPushButton(self.groupBox_4)
        self.cmdAbout.setObjectName("cmdAbout")
        self.cmdSurvey.setObjectName("cmdSurvey")
        self.verticalLayout_8.addWidget(self.cmdAbout)
        self.verticalLayout_8.addWidget(self.cmdSurvey)
        self.verticalLayout_4.addWidget(self.groupBox_4)
        self.groupBox = QtGui.QGroupBox(Form)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.cmdProduct = QtGui.QPushButton(self.groupBox)
        self.cmdProduct.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdProduct.setObjectName("cmdProduct")
        self.verticalLayout.addWidget(self.cmdProduct)
        self.cmdDifference = QtGui.QPushButton(self.groupBox)
        self.cmdDifference.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdDifference.setObjectName("cmdDifference")
        self.verticalLayout.addWidget(self.cmdDifference)
        self.cmdUnion = QtGui.QPushButton(self.groupBox)
        self.cmdUnion.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdUnion.setObjectName("cmdUnion")
        self.verticalLayout.addWidget(self.cmdUnion)
        self.cmdIntersection = QtGui.QPushButton(self.groupBox)
        self.cmdIntersection.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdIntersection.setObjectName("cmdIntersection")
        self.verticalLayout.addWidget(self.cmdIntersection)
        self.cmdJoin = QtGui.QPushButton(self.groupBox)
        self.cmdJoin.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdJoin.setObjectName("cmdJoin")
        self.verticalLayout.addWidget(self.cmdJoin)
        self.cmdOuterLeft = QtGui.QPushButton(self.groupBox)
        self.cmdOuterLeft.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdOuterLeft.setObjectName("cmdOuterLeft")
        self.verticalLayout.addWidget(self.cmdOuterLeft)
        self.cmdOuterRight = QtGui.QPushButton(self.groupBox)
        self.cmdOuterRight.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdOuterRight.setObjectName("cmdOuterRight")
        self.verticalLayout.addWidget(self.cmdOuterRight)
        self.cmdOuter = QtGui.QPushButton(self.groupBox)
        self.cmdOuter.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdOuter.setObjectName("cmdOuter")
        self.verticalLayout.addWidget(self.cmdOuter)
        self.cmdProjection = QtGui.QPushButton(self.groupBox)
        self.cmdProjection.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdProjection.setObjectName("cmdProjection")
        self.verticalLayout.addWidget(self.cmdProjection)
        self.cmdSelection = QtGui.QPushButton(self.groupBox)
        self.cmdSelection.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdSelection.setObjectName("cmdSelection")
        self.verticalLayout.addWidget(self.cmdSelection)
        self.cmdRename = QtGui.QPushButton(self.groupBox)
        self.cmdRename.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdRename.setObjectName("cmdRename")
        self.verticalLayout.addWidget(self.cmdRename)
        self.cmdArrow = QtGui.QPushButton(self.groupBox)
        self.cmdArrow.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdArrow.setObjectName("cmdArrow")
        self.verticalLayout.addWidget(self.cmdArrow)
        self.verticalLayout_6.addLayout(self.verticalLayout)
        self.verticalLayout_4.addWidget(self.groupBox)
        spacerItem = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem)
        self.horizontalLayout_4.addLayout(self.verticalLayout_4)
        
        
        self.centerLayout = QtGui.QVBoxLayout()
        self.centerLayout.setObjectName("centerLayout")
        
        
        self.table = QtGui.QTreeWidget(Form) #QtGui.QTableView(Form)
        self.table.setAlternatingRowColors(True)
        self.table.setRootIsDecorated(False)
        self.table.setObjectName("table")
        self.showRelation(self.selectedRelation)
        self.centerLayout.addWidget(self.table)
        
        self.cmdInsert = QtGui.QPushButton(self.groupBox)
        self.cmdInsert.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdInsert.setObjectName("cmdInsert")
        self.cmdDelete = QtGui.QPushButton(self.groupBox)
        self.cmdDelete.setMaximumSize(QtCore.QSize(16777215,16777215))
        self.cmdDelete.setObjectName("cmdDelete")
        self.bottomButtonsLayout = QtGui.QHBoxLayout()
        self.bottomButtonsLayout.setObjectName("bottomButtonsLayout")
        self.bottomButtonsLayout.addWidget(self.cmdInsert)
        self.bottomButtonsLayout.addWidget(self.cmdDelete)
        
        self.centerLayout.addLayout(self.bottomButtonsLayout)
        self.horizontalLayout_4.addLayout(self.centerLayout)
        
        
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.groupBox_2 = QtGui.QGroupBox(Form)
        self.groupBox_2.setMaximumSize(QtCore.QSize(200,16777215))
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.lstRelations = QtGui.QListWidget(self.groupBox_2)
        self.lstRelations.setMaximumSize(QtCore.QSize(300,16777215))
        self.lstRelations.setObjectName("lstRelations")
        self.verticalLayout_5.addWidget(self.lstRelations)
        self.cmdLoad = QtGui.QPushButton(self.groupBox_2)
        self.cmdLoad.setObjectName("cmdLoad")
        self.verticalLayout_5.addWidget(self.cmdLoad)
        self.cmdUnload = QtGui.QPushButton(self.groupBox_2)
        self.cmdUnload.setObjectName("cmdUnload")
        self.cmdSave = QtGui.QPushButton(self.groupBox_2)
        self.cmdSave.setObjectName("cmdSave")
        self.verticalLayout_5.addWidget(self.cmdSave)
        self.verticalLayout_5.addWidget(self.cmdUnload)
        
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.groupBox_3 = QtGui.QGroupBox(Form)
        self.groupBox_3.setMaximumSize(QtCore.QSize(200,16777215))
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout_6 = QtGui.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.lstAttributes = QtGui.QListWidget(self.groupBox_3)
        self.lstAttributes.setMaximumSize(QtCore.QSize(300,16777215))
        self.lstAttributes.setObjectName("lstAttributes")
        self.horizontalLayout_6.addWidget(self.lstAttributes)
        self.verticalLayout_3.addWidget(self.groupBox_3)
        self.horizontalLayout_4.addLayout(self.verticalLayout_3)
        self.verticalLayout_7.addLayout(self.horizontalLayout_4)
        
        
        
        
        self.queryLayout = QtGui.QHBoxLayout()
        self.queryLayout.setObjectName("queryLayout")
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName("label")
        self.queryLayout.addWidget(self.label)
        self.txtResult = QtGui.QLineEdit(Form)
        self.txtResult.setMaximumSize(QtCore.QSize(70,16777215))
        self.txtResult.setObjectName("txtResult")
        self.queryLayout.addWidget(self.txtResult)
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName("label_2")
        self.queryLayout.addWidget(self.label_2)
        self.txtQuery = QtGui.QLineEdit(Form)
        self.txtQuery.setObjectName("txtQuery")
        self.queryLayout.addWidget(self.txtQuery)
        self.cmdExecute = QtGui.QPushButton(Form)
        self.cmdExecute.setAutoDefault(False)
        self.cmdExecute.setDefault(True)
        self.cmdExecute.setFlat(False)
        self.cmdExecute.setObjectName("cmdExecute")
        self.queryLayout.addWidget(self.cmdExecute)
        
        self.cmdAdvanced = QtGui.QPushButton(Form)
        self.cmdAdvanced.setAutoDefault(False)
        self.cmdAdvanced.setFlat(False)
        self.cmdAdvanced.setObjectName("cmdAdvanced")
        self.queryLayout.addWidget(self.cmdAdvanced)
        
        
        self.advancedBox = QtGui.QGroupBox(Form)
        self.advancedBox.setObjectName("advancedBox")
        self.advancedLayout = QtGui.QHBoxLayout(self.advancedBox)
        self.advancedLayout.setObjectName("AdvancedLayout")
        self.advancedBox.hide()
        
        self.cmdOptimize = QtGui.QPushButton(Form)
        self.cmdOptimize.setAutoDefault(False)
        self.cmdOptimize.setFlat(False)
        self.cmdOptimize.setObjectName("cmdOptimize")
        self.advancedLayout.addWidget(self.cmdOptimize)
        
        self.cmdUndoOptimize = QtGui.QPushButton(Form)
        self.cmdUndoOptimize.setAutoDefault(False)
        self.cmdUndoOptimize.setDefault(True)
        self.cmdUndoOptimize.setFlat(False)
        self.cmdUndoOptimize.setObjectName("cmdUndoOptimize")
        self.advancedLayout.addWidget(self.cmdUndoOptimize)
        
        
        self.savedQ= QtGui.QComboBox(Form)
        self.savedQ.addItem(QtGui.QApplication.translate("Form", "Select query"),QtCore.QVariant(None))
        self.advancedLayout.addWidget(self.savedQ)
        
        self.cmdSaveQ = QtGui.QPushButton(Form)
        self.cmdSaveQ.setAutoDefault(False)
        self.cmdSaveQ.setFlat(False)
        self.cmdSaveQ.setObjectName("cmdSaveQ")
        self.advancedLayout.addWidget(self.cmdSaveQ)
        
        
        
        self.verticalLayout_7.addLayout(self.queryLayout)
        self.verticalLayout_7.addWidget(self.advancedBox)
        
        self.label.setBuddy(self.txtResult)
        self.label_2.setBuddy(self.txtQuery)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.txtQuery,QtCore.SIGNAL("returnPressed()"),self.execute)
        QtCore.QObject.connect(self.cmdAbout,QtCore.SIGNAL("clicked()"),self.showAbout)
        QtCore.QObject.connect(self.cmdSurvey,QtCore.SIGNAL("clicked()"),self.showSurvey)
        QtCore.QObject.connect(self.cmdProduct,QtCore.SIGNAL("clicked()"),self.addProduct)
        QtCore.QObject.connect(self.cmdDifference,QtCore.SIGNAL("clicked()"),self.addDifference)
        QtCore.QObject.connect(self.cmdUnion,QtCore.SIGNAL("clicked()"),self.addUnion)
        QtCore.QObject.connect(self.cmdIntersection,QtCore.SIGNAL("clicked()"),self.addIntersection)
        QtCore.QObject.connect(self.cmdOuterLeft,QtCore.SIGNAL("clicked()"),self.addOLeft)
        QtCore.QObject.connect(self.cmdJoin,QtCore.SIGNAL("clicked()"),self.addJoin)
        QtCore.QObject.connect(self.cmdOuterRight,QtCore.SIGNAL("clicked()"),self.addORight)
        QtCore.QObject.connect(self.cmdOuter,QtCore.SIGNAL("clicked()"),self.addOuter)
        QtCore.QObject.connect(self.cmdProjection,QtCore.SIGNAL("clicked()"),self.addProjection)
        QtCore.QObject.connect(self.cmdSelection,QtCore.SIGNAL("clicked()"),self.addSelection)
        QtCore.QObject.connect(self.cmdRename,QtCore.SIGNAL("clicked()"),self.addRename)
        QtCore.QObject.connect(self.cmdArrow,QtCore.SIGNAL("clicked()"),self.addArrow)
        QtCore.QObject.connect(self.cmdExecute,QtCore.SIGNAL("clicked()"),self.execute)
        QtCore.QObject.connect(self.cmdAdvanced,QtCore.SIGNAL("clicked()"),self.toggle_advanced)
        QtCore.QObject.connect(self.cmdOptimize,QtCore.SIGNAL("clicked()"),self.optimize)
        QtCore.QObject.connect(self.cmdUndoOptimize,QtCore.SIGNAL("clicked()"),self.undo_optimize)
        QtCore.QObject.connect(self.cmdSaveQ,QtCore.SIGNAL("clicked()"),self.save_query)
        QtCore.QObject.connect(self.cmdLoad,QtCore.SIGNAL("clicked()"),self.loadRelation)
        QtCore.QObject.connect(self.cmdSave,QtCore.SIGNAL("clicked()"),self.saveRelation)
        QtCore.QObject.connect(self.cmdUnload,QtCore.SIGNAL("clicked()"),self.unloadRelation)
        QtCore.QObject.connect(self.cmdInsert,QtCore.SIGNAL("clicked()"),self.insertTuple)
        QtCore.QObject.connect(self.cmdDelete,QtCore.SIGNAL("clicked()"),self.deleteTuple)
        QtCore.QObject.connect(self.lstRelations,QtCore.SIGNAL("itemDoubleClicked(QListWidgetItem*)"),self.printRelation)
        QtCore.QObject.connect(self.lstRelations,QtCore.SIGNAL("itemClicked(QListWidgetItem*)"),self.showAttributes)
        QtCore.QObject.connect(self.savedQ,QtCore.SIGNAL("currentIndexChanged(int)"),self.load_query)
        
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.txtResult,self.txtQuery)
        Form.setTabOrder(self.txtQuery,self.cmdExecute)
        Form.setTabOrder(self.txtQuery,self.cmdAdvanced)
        Form.setTabOrder(self.txtQuery,self.cmdOptimize)
        Form.setTabOrder(self.txtQuery,self.cmdUndoOptimize)
        Form.setTabOrder(self.txtQuery,self.savedQ)
        Form.setTabOrder(self.txtQuery,self.cmdSaveQ)
        Form.setTabOrder(self.lstRelations,self.cmdLoad)
        Form.setTabOrder(self.cmdLoad,self.cmdUnload)
        Form.setTabOrder(self.cmdLoad,self.cmdSave)
        Form.setTabOrder(self.cmdUnload,self.lstAttributes)
        Form.setTabOrder(self.lstAttributes,self.table)
        Form.setTabOrder(self.table,self.cmdProduct)
        Form.setTabOrder(self.cmdProduct,self.cmdUnion)
        Form.setTabOrder(self.cmdUnion,self.cmdJoin)
        Form.setTabOrder(self.cmdJoin,self.cmdOuterLeft)
        Form.setTabOrder(self.cmdOuterLeft,self.cmdProjection)
        Form.setTabOrder(self.cmdProjection,self.cmdRename)
        Form.setTabOrder(self.cmdRename,self.cmdAbout)
        Form.setTabOrder(self.cmdAbout,self.cmdSurvey)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Relational", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_4.setTitle(QtGui.QApplication.translate("Form", "Menu", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdAbout.setText(QtGui.QApplication.translate("Form", "Docs", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdSurvey.setText(QtGui.QApplication.translate("Form", "Survey", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Form", "Operators", None, QtGui.QApplication.UnicodeUTF8))
        self.advancedBox.setTitle(QtGui.QApplication.translate("Form", "Advanced", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdProduct.setToolTip(QtGui.QApplication.translate("Form", "Product operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdProduct.setText(QtGui.QApplication.translate("Form", "*", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdDifference.setToolTip(QtGui.QApplication.translate("Form", "Difference operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdDifference.setText(QtGui.QApplication.translate("Form", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdUnion.setToolTip(QtGui.QApplication.translate("Form", "Union operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdUnion.setText(QtGui.QApplication.translate("Form", "ᑌ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdIntersection.setToolTip(QtGui.QApplication.translate("Form", "Intersection operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdIntersection.setText(QtGui.QApplication.translate("Form", "ᑎ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdJoin.setToolTip(QtGui.QApplication.translate("Form", "Natural join operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdJoin.setText(QtGui.QApplication.translate("Form", "ᐅᐊ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdOuterLeft.setToolTip(QtGui.QApplication.translate("Form", "Outer join left operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdOuterLeft.setText(QtGui.QApplication.translate("Form", "ᐅLEFTᐊ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdOuterRight.setToolTip(QtGui.QApplication.translate("Form", "Outer join right operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdOuterRight.setText(QtGui.QApplication.translate("Form", "ᐅRIGHTᐊ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdOuter.setToolTip(QtGui.QApplication.translate("Form", "Outer join full operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdOuter.setText(QtGui.QApplication.translate("Form", "ᐅFULLᐊ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdProjection.setToolTip(QtGui.QApplication.translate("Form", "Projection operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdProjection.setText(QtGui.QApplication.translate("Form", "π", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdSelection.setToolTip(QtGui.QApplication.translate("Form", "Selection operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdSelection.setText(QtGui.QApplication.translate("Form", "σ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdRename.setToolTip(QtGui.QApplication.translate("Form", "Rename operator", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdRename.setText(QtGui.QApplication.translate("Form", "ρ", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdArrow.setToolTip(QtGui.QApplication.translate("Form", "Rename attribute", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdArrow.setText(QtGui.QApplication.translate("Form", "➡", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Form", "Relations", None, QtGui.QApplication.UnicodeUTF8))
        self.lstRelations.setToolTip(QtGui.QApplication.translate("Form", "List all the relations.\n"
"Double click on a relation to show it in the table.", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdLoad.setToolTip(QtGui.QApplication.translate("Form", "Loads a relation from a file", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdLoad.setText(QtGui.QApplication.translate("Form", "Load relation", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdSave.setToolTip(QtGui.QApplication.translate("Form", "Saves a relation to a file", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdSave.setText(QtGui.QApplication.translate("Form", "Save relation", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdUnload.setToolTip(QtGui.QApplication.translate("Form", "Unloads a relation", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdUnload.setText(QtGui.QApplication.translate("Form", "Unload relation", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdInsert.setText(QtGui.QApplication.translate("Form", "Insert", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdDelete.setText(QtGui.QApplication.translate("Form", "Delete", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_3.setTitle(QtGui.QApplication.translate("Form", "Attributes", None, QtGui.QApplication.UnicodeUTF8))
        self.lstAttributes.setToolTip(QtGui.QApplication.translate("Form", "Shows the attributes of the current relation", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Form", "Query", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Form", "=", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdExecute.setText(QtGui.QApplication.translate("Form", "Execute", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdAdvanced.setText(QtGui.QApplication.translate("Form", "Advanced", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdOptimize.setText(QtGui.QApplication.translate("Form", "Optimize", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdUndoOptimize.setText(QtGui.QApplication.translate("Form", "Undo optimize", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdSaveQ.setText(QtGui.QApplication.translate("Form", "Save query", None, QtGui.QApplication.UnicodeUTF8))

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Form = QtGui.QWidget()
    
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    Form.setWindowTitle("Relational")
    sys.exit(app.exec_())

