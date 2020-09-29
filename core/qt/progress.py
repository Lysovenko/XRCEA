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
"""Draw progress dialog"""


from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QVBoxLayout, QDialog, QDialogButtonBox, QLabel, QComboBox, QFileDialog,
    QFormLayout, QLineEdit, QCheckBox, QMessageBox, QProgressBar)


class Progress(QDialog):
    def __init__(self, title, status,
                 parent=None  # type: Any
                 ):
        super().__init__(parent)
        self.setWindowTitle(title)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttonBox.rejected.connect(self.reject)
        self._status = status
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 1000)
        self.progressBar.setValue(0)
        self.description = QLabel()
        self.description.setText("")
        layout = QVBoxLayout()
        layout.addWidget(self.description)
        layout.addWidget(self.progressBar)
        layout.addWidget(buttonBox)
        self.setLayout(layout)
        self.prev_st = ""
        self.prev_pr = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_status)
        self.timer.start(100)
        self._starter = status["start"]

    def _check_status(self):
        if self._starter is not None:
            self._starter()
            self._starter = None
        cur_pr = int(self._status.get("part", 0.) * 1000)
        if self.prev_pr != cur_pr:
            self.progressBar.setValue(cur_pr)
            self.prev_pr = cur_pr
        cur_st = self._status.get("description", "")
        if self.prev_st != cur_st:
            self.description.setText(cur_st)
            self.prev_st = cur_st
        if self._status.get("complete"):
            self.reject()

    def reject(self):
        try:
            self.timer.stop()
        except RuntimeError:
            pass
        else:
            self.timer.deleteLater()
        self._status["stop"] = True
        return super().reject()
