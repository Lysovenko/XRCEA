#!/usr/bin/env python3
"""control the menu"""
# xrcea (C) 2019 Serhii Lysovenko
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

from ..application import APPLICATION
from PyQt5.QtCore import QSignalMapper
from PyQt5.QtWidgets import (QAction, QWidget)
from PyQt5.QtGui import QIcon, QKeySequence


class SDIMenu:
    def __init__(self, frame):
        self.menu = APPLICATION.menu
        self.menu_bar = frame.menuBar()
        self.frame = frame
        # MDI_area.subWindowActivated.connect(self.update_menu)
        self.window_mapper = QSignalMapper(self.frame)
        # self.window_mapper.mapped[QWidget].connect(self.set_active_subwindow)
        # self.create_window_actions()
        self.main_menu_set = set()
        self.update_menu()

    def update_menu(self):
        items = self.menu.get_items((), self.frame.vi_obj.menu)
        iset = set(i[0] for i in items)
        if iset != self.main_menu_set:
            menubar = self.menu_bar
            menubar.clear()
            for i in items:
                smenu = menubar.addMenu(i[0])
                smenu.aboutToShow.connect(lambda p=(i[0],), s=smenu:
                                          self.show_path(p, s))

    def show_path(self, path, smenu):
        smenu.clear()
        items = self.menu.get_items(path, self.frame.vi_obj.menu)
        for name, item in items:
            new_item = None
            if isinstance(item.function, dict):
                new_item = smenu.addMenu(name)
                new_item.aboutToShow.connect(
                    lambda p=path + (name,), s=new_item:
                    self.show_path(p, s)
                )
            elif item.function is None:
                smenu.addSeparator()
            else:
                new_item = QAction(name, self.frame)
                new_item.triggered.connect(lambda x, f=item.function: f())
                if item.icon is not None:
                    new_item.setIcon(QIcon(item.icon))
                smenu.addAction(new_item)
            if item.description is not None and new_item is not None:
                new_item.setStatusTip(item.description)
            if item.shortcut is not None and new_item is not None:
                new_item.setShortcut(item.shortcut)
