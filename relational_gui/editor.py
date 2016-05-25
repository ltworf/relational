# Relational
# Copyright (C) 2016  Salvo "LtWorf" Tomaselli
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
# This module provides a classes to represent relations and to perform
# relational operations on them.

from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPalette
from PyQt5.QtGui import QTextCharFormat


class Editor(QPlainTextEdit):

    def __init__(self, *args, **kwargs):
        super(Editor, self).__init__(*args, **kwargs)

        self._cursor_moved()
        self.cursorPositionChanged.connect(self._cursor_moved)

    def _cursor_moved(self):
        selections = []

        # Current line
        cur_line = QTextEdit.ExtraSelection()
        bgcolor = QPalette().color(
            QPalette.Normal,
            QPalette.Window
        ).lighter()
        cur_line.format.setBackground(bgcolor)
        cur_line.format.setProperty(
            QTextCharFormat.FullWidthSelection,
            True
        )
        cur_line.cursor = self.textCursor()
        cur_line.cursor.clearSelection()
        selections.append(cur_line)

        # Apply the selections
        self.setExtraSelections(selections)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            event.accept()
            self.zoom(1 if event.angleDelta().y()>0 else -1)
        else:
            super(Editor, self).wheelEvent(event)

    def zoom(self, incr):
        font = self.font()
        point_size = font.pointSize()
        point_size += incr
        font.setPointSize(point_size)
        self.setFont(font)
