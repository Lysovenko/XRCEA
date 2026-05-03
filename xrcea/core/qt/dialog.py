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

import os

try:
    from PyQt6.QtWidgets import QFileDialog, QMessageBox
except ImportError:
    from PyQt5.QtWidgets import QFileDialog, QMessageBox
from .idialog import MNO, MOK, MYES


def print_information(title, info):
    parent = None
    return QMessageBox.information(parent, title, info) == MOK


def print_error(title, info):
    parent = None
    return QMessageBox.critical(parent, title, info) == MOK


def ask_question(title, question):
    parent = None
    return QMessageBox.question(parent, title, question, MYES | MNO) == MYES


def ask_open_filename(title, filename, masks):
    fltr = ";;".join("{1} ({0})".format(*md) for md in masks)

    # 1. Handle the Enum naming difference
    if hasattr(QFileDialog, "Option"):
        # PyQt6 path
        options = QFileDialog.Option(0)  # Initialize empty flag set
        native_flag = QFileDialog.Option.DontUseNativeDialog
    else:
        # PyQt5 path
        options = QFileDialog.Options()
        native_flag = QFileDialog.DontUseNativeDialog

    # 2. Add the flag for Linux/Posix
    if os.name == "posix":
        options |= native_flag

    # 3. Call the dialog
    fname, _h = QFileDialog.getOpenFileName(
        None, title, filename, fltr, options=options
    )

    return fname if fname else None


def ask_save_filename(title, filename, masks):
    fltr = ";;".join("{1} ({0})".format(*md) for md in masks)
    options = QFileDialog.Options()
    if os.name == "posix":
        options |= QFileDialog.DontUseNativeDialog
    fname, _h = QFileDialog.getSaveFileName(
        None, title, filename, fltr, options=options
    )
    if fname:
        return fname
    return None
