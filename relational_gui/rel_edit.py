# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'relational_gui/rel_edit.ui'
#
# Created: Sat Oct 22 15:25:32 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

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
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Relation editor", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdAddTuple.setText(QtGui.QApplication.translate("Dialog", "Add tuple", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdRemoveTuple.setText(QtGui.QApplication.translate("Dialog", "Remove tuple", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdAddColumn.setText(QtGui.QApplication.translate("Dialog", "Add column", None, QtGui.QApplication.UnicodeUTF8))
        self.cmdRemoveColumn.setText(QtGui.QApplication.translate("Dialog", "Remove column", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Dialog", "Remember that new relations and modified relations are not automatically saved", None, QtGui.QApplication.UnicodeUTF8))

