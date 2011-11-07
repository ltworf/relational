# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'relational_pyside/rel_edit.ui'
#
# Created: Sat Oct 22 15:25:32 2011
#      by: pyside-uic 0.2.13 running on PySide 1.0.7
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(594, 444)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cmdAddTuple = QtGui.QPushButton(self.groupBox)
        self.cmdAddTuple.setObjectName("cmdAddTuple")
        self.verticalLayout.addWidget(self.cmdAddTuple)
        self.cmdRemoveTuple = QtGui.QPushButton(self.groupBox)
        self.cmdRemoveTuple.setObjectName("cmdRemoveTuple")
        self.verticalLayout.addWidget(self.cmdRemoveTuple)
        self.cmdAddColumn = QtGui.QPushButton(self.groupBox)
        self.cmdAddColumn.setObjectName("cmdAddColumn")
        self.verticalLayout.addWidget(self.cmdAddColumn)
        self.cmdRemoveColumn = QtGui.QPushButton(self.groupBox)
        self.cmdRemoveColumn.setObjectName("cmdRemoveColumn")
        self.verticalLayout.addWidget(self.cmdRemoveColumn)
        self.horizontalLayout.addWidget(self.groupBox)
        self.table = QtGui.QTableWidget(Dialog)
        self.table.setObjectName("table")
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.horizontalLayout.addWidget(self.table)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Dialog.reject)
        QtCore.QObject.connect(self.cmdAddColumn, QtCore.SIGNAL("clicked()"), Dialog.addColumn)
        QtCore.QObject.connect(self.cmdRemoveColumn, QtCore.SIGNAL("clicked()"), Dialog.deleteColumn)
        QtCore.QObject.connect(self.cmdAddTuple, QtCore.SIGNAL("clicked()"), Dialog.addRow)
        QtCore.QObject.connect(self.cmdRemoveTuple, QtCore.SIGNAL("clicked()"), Dialog.deleteRow)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Relation editor", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdAddTuple.setText(QtGui.QApplication.translate("Dialog", "Add tuple", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdRemoveTuple.setText(QtGui.QApplication.translate("Dialog", "Remove tuple", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdAddColumn.setText(QtGui.QApplication.translate("Dialog", "Add column", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdRemoveColumn.setText(QtGui.QApplication.translate("Dialog", "Remove column", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Remember that new relations and modified relations are not automatically saved", None, QtGui.QApplication.UnicodeUTF8))

