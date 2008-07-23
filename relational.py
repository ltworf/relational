#!/usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui
import parser
import relation
import maingui

if __name__ == "__main__":
	import sys
	app = QtGui.QApplication(sys.argv)
	Form = QtGui.QWidget()
	
	ui = maingui.Ui_Form()
	ui.setupUi(Form)
	Form.show()
	Form.setWindowTitle("Relational")
	sys.exit(app.exec_())