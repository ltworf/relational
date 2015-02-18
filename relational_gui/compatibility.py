# -*- coding: utf-8 -*-
# Relational
# Copyright (C) 2011  Salvo "LtWorf" Tomaselli
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
#
# Module to unify the use of both pyqt and pyside

from PyQt4 import QtCore, QtGui

def get_py_str(a):
    '''Returns a python string out of a QString'''
    return unicode(a.toUtf8(), 'utf-8')

def set_utf8_text(component, text):
    component.setText(QtCore.QString.fromUtf8(text))

def get_filename(filename):
    return str(filename.toUtf8())

def add_list_item(l, item):
    history_item = QtCore.QString()
    history_item.append(item)
    hitem = QtGui.QListWidgetItem(None, 0)
    hitem.setText(history_item)
    l.addItem(hitem)
    l.setCurrentItem(hitem)
