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

from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel
from PyQt5.QtWidgets import QTableView, QTreeView, QAbstractItemView, QMenu
from PyQt5.QtGui import (QStandardItem, QStandardItemModel, QColor)

COLORS = {"red": Qt.red, "blue": Qt.blue, "gray": Qt.gray,
          "light gray": Qt.lightGray,
          "white": Qt.white, "dark blue": Qt.darkBlue, "green": Qt.green}


class VisualTableModel(QAbstractTableModel):
    def __init__(self, colnames, value, styles, parent):
        super().__init__(parent)
        self.colnames = colnames
        for i, name in enumerate(colnames):
            self.setHeaderData(i, Qt.Horizontal, name)
        self.value = value
        value.set_updater(self.updater)
        self.styles = styles

    def updater(self, lst):
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.colnames[section]
        return None

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.value.get()[index.row()][index.column()]
        if role == Qt.BackgroundRole or role == Qt.ForegroundRole:
            tup = self.value.get()[index.row()]
            try:
                style = tup[self.columnCount()]
            except IndexError:
                return None
            if isinstance(style, (tuple, list)):
                style = style[index.column()]
            if not isinstance(style, set):
                style = {style}
            for s in style:
                fg, bg = self.styles.get(s, (None, None))
                if fg is not None and role == Qt.ForegroundRole:
                    return QColor(fg)
                if bg is not None and role == Qt.BackgroundRole:
                    return QColor(bg)
        return None

    def setData(self, index, data, role):
        print(index.row(), index.column(), role, data)
        return True

    def rowCount(self, *dummy):
        return len(self.value.value)

    def columnCount(self, parent=None):
        return len(self.colnames)

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable

    def index(self, row, column, parent=None):
        if not self.hasIndex(row, column, parent) or parent.isValid():
            return QModelIndex()
        return self.createIndex(row, column, None)


class VisualTable(QTableView):
    def __init__(self, parent, colnames, value, styles={}):
        super().__init__(parent)
        self.value = value
        self.styles = styles
        self.setAlternatingRowColors(True)
        self.ncols = len(colnames)
        self.model = model = VisualTableModel(colnames, value, styles, self)
        self.setModel(model)
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
