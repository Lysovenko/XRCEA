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

from PyQt5.QtWidgets import QLineEdit


class LineEdit(QLineEdit):
    def __init__(self, parent, value):
        super().__init__(parent)
        self.setText(str(value))
        value.set_relevator(self.its_relevant)
        value.set_updater(self.updater)
        self.value = value
        self.its_relevant(value.is_relevant())
        self.textChanged.connect(self.text_changed)

    def updater(self, val):
        self.setText(str(val))
        self.value.had_error = False

    def its_relevant(self, relevant):
        self.setReadOnly(not relevant)
        if relevant:
            self.setStyleSheet("QLineEdit ")
        else:
            self.setText(str(self.value))
            self.value.had_error = False
            self.setStyleSheet("QLineEdit { background: rgb(127, 127, 127); }")

    def text_changed(self, txt):
        val = self.value
        try:
            val.update(txt, False)
        except ValueError as err:
            val.had_error = True
            self.setStyleSheet("QLineEdit { background: rgb(255, 55, 55); }")
        else:
            val.had_error = False
            self.setStyleSheet("QLineEdit ")
