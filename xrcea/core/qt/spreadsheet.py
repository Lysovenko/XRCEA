#!/usr/bin/env python3
# XRCEA (C) 2020 Serhii Lysovenko
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
"""Show spreadsheets"""

from PyQt5.QtWidgets import (QFormLayout, QWidget, QVBoxLayout, QSplitter,
                             QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from .table import VisualTable
from .core import clearLayout, qMainWindow
from .idialog import DialogsMixin, get_widget_value, get_widget_from_value


class Spreadsheet(qMainWindow):
    def __init__(self, vi_obj):
        super().__init__(vi_obj)
        self.splitter = QSplitter(self)
        self.setCentralWidget(self.splitter)
        self.timers = []
        self.form_edas = []
        self.form = None

    def draw_shape(self, value):
        """Internal. Draw window shape"""
        self.table = vt = VisualTable(self, value)
        vt.set_del_pressed(value.on_del_pressed)
        layout = QVBoxLayout()
        self.form = QFormLayout()
        layout.addLayout(self.form)
        layout.addWidget(vt)
        w = QWidget()
        w.setLayout(layout)
        self.setCentralWidget(w)

    def set_context_menu(self, cmenu):
        self.table.set_context_menu(cmenu)

    def get_selected_cells(self):
        return [(i.row(), i.column()) for i in self.table.selectedIndexes()]

    def set_icon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def add_timer(self, seconds, func):
        timer = QTimer(self)
        timer.start(int(seconds * 1000))
        timer.timeout.connect(func)
        self.timers.append(timer)

    def update_form(self, form, is_editable):
        layout = self.form
        self.form_edas.clear()
        clearLayout(layout)
        for f in form:
            n, f, o = tuple(f)[:3] + (None,) * (3 - len(f))
            if isinstance(f, (bool, tuple)):
                if callable(o):

                    def fun(*args, opt=o):
                        opt(*args)

                    o = fun
            ew = get_widget_from_value(f, o)
            try:
                ew.setReadOnly(not is_editable)
            except AttributeError:
                pass
            if callable(n):
                call = n
                n = QPushButton(n.name)
                n.clicked.connect(
                    lambda x, y=ew, c=call: c(get_widget_value(y)))
                if hasattr(ew, "returnPressed"):
                    ew.returnPressed.connect(
                        lambda y=ew, c=call: c(get_widget_value(y)))
            if ew is None:
                layout.addRow(n)
            else:
                layout.addRow(n, ew)
                self.form_edas.append(ew)

    def get_form_vals(self, which):
        return tuple(get_widget_value(e) for e in self.form_edas)

    def closeEvent(self, event=None, **kwargs):
        for t in self.timers:
            try:
                t.stop()
            except RuntimeError:
                pass
            else:
                t.deleteLater()
        self.timers.clear()
        self.vi_obj.gui_functions.clear()
        self.vi_obj.currently_alive = False


def show_spreadsheet(vi_obj):
    if vi_obj.gui_functions:
        vi_obj.gui_functions["%Window%"].raise_()
        return
    sheet = Spreadsheet(vi_obj)
    vi_obj.gui_functions["%Window%"] = sheet
    sheet.draw_shape(vi_obj.value)
    if vi_obj.icon is not None:
        sheet.set_icon(vi_obj.icon)
    vi_obj.gui_functions["add_timer"] = sheet.add_timer
    vi_obj.gui_functions[
        "set_spreadsheet_context_menu"] = sheet.set_context_menu
    vi_obj.gui_functions["set_form"] = sheet.update_form
    vi_obj.gui_functions["get_form_values"] = sheet.get_form_vals
    vi_obj.gui_functions["get_selected_cells"] = sheet.get_selected_cells
    sheet.register_dialogs()
    sheet.show()
    vi_obj.currently_alive = True
