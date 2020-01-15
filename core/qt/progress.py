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


from PyQt5.QtWidgets import (
    QVBoxLayout, QDialog, QDialogButtonBox, QLabel, QComboBox, QFileDialog,
    QFormLayout, QLineEdit, QCheckBox, QMessageBox, QProgressBar)


class Progress(QDialog):
    def __init__(self, title, status, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle(title)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttonBox.rejected.connect(self.reject)
        self._status = status
        self.progressBar = QProgressBar()
        self.progressBar.setRange(0, 1000)
        self.progressBar.setValue(0)
        timer = QTimer(self)
        timer.timeout.connect(self.advanceProgressBar)
        timer.start(1000)

    def _scheck_status(self):
        self.progressBar.setValue(self._status.get("part", 0.))

    def reject(self):
        # TODO: stop timer and process
        return super().reject()
