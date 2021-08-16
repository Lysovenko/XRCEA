#!/usr/bin/env python3
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
"""Show listings"""

from PyQt5.QtWidgets import (QFormLayout, QGroupBox, QVBoxLayout, QSplitter,
                             QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from .lists import VisualList
from .core import clearLayout, qMainWindow
from .idialog import DialogsMixin, get_widget_value, get_widget_from_value


class Lister(qMainWindow):
    def __init__(self, vi_obj):
        super().__init__(vi_obj)
        self.splitter = QSplitter(self)
        self.setCentralWidget(self.splitter)
        self.timers = []
        self.form_edas = []
        self.forms = []

    def draw_shape(self, titles, values, styles):
        """Internal. Draw window shape"""
        gr_boxes = []
        self.lists = lists = []
        for tr_no, (l_title, colnames) in enumerate(titles):
            gr_boxes.append(QGroupBox(l_title))
            vl = VisualList(self, colnames, values[tr_no], styles)
            lists.append(vl)
            layout = QVBoxLayout()
            self.forms.append(QFormLayout())
            self.form_edas.append([])
            layout.addLayout(self.forms[-1])
            layout.addWidget(vl)
            gr_boxes[-1].setLayout(layout)
        for grb in gr_boxes:
            self.splitter.addWidget(grb)
        self.splitter.setOrientation(Qt.Vertical)

    def set_choicer(self, choicer, separate_items=False, holder=None):
        """ Set choicer function which is called when list
        item is activated.
        choicer gets appropriate list item if separate_items is True ---
        second parameter of choicer is number of column """
        if holder is not None:
            self.lists[holder].set_choicer(choicer, separate_items)
        else:
            for vl in self.lists:
                vl.set_choicer(choicer, separate_items)

    def set_context_menu(self, cmenu, holder=None):
        if holder is not None:
            self.lists[holder].set_context_menu(cmenu)
        else:
            for vl in self.lists:
                vl.set_context_menu(cmenu)

    def set_icon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def add_timer(self, seconds, func):
        timer = QTimer(self)
        timer.start(int(seconds * 1000))
        timer.timeout.connect(func)
        self.timers.append(timer)

    def update_form(self, form, which, is_editable):
        layout = self.forms[which]
        self.form_edas[which].clear()
        clearLayout(layout)
        for n, f in form:
            ew = get_widget_from_value(f)
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
                self.form_edas[which].append(ew)

    def get_form_vals(self, which):
        return tuple(get_widget_value(e) for e in self.form_edas[which])

    def closeEvent(self, event=None):
        if event is not None:
            if super().closeEvent(event, False):
                return
        for t in self.timers:
            try:
                t.stop()
            except RuntimeError:
                pass
            else:
                t.deleteLater()
        self.timers.clear()
        self.vi_obj.currently_alive = False


def show_lister(vi_obj):
    if vi_obj.gui_functions:
        vi_obj.gui_functions["%Window%"].raise_()
        return
    lister = Lister(vi_obj)
    vi_obj.gui_functions["%Window%"] = lister
    lister.draw_shape(vi_obj.titles, vi_obj.lvalues, vi_obj.styles)
    if vi_obj.icon is not None:
        lister.set_icon(vi_obj.icon)
    vi_obj.gui_functions["set_choicer"] = lister.set_choicer
    vi_obj.gui_functions["add_timer"] = lister.add_timer
    vi_obj.gui_functions["set_list_context_menu"] = lister.set_context_menu
    vi_obj.gui_functions["set_form"] = lister.update_form
    vi_obj.gui_functions["get_form_values"] = lister.get_form_vals
    lister.register_dialogs()
    lister.show()
    vi_obj.currently_alive = True
