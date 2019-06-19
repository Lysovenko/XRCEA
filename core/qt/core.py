#!/usr/bin/env python3
"""start from here"""
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

import sys
from threading import Lock
from time import time
from ..application import APPLICATION
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QSettings, QTimer, QSignalMapper
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QApplication,
                             QShortcut, QWidget, QTextEdit)
from PyQt5.QtGui import QIcon
from ..vi import Plot
_DATA = {}
_DIALOGS = []
_TASKS = []
_DLG_LOCKER = Lock()


def register_dialog(dlg):
    _DLG_LOCKER.acquire()
    _DIALOGS.append(dlg)
    _DLG_LOCKER.release()


def _get_dialog():
    _DLG_LOCKER.acquire()
    if _TASKS and _TASKS[0][0] <= time():
        rv = _TASKS.pop(0)[1]
    else:
        try:
            rv = _DIALOGS.pop(0)
        except IndexError:
            rv = None
    _DLG_LOCKER.release()
    return rv


def _check_dialogs():
    dlg = _get_dialog()
    while dlg is not None:
        dlg()
        dlg = _get_dialog()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("XRCEA")
    APPLICATION.compman.introduce()
    for e in APPLICATION.on_start:
        e()
    t_dialogs = QTimer()
    t_dialogs.start(250)
    t_dialogs.timeout.connect(_check_dialogs)
    outcode = app.exec_()
    APPLICATION.compman.terminate(True)
    APPLICATION.settings.save()
    sys.exit(outcode)


def show_vi(vi_obj):
    if isinstance(vi_obj, Plot):
        from .plot import show_plot_window
        show_plot_window(vi_obj)


def clearLayout(layout):
    for i in range(layout.count() - 1, -1, -1):
        child = layout.takeAt(i)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())


def print_status(status):
    # DODO: implement
    pass


def copy_to_clipboard(text):
    cb = QApplication.clipboard()
    cb.clear(mode=cb.Clipboard)
    cb.setText(text, mode=cb.Clipboard)


def schedule(at, task):
    _DLG_LOCKER.acquire()
    _TASKS.append((at, task))
    _TASKS.sort()
    _DLG_LOCKER.release()
