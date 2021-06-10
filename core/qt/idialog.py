#!/usr/bin/env python3
"""Draw input dialogs"""
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

import os
from PyQt5.QtWidgets import (
    QVBoxLayout, QDialog, QDialogButtonBox, QLabel, QComboBox, QFileDialog,
    QFormLayout, QLineEdit, QCheckBox, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator
from .text import LineEdit
from .progress import Progress
from ..vi.value import Value


class MyValidator(QValidator):
    def __init__(self, vt, vo):
        QValidator.__init__(self, vo)
        self.vt = vt

    def validate(self, inp, pos):
        try:
            self.vt(str(inp))
        except ValueError:
            return QValidator.Invalid, inp, pos
        return QValidator.Acceptable, inp, pos


def get_widget_value(widget):
    if isinstance(widget, QCheckBox):
        return bool(widget.isChecked())
    if isinstance(widget, QComboBox):
        return int(widget.currentIndex())
    if isinstance(widget, QLineEdit):
        return str(widget.text())


def get_widget_from_value(value, optional=None):
    if isinstance(value, bool):
        rv = QCheckBox()
        rv.setChecked(value)
        return rv
    if isinstance(value, tuple):
        rv = QComboBox()
        for i in value:
            rv.addItem(i)
        if isinstance(optional, int) and 0 <= optional < len(value):
            rv.setCurrentIndex(optional)
        if callable(optional):
            rv.currentIndexChanged.connect(optional)
        return rv
    if isinstance(value, str):
        return QLineEdit(value)
    if isinstance(value, Value):
        return LineEdit(None, value)


class InputDialog(QDialog):
    def __init__(self, title, question, fields, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        self.title = title
        self.parent = parent
        buttonBox = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttonBox.rejected.connect(self.reject)
        buttonBox.accepted.connect(self.accept)
        mainLayout = QVBoxLayout()
        layout = QFormLayout()
        if question:
            layout.addRow(QLabel(question))
        self.edt = []
        self.vals = []
        for f in fields:
            n, f, o = tuple(f)[:3] + (None,) * (3 - len(f))
            if isinstance(f, Value):
                self.vals.append(f)
            type_f = type(f)
            if type_f in {bool, tuple, Value}:
                if callable(o):
                    def fun(*args, opt=o):
                        self.do_actions(opt(*args))
                    o = fun
                ew = get_widget_from_value(f, o)
            else:
                ew = QLineEdit()
                ew.setValidator(MyValidator(type_f, ew))
                if type_f.__name__ == 'Password':
                    ew.setEchoMode(QLineEdit.Password)
                if isinstance(f, dict):
                    if "Filename" in f:
                        ew.setText(str(f["Filename"]))
                        ew.setReadOnly(True)
                        ew.selectionChanged.connect(
                            lambda y=ew, z=f: self.open_filename(y, z))
                else:
                    ew.setText(str(f))
            layout.addRow(QLabel(n), ew)
            self.edt.append((ew, type_f))
        mainLayout.addLayout(layout)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)
        for i, f in enumerate(fields):
            if len(f) > 3:
                wdg = self.edt[i][0]
                if isinstance(wdg, QComboBox):
                    print(wdg.currentIndex(), f[3])
                    if int(wdg.currentIndex()) == f[3]:
                        wdg.currentIndexChanged.emit(f[3])
                    else:
                        wdg.setCurrentIndex(f[3])

    def accept(self):
        for v in self.vals:
            if getattr(v, "had_error", False):
                return
        self.result = result = []
        for editable, type_ in self.edt:
            if type_ in {bool, tuple, dict, Value}:
                res_itm = get_widget_value(editable)
            else:
                res_itm = type_(editable.text())
            result.append(res_itm)
        return QDialog.accept(self)

    def do_actions(self, actions):
        for action, index, value in actions:
            if action == "set":
                self.set_value(index, value)

    def set_value(self, index, value):
        if len(self.edt) <= index:
            raise IndexError("Index of inputs out of range")
        widget = self.edt[index][0]
        if isinstance(widget, QCheckBox):
            if not isinstance(value, bool):
                raise TypeError("Value %d should be of bool type" % (index,))
            widget.setChecked(value)
        if isinstance(widget, QComboBox):
            if not isinstance(value, int):
                raise TypeError("Value %d should be of int type" % (index,))
            widget.setCurrentIndex(value)
        if isinstance(widget, QLineEdit):
            widget.setText(str(value))

    def open_filename(self, editable, fdict):
        fname = editable.text()
        masks = fdict.get("Masks", ())
        fltr = ";;".join("{1} ({0})".format(*md) for md in masks)
        options = QFileDialog.Options()
        if os.name == "posix":
            options |= QFileDialog.DontUseNativeDialog
        fname, h = QFileDialog.getOpenFileName(
            self.parent, self.title, fname, fltr, options=options)
        if fname:
            editable.setText(fname)


def input_dialog(title, question, fields, parent=None):
    dlg = InputDialog(title, question, fields, parent)
    dlg.setWindowModality(Qt.ApplicationModal)
    if dlg.exec_():
        return dlg.result
    return None


class DialogsMixin:
    """Call dialogs with extrawidgets as parent"""
    def input_dialog(self, question, fields):
        return input_dialog(self.vi_obj.name, question, fields, self)

    def print_information(self, info):
        return QMessageBox.information(
            self, self.vi_obj.name, info) == QMessageBox.Ok

    def print_error(self, info):
        return QMessageBox.critical(
            self, self.vi_obj.name, info) == QMessageBox.Ok

    def ask_question(self, question):
        return QMessageBox.question(
            self, self.vi_obj.name, question,
            QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes

    def ask_save_filename(self, filename, masks):
        fltr = ";;".join("{1} ({0})".format(*md) for md in masks)
        options = QFileDialog.Options()
        if os.name == "posix":
            options |= QFileDialog.DontUseNativeDialog
        fname, h = QFileDialog.getSaveFileName(
            self, self.vi_obj.name, filename, fltr, options=options)
        if fname:
            return fname

    def ask_open_filename(self, filename, masks):
        fltr = ";;".join("{1} ({0})".format(*md) for md in masks)
        options = QFileDialog.Options()
        if os.name == "posix":
            options |= QFileDialog.DontUseNativeDialog
        fname, h = QFileDialog.getOpenFileName(
            self, self.vi_obj.name, filename, fltr, options=options)
        if fname:
            return fname

    def bg_process(self, status):
        dlg = Progress(self.vi_obj.name, status, self)
        dlg.setWindowModality(Qt.ApplicationModal)
        dlg.exec_()

    def register_dialogs(self):
        guf = self.vi_obj.gui_functions
        for fun in ("input_dialog", "print_information", "print_error",
                    "ask_question", "ask_save_filename", "ask_open_filename",
                    "bg_process"):
            guf[fun] = getattr(self, fun)
