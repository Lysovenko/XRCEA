#!/usr/bin/env python
"""Text editors dealing with value"""
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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QListWidget, QTreeView, QAbstractItemView, QMenu
from PyQt5.QtGui import (QStandardItem, QStandardItemModel, QColor)

COLORS = {"red": Qt.red, "blue": Qt.blue, "gray": Qt.gray,
          "light gray": Qt.lightGray,
          "white": Qt.white, "dark blue": Qt.darkBlue, "green": Qt.green}


class CheckedList(QListWidget):
    def __init__(self, parent, value):
        super().__init__(parent)
        self.value = value
        self.addItems(i[1] for i in value)
        for i, (uid, name, sel) in enumerate(value):
            item = self.item(i)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            check = Qt.Checked if sel else Qt.Unchecked
            item.setCheckState(check)
            item.setWhatsThis(str(i))
        self.itemChanged.connect(self.clk)
        self.show()

    def selectionChanged(self, *args):
        print("selection changed:", args)

    def clk(self, item):
        try:
            i = int(item.whatsThis())
        except TypeError:
            return
        uid, name, sel = self.value.pop(i)
        sel = item.checkState() == Qt.Checked
        self.value.insert(i, (uid, name, sel))
        if sel:
            item.setBackground(QColor("#ffffb2"))
        else:
            item.setBackground(QColor("#ffffff"))


class VisualList(QTreeView):
    def __init__(self, parent, colnames, value, styles={}):
        super().__init__(parent)
        self.value = value
        self.styles = styles
        self.setRootIsDecorated(False)
        self.setAlternatingRowColors(True)
        self.ncols = len(colnames)
        model = QStandardItemModel(0, self.ncols, parent)
        self.model = model
        for i, name in enumerate(colnames):
            model.setHeaderData(i, Qt.Horizontal, name)
        self.setModel(model)
        self.update_rows(value.get())
        value.set_updater(self.update_rows)
        self.activated.connect(self.on_activated)
        self.choicer = None
        self.context_menu = None
        self.separate_items = False

    def on_activated(self, model_index):
        if self.choicer is not None and model_index.isValid() \
           and self.value is not None:
            if self.separate_items:
                self.choicer(self.value.get()[model_index.row()],
                             model_index.column())
            else:
                self.choicer(self.value.get()[model_index.row()])

    def add_item(model, itup):
        model.insertRow(0)
        for i, value in enumerate(itup):
            model.setData(model.index(0, i), value)

    def update_rows(self, self_value):
        model = self.model
        ncols = self.ncols
        model.removeRows(0, model.rowCount())
        for itup in reversed(self_value):
            model.insertRow(0)
            try:
                style = itup[ncols]
            except IndexError:
                style = None
            for i, value in enumerate(itup[:ncols]):
                itm = QStandardItem(str(value))
                itm.setFlags(itm.flags() & ~Qt.ItemIsEditable)
                if isinstance(style, str):
                    self.set_style(style, itm)
                elif isinstance(style, (tuple, list)):
                    self.set_style(style[i], itm)
                model.setItem(0, i, itm)
        for i in range(ncols):
            self.resizeColumnToContents(i)

    def set_style(self, style, cell):
        if isinstance(style, set):
            styles = style
        else:
            styles = {style}
        for style in styles:
            fg, bg = self.styles.get(style, (None, None))
            try:
                if fg is not None:
                    cell.setForeground(QColor(fg))
                if bg is not None:
                    cell.setBackground(QColor(bg))
            except Exception:
                print('bad colors:', fg, bg)

    def set_choicer(self, choicer, separate_items=False):
        if separate_items:
            self.setSelectionBehavior(QAbstractItemView.SelectItems)
        else:
            self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.choicer = choicer
        self.separate_items = separate_items

    def set_context_menu(self, menu):
        self.context_menu = menu

    def contextMenuEvent(self, event):
        try:
            model_index = self.selectedIndexes()[0]
        except IndexError:
            return
        if self.context_menu is None or not model_index.isValid() \
           or self.value is None:
            return
        cmenu = QMenu(self)
        actlist = []
        # TODO: add ability to make context menu with subitems
        for name, function in self.context_menu:
            actlist.append((cmenu.addAction(name), function))
        do_action = cmenu.exec_(self.mapToGlobal(event.pos()))
        for action, function in actlist:
            if do_action == action:
                try:
                    tup = self.value.get()[model_index.row()]
                except IndexError:
                    tup = ()
                function(tup, model_index.column())
                break

    def set_selected(self, index):
        self.setCurrentIndex(self.model.index(index, 0))
