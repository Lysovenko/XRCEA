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
    def __init__(self, value, parent):
        super().__init__(parent)
        self.value = value
        value.set_updater(self.updater)

    def updater(self):
        self.layoutChanged.emit()

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.value.colname(section)
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section + 1
        return None

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            v = self.value.get(index.row(), index.column())
            if v is None:
                return None
            return str(v)
        if role == Qt.EditRole:
            v = self.value.get(index.row(), index.column())
            if v is None:
                return None
            try:
                return v.edit
            except AttributeError:
                return str(v)
        if role == Qt.BackgroundRole or role == Qt.ForegroundRole:
            tc = self.value.get(index.row(), index.column())
            try:
                if role == Qt.ForegroundRole and tc.foreground is not None:
                    return QColor(tc.foreground)
                if role == Qt.BackgroundRole and tc.background is not None:
                    return QColor(tc.background)
            except AttributeError:
                return None
        return None

    def setData(self, index, data, role=Qt.DisplayRole):
        if role == Qt.EditRole:
            self.value.set(index.row(), index.column(), data)
            return True
        print(role, index.row(), index.column(), data)

    def rowCount(self, *dummy):
        return self.value.rows

    def columnCount(self, parent=None):
        return self.value.columns

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        tc = self.value.get(index.row(), index.column())
        editable = Qt.ItemIsEditable if getattr(tc, "editable", True) else 0
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | editable

    def index(self, row, column, parent=None):
        if not self.hasIndex(row, column, parent) or parent.isValid():
            return QModelIndex()
        return self.createIndex(row, column, None)


class VisualTable(QTableView):
    def __init__(self, parent, value, styles=None):
        super().__init__(parent)
        self.value = value
        self.styles = styles
        self.setAlternatingRowColors(True)
        self.model = model = VisualTableModel(value, self)
        self.setModel(model)
        self.activated.connect(self.on_activated)
        self.choicer = None
        self.context_menu = None
        self.separate_items = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            try:
                self._del_pressed([(i.row(), i.column())
                                   for i in self.selectedIndexes()])
            except AttributeError:
                pass
            else:
                self.model.updater()
        super().keyPressEvent(event)

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
            try:
                fg, bg = self.styles.get(style, (None, None))
            except AttributeError:
                fg = bg = None
            if fg is not None:
                cell.setForeground(QColor(fg))
            if bg is not None:
                cell.setBackground(QColor(bg))

    def set_choicer(self, choicer, separate_items=False):
        if separate_items:
            self.setSelectionBehavior(QAbstractItemView.SelectItems)
        else:
            self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.choicer = choicer
        self.separate_items = separate_items

    def set_del_pressed(self, callback):
        self._del_pressed = callback

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
                    val = self.value.get(model_index.row(),
                                         model_index.column())
                except IndexError:
                    val = None
                function(val, model_index.row(), model_index.column())
                break

    def set_selected(self, index):
        self.setCurrentIndex(self.model.index(index, 0))
