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
from PyQt5.QtWidgets import QMessageBox, QFileDialog


def print_information(title, info):
    parent = None
    return QMessageBox.information(parent, title, info) == QMessageBox.Ok


def print_error(title, info):
    parent = None
    return QMessageBox.critical(parent, title, info) == QMessageBox.Ok


def ask_question(title, question):
    parent = None
    return QMessageBox.question(
        parent, title, question,
        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes


def ask_open_filename(title, filename, masks):
    fltr = ";;".join("{1} ({0})".format(*md) for md in masks)
    options = QFileDialog.Options()
    if os.name == "posix":
        options |= QFileDialog.DontUseNativeDialog
    fname, _h = QFileDialog.getOpenFileName(
        None, title, filename, fltr, options=options)
    if fname:
        return fname
    return None


def ask_save_filename(title, filename, masks):
    fltr = ";;".join("{1} ({0})".format(*md) for md in masks)
    options = QFileDialog.Options()
    if os.name == "posix":
        options |= QFileDialog.DontUseNativeDialog
    fname, _h = QFileDialog.getSaveFileName(
        None, title, filename, fltr, options=options)
    if fname:
        return fname
    return None
