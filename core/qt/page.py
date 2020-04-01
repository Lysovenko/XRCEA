#!/usr/bin/env python3
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
"""Draw an Page (list and text area)"""


from PyQt5.QtWidgets import (QFormLayout, QWidget, QVBoxLayout, QTextBrowser,
                             QSplitter, QPushButton, QShortcut)
from PyQt5.QtCore import Qt, QTextCodec
from PyQt5.QtGui import (QKeySequence, QIcon)
from .lists import VisualList
from .core import clearLayout, qMainWindow
from .idialog import DialogsMixin, get_widget_value, get_widget_from_value


class Page(qMainWindow):
    def __init__(self, vi_obj):
        super().__init__(vi_obj)
        self.splitter = QSplitter(self)
        self.setCentralWidget(self.splitter)
        self.styles = {}
        self.values = None
        self.choicer = None
        self.separate_items = False
        self.close_lock = None
        self.form_edas = []

    def draw_shape(self, colnames, lvalue, styles):
        message_area = QWidget()
        layout = QVBoxLayout(message_area)
        self.form = QFormLayout()
        layout.addLayout(self.form)
        self.textEdit = QTextBrowser(self)
        self.textEdit.setOpenExternalLinks(True)
        sk = QShortcut(QKeySequence("Ctrl+="), self.textEdit)
        sk.activated.connect(self.textEdit.zoomIn)
        sk = QShortcut(QKeySequence("Ctrl+-"), self.textEdit)
        sk.activated.connect(self.textEdit.zoomOut)
        layout.addWidget(self.textEdit)
        self.splitter.addWidget(message_area)
        if colnames is not None:
            self.vislist = vl = VisualList(self, colnames, lvalue, styles)
            self.splitter.addWidget(vl)
        else:
            self.vislist = None
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

    def set_choicer(self, choicer, separate_items=False):
        if self.vislist is not None:
            self.vislist.set_choicer(choicer, separate_items)

    def set_context_menu(self, cmenu):
        if self.vislist is not None:
            self.vislist.set_context_menu(cmenu)

    def set_close_lock(self, close_lock):
        self.close_lock = close_lock

    def set_icon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def load(self, data, editable=False):
        if isinstance(data, str):
            unistr = data
        else:
            codec = QTextCodec.codecForHtml(data)
            unistr = codec.toUnicode(data)
        if Qt.mightBeRichText(unistr):
            self.textEdit.setHtml(unistr)
        else:
            self.textEdit.setPlainText(unistr)
        self.textEdit.setReadOnly(not editable)

    def getHTML(self):
        return self.textEdit.document().toHtml()

    def getText(self):
        return self.textEdit.document().toPlainText()

    def scroll_down(self):
        scroll = self.textEdit.verticalScrollBar()
        scroll.setValue(scroll.maximum())

    def update_form(self, form, is_editable):
        layout = self.form
        self.form_edas.clear()
        clearLayout(layout)
        for n, f in form:
            ew = get_widget_from_value(f)
            try:
                ew.setReadOnly(not is_editable)
            except AttributeError:
                pass
            if callable(n):
                call = n
                n = QPushButton(n.name)
                n.clicked.connect(
                    lambda x, y=ew, c=call: c(get_widget_value(y)))
                if hasattr(ew, "returnPressed"):
                    ew.returnPressed.connect(
                        lambda y=ew, c=call: c(get_widget_value(y)))
            if ew is None:
                layout.addRow(n)
            else:
                layout.addRow(n, ew)
                self.form_edas.append(ew)

    def get_form_vals(self):
        return tuple(get_widget_value(e) for e in self.form_edas)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.parent.close()

    def closeEvent(self, event=None):
        if event is not None:
            if super().closeEvent(event):
                return
        self.vi_obj.currently_alive = False


def show_page(vi_obj):
    if vi_obj.gui_functions:
        vi_obj.gui_functions["%Window%"].raise_()
        return
    page = Page(vi_obj)
    vi_obj.gui_functions["%Window%"] = page
    page.draw_shape(vi_obj.colnames, vi_obj.lvalue, vi_obj.styles)
    if vi_obj.choicer is not None:
        page.set_choicer(vi_obj.choicer)
    if vi_obj.list_context_menu is not None:
        page.set_context_menu(vi_obj.list_context_menu)
    if vi_obj.icon is not None:
        page.set_icon(vi_obj.icon)
    vi_obj.gui_functions["set_choicer"] = page.set_choicer
    vi_obj.gui_functions["set_list_context_menu"] = page.set_context_menu
    vi_obj.gui_functions["set_text"] = page.load
    vi_obj.gui_functions["set_form"] = page.update_form
    vi_obj.gui_functions["get_form_values"] = page.get_form_vals
    vi_obj.gui_functions["get_text"] = page.getText
    vi_obj.gui_functions["get_html"] = page.getHTML
    vi_obj.gui_functions["scroll_down"] = page.scroll_down
    if page.vislist is not None:
        vi_obj.gui_functions["set_selected"] = page.vislist.set_selected
    page.register_dialogs()
    for k, f in vi_obj.shortcuts.items():
        page.add_shortcut(k, f)
    page.show()
    vi_obj.currently_alive = True
