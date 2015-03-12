# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'relational_gui/rel_edit.ui'
#
# Created: Mon Feb 23 15:16:57 2015
#      by: PyQt5 UI code generator 5.3.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(594, 444)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.cmdAddTuple = QtWidgets.QPushButton(self.groupBox)
        self.cmdAddTuple.setObjectName("cmdAddTuple")
        self.verticalLayout.addWidget(self.cmdAddTuple)
        self.cmdRemoveTuple = QtWidgets.QPushButton(self.groupBox)
        self.cmdRemoveTuple.setObjectName("cmdRemoveTuple")
        self.verticalLayout.addWidget(self.cmdRemoveTuple)
        self.cmdAddColumn = QtWidgets.QPushButton(self.groupBox)
        self.cmdAddColumn.setObjectName("cmdAddColumn")
        self.verticalLayout.addWidget(self.cmdAddColumn)
        self.cmdRemoveColumn = QtWidgets.QPushButton(self.groupBox)
        self.cmdRemoveColumn.setObjectName("cmdRemoveColumn")
        self.verticalLayout.addWidget(self.cmdRemoveColumn)
        self.horizontalLayout.addWidget(self.groupBox)
        self.table = QtWidgets.QTableWidget(Dialog)
        self.table.setObjectName("table")
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.horizontalLayout.addWidget(self.table)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.cmdAddColumn.clicked.connect(Dialog.addColumn)
        self.cmdRemoveColumn.clicked.connect(Dialog.deleteColumn)
        self.cmdAddTuple.clicked.connect(Dialog.addRow)
        self.cmdRemoveTuple.clicked.connect(Dialog.deleteRow)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Relation editor"))
        self.groupBox.setTitle(_translate("Dialog", "Edit"))
        self.cmdAddTuple.setText(_translate("Dialog", "Add tuple"))
        self.cmdRemoveTuple.setText(_translate("Dialog", "Remove tuple"))
        self.cmdAddColumn.setText(_translate("Dialog", "Add column"))
        self.cmdRemoveColumn.setText(_translate("Dialog", "Remove column"))
        self.label.setText(_translate("Dialog", "Remember that new relations and modified relations are not automatically saved"))

