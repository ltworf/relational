# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'relational_gui/rel_edit.ui'
#
# Created: Fri Dec 27 00:05:54 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(594, 444)
        self.verticalLayout_2 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.cmdAddTuple = QtGui.QPushButton(self.groupBox)
        self.cmdAddTuple.setObjectName(_fromUtf8("cmdAddTuple"))
        self.verticalLayout.addWidget(self.cmdAddTuple)
        self.cmdRemoveTuple = QtGui.QPushButton(self.groupBox)
        self.cmdRemoveTuple.setObjectName(_fromUtf8("cmdRemoveTuple"))
        self.verticalLayout.addWidget(self.cmdRemoveTuple)
        self.cmdAddColumn = QtGui.QPushButton(self.groupBox)
        self.cmdAddColumn.setObjectName(_fromUtf8("cmdAddColumn"))
        self.verticalLayout.addWidget(self.cmdAddColumn)
        self.cmdRemoveColumn = QtGui.QPushButton(self.groupBox)
        self.cmdRemoveColumn.setObjectName(_fromUtf8("cmdRemoveColumn"))
        self.verticalLayout.addWidget(self.cmdRemoveColumn)
        self.horizontalLayout.addWidget(self.groupBox)
        self.table = QtGui.QTableWidget(Dialog)
        self.table.setObjectName(_fromUtf8("table"))
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.horizontalLayout.addWidget(self.table)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.cmdAddColumn, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.addColumn)
        QtCore.QObject.connect(self.cmdRemoveColumn, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.deleteColumn)
        QtCore.QObject.connect(self.cmdAddTuple, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.addRow)
        QtCore.QObject.connect(self.cmdRemoveTuple, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.deleteRow)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Relation editor", None))
        self.groupBox.setTitle(_translate("Dialog", "Edit", None))
        self.cmdAddTuple.setText(_translate("Dialog", "Add tuple", None))
        self.cmdRemoveTuple.setText(_translate("Dialog", "Remove tuple", None))
        self.cmdAddColumn.setText(_translate("Dialog", "Add column", None))
        self.cmdRemoveColumn.setText(_translate("Dialog", "Remove column", None))
        self.label.setText(_translate("Dialog", "Remember that new relations and modified relations are not automatically saved", None))

