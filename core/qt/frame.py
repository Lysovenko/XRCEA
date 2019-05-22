#!/usr/bin/env python3
"""Draw frames"""
# XRCEA (C) 2019 Serhii Lysovenko
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from PyQt5.QtWidgets import (
    QMdiSubWindow, QGridLayout, QLabel, QPushButton,
    QWidget, QSizePolicy)
from PyQt5.QtCore import Qt
from .text import LineEdit
from .core import _DATA
from .lists import CheckedList, VisualList


class VFrame:
    def __init__(self, puzzle):
        # super().__init__(parent)
        self.current_table = None
        self.current_raw = -1
        self.row_spans = {}
        self.err_prone_values = []
        self.all_values = []
        self.post_create = []
        puzzle.set_actors({
            'set_title': self.setWindowTitle,
            'table_new': self.new_table,
            'table_end': self.end_table,
            'table_next_raw': self.table_next_raw,
            'table_put_cell': self.table_put_cell,
            'get_label': self.get_label,
            'get_text': self.get_text,
            'get_spin': self.get_spin,
            'get_button': self.get_button,
            'get_radio': self.get_radio,
            'get_line': self.get_line,
            'get_list': self.get_list,
            'get_checkedlist': self.get_checkedlist})
        puzzle.play()
        for f in self.post_create:
            f()
        del self.post_create
        self.setGeometry(300, 300, 350, 300)
        self.i_am_running = True

    def new_table(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_table = QGridLayout()
        self.current_table.setSpacing(2)

    def end_table(self):
        self.setLayout(self.current_table)
        self.current_table = None

    def table_next_raw(self):
        self.current_raw += 1
        self.current_col = 0
        for i in list(self.row_spans.keys()):
            self.row_spans[i][1] -= 1
            if self.row_spans[i][1] == 0:
                self.row_spans.pop(i)
        while self.current_col in self.row_spans:
            self.current_col += self.row_spans[self.current_col][0]

    def table_put_cell(self, cont, align, colspan,
                       rowspan, expand, border):
        flag = 0
        if expand:
            cont.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # sp = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # sp.setHorizontalStretch(0)
            # sp.setVerticalStretch(0)
            # sp.setHeightForWidth(cont.sizePolicy().hasHeightForWidth())
            # cont.setSizePolicy(sp)
        if align == "right":
            flag |= Qt.AlignRight
        if align == "left":
            flag |= Qt.AlignLeft
        if align == "center":
            flag |= Qt.AlignCenter
        if colspan is None:
            colspan = 1
        if rowspan is None:
            rowspan = 1
        if not border:
            border = 0
        if flag == 0:
            self.current_table.addWidget(
                cont, self.current_raw, self.current_col,
                rowspan, colspan)
        else:
            self.current_table.addWidget(
                cont, self.current_raw, self.current_col,
                rowspan, colspan, flag)
        self.row_spans[self.current_col] = [colspan, rowspan]
        while self.current_col in self.row_spans:
            self.current_col += self.row_spans[self.current_col][0]

    def get_label(self, label):
        return QLabel(str(label))

    def get_text(self, value):
        text = LineEdit(self, value)
        text.setText(str(value))
        self.all_values.append(value)
        self.err_prone_values.append(value)
        return text

    def get_list(self, colnames, value, callback):
        vislist = VisualList(self, colnames, value, callback)
        self.all_values.append(value)
        self.err_prone_values.append(value)
        return vislist

    def get_checkedlist(self, value):
        checkedlist = CheckedList(self, value)
        self.all_values.append(value)
        self.err_prone_values.append(value)
        return checkedlist

    def get_button(self, b_type, name, default=False):
        btn = QPushButton(name)
        if default:
            btn.setDefault(True)
        return btn

    def get_spin(self, begin=0, end=0, value=None):
        spin = QPushButton('spin')
        return spin

    def get_radio(self, title, options, choices, value, onchange, style):
        radio = QPushButton('radio')
        return radio

    def release_values(self):
        for v in self.all_values:
            v.set_updater(None)
            v.set_relevator(None)

    def get_line(self):
        pass

    def closeEvent(self, event):
        self.i_am_running = False

    def __bool__(self):
        return self.i_am_running


class Frame(VFrame, QWidget):
    def __init__(self, puzzle, parent=None):
        QWidget.__init__(self, parent)
        VFrame.__init__(self, puzzle)


def new_frame(puzzle):
    sw = QMdiSubWindow()
    frame = Frame(puzzle)
    sw.setWidget(frame)
    _DATA["MDI area"].addSubWindow(sw)
    sw.show()
    return frame
