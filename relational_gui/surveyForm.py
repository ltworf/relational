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

import httplib
import urllib


class surveyForm (QtGui.QWidget):
    '''This class is the form used for the survey, needed to intercept the events.
    It also sends the data with http POST to a page hosted on galileo'''
    def setUi(self,ui):
        self.ui=ui
    def send(self):
        '''Sends the data inserted in the form'''
        #Creates the string
        post="Relational algebra\n"
        post+="system:" + str(self.ui.txtSystem.text().toUtf8())+ "\n"
        post+="country:" + str(self.ui.txtCountry.text().toUtf8())+ "\n"
        post+="school:" + str(self.ui.txtSchool.text().toUtf8())+ "\n"
        post+="age:" + str(self.ui.txtAge.text().toUtf8())+ "\n"
        post+="find:" + str(self.ui.txtFind.text().toUtf8())+ "\n"
        post+="comments:" + str(self.ui.txtComments.toPlainText().toUtf8())
    
        #Clears the form
        self.ui.txtSystem.clear()
        self.ui.txtCountry.clear()
        self.ui.txtSchool.clear()
        self.ui.txtAge.clear()
        self.ui.txtFind.clear()
        self.ui.txtComments.clear()
    
        #sends the string
        params = urllib.urlencode({'survey':post})
        headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
        connection = httplib.HTTPConnection('galileo.dmi.unict.it')
        connection.request("POST","/~ltworf/survey.php",params,headers)
        response=connection.getresponse()
        if response.status!=200:
            QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Error"),QtGui.QApplication.translate("Form", "Unable to send the data!")  )
        else:
            QtGui.QMessageBox.information(None,QtGui.QApplication.translate("Form", "Thanks"),QtGui.QApplication.translate("Form", "Thanks for sending!")  )
      
        self.hide()
