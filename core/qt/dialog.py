#!/usr/bin/env python3
"""Draw dialogs"""
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


from sys import stderr
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog
from PyQt5.QtCore import Qt
from .frame import VFrame, QPushButton
from .core import _DATA


class Frame(VFrame, QDialog):
    def __init__(self, puzzle, parent=None):
        QDialog.__init__(self, parent)
        VFrame.__init__(self, puzzle)

    def get_button(self, b_type, name, default=False):
        btn = QPushButton(name)
        if default:
            btn.setDefault(True)
        if b_type == "ok":
            btn.clicked.connect(self.accept)
        if b_type == "cancel":
            btn.clicked.connect(self.reject)
        return btn


def run_dialog(puzzle):
    dlg = Frame(puzzle)
    dlg.setWindowModality(Qt.ApplicationModal)
    dlgr = dlg.exec_()
    return bool(dlgr)


def print_information(title, info):
    parent = None
    return QMessageBox.information(parent, title, info) == QMessageBox.Ok


def print_error(title, info):
    try:
        parent = None
        return QMessageBox.critical(parent, title, info) == QMessageBox.Ok
    except KeyError:
        print(title, "\n", info, file=stderr)


def ask_question(title, question):
    parent = None
    return QMessageBox.question(
        parent, title, question,
        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes


def ask_open_filename(title, filename, masks):
    fltr = ";;".join("{1} ({0})".format(*md) for md in masks)
    fname, h = QFileDialog.getOpenFileName(
        None, title, filename, fltr)
    if fname:
        return fname


def ask_save_filename(title, filename, masks):
    fltr = ";;".join("{1} ({0})".format(*md) for md in masks)
    fname, h = QFileDialog.getSaveFileName(
        None, title, filename, fltr)
    if fname:
        return fname

