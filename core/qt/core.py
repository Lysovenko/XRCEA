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
from ..application import APPLICATION, icon_file
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QSettings, QTimer, QSignalMapper
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QApplication,
                             QShortcut, QWidget,
                             QMdiSubWindow, QMdiArea)
from PyQt5.QtGui import QIcon
from .menu import MDIMenu
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


class Face(QMainWindow):

    def __init__(self):
        super().__init__()
        _DATA["MDI area"] = self.mdiArea = QMdiArea()
        _DATA["Main window"] = self
        self.just_created = True
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)
        self.statusbar = self.statusBar()
        self.initUI()
        _DATA["Settings"] = self.settings = QSettings('XRCEA', 'XRCEA')
        geometry = self.settings.value('geometry', b'')
        self.restoreGeometry(geometry)
        self.setWindowIcon(QIcon(icon_file("logo")))
        self.show()

    def initUI(self):
        self.menu = MDIMenu(self, self.mdiArea)
        # self.toolbar = self.addToolBar('Exit')
        mdi = self.mdiArea
        self.setCentralWidget(mdi)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle("HvosTiSol")

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            try:
                self.t_dialogs.stop()
            except RuntimeError:
                pass
            else:
                self.t_dialogs.deleteLater()
            event.accept()

    def writeSettings(self):
        geometry = self.saveGeometry()
        self.settings.setValue('geometry', geometry)

    def toggleMenu(self, state):
        if state:
            self.statusbar.show()
        else:
            self.statusbar.hide()

    def showEvent(self, event):
        if self.just_created:
            self.just_created = False
            for e in APPLICATION.on_start:
                e()

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def activeMdiChild(self):
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow:
            return activeSubWindow.widget()
        return None


def _check_dialogs(self):
    dlg = _get_dialog()
    while dlg is not None:
        dlg()
        dlg = _get_dialog()


def main():
    app = QApplication(sys.argv)
    APPLICATION.compman.introduce()
    Face()
    t_dialogs = QTimer()
    t_dialogs.start(250)
    t_dialogs.timeout.connect(_check_dialogs)
    outcode = app.exec_()
    APPLICATION.compman.terminate(True)
    APPLICATION.settings.save()
    sys.exit(outcode)
# http://zetcode.com/gui/pyqt5/firstprograms/


def show_vi(vi_obj):
    if isinstance(vi_obj, Plot):
        from .plot import show_plot_window
        show_plot_window(vi_obj)


class MDISubWindow(QMdiSubWindow):
    def __init__(self, vi_obj):
        QMdiSubWindow.__init__(self)
        self.vi_obj = vi_obj
        if vi_obj.name:
            self.setWindowTitle(vi_obj.name)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.after_close = []
        for i in ("set_name", "set_icon", "add_shortcut", "is_active"):
            vi_obj.gui_functions[i] = getattr(self, i)
        vi_obj.gui_functions["%SubWindow%"] = self

    def set_name(self, name):
        self.setWindowTitle(name)

    def set_icon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def closeEvent(self, event):
        stop_close = False
        if getattr(self.vi_obj, "close_lock", None):
            if QMessageBox.warning(
                    self, self.vi_obj.close_lock.title,
                    self.vi_obj.close_lock.question,
                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.No:
                stop_close = True
        if stop_close:
            event.ignore()
        else:
            self.vi_obj.gui_functions.clear()
            for i in self.after_close:
                i(self)
            self.vi_obj.currently_alive = False
            event.accept()

    def add_shortcut(self, key, func):
        sk = QShortcut(QKeySequence(key), self)
        sk.activated.connect(func)

    def is_active(self):
        return self.isActiveWindow()


def clearLayout(layout):
    for i in range(layout.count() - 1, -1, -1):
        child = layout.takeAt(i)
        if child.widget() is not None:
            child.widget().deleteLater()
        elif child.layout() is not None:
            clearLayout(child.layout())


def print_status(status):
    try:
        _DATA["Main window"].statusbar.showMessage(str(status))
    except KeyError:
        print(status)
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
