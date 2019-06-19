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
#
# If matplotlib contributes to a project that leads to a scientific
# publication, please acknowledge this fact by citing the project.
# You can use this BibTeX entry:
# @Article{Hunter:2007,
#   Author    = {Hunter, J. D.},
#   Title     = {Matplotlib: A 2D graphics environment},
#   Journal   = {Computing In Science \& Engineering},
#   Volume    = {9},
#   Number    = {3},
#   Pages     = {90--95},
#   abstract  = {Matplotlib is a 2D graphics package used for Python
#   for application development, interactive scripting, and
#   publication-quality image generation across user
#   interfaces and operating systems.},
#   publisher = {IEEE COMPUTER SOC},
#   year      = 2007
# }

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt,
                          QTextStream)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog, QMainWindow,
                             QMessageBox, QSizePolicy)
import matplotlib
matplotlib.use('Qt5Agg')


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg \
    as FigureCanvas
from matplotlib.figure import Figure
# from .core import _DATA, Face, clearLayout


class Canvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        # self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class PlotWindow(QMainWindow):
    def __init__(self, vi_obj):
        super(PlotWindow, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(vi_obj.title)
        self.canvas = Canvas(self)
        self.setCentralWidget(self.canvas)
        # self.createActions()
        # self.createMenus()
        # self.createToolBars()
        # self.createStatusBar()

        # self.readSettings()

        # self.textEdit.document().contentsChanged.connect(self.documentWasModified)
        self.vi_obj = vi_obj

    def closeEvent(self, event):
        # if self.maybeSave():
        #     self.writeSettings()
        #     event.accept()
        # else:
        #     event.ignore()
        pass


def show_plot_window(vi_obj):
    if vi_obj.gui_functions:
        vi_obj.gui_functions["%Window%"].raise_()
        return
    # if vi_obj.class_name is not None:
    #     sw.after_close.append(lambda x:  _DATA["Settings"].setValue(
    #         vi_obj.class_name+'_geometry', x.saveGeometry()))
    plt = PlotWindow(vi_obj)
    vi_obj.gui_functions["%Window%"] = plt
    plt.show()


if __name__ == '__main__':
    class vi_obj:
        def __init__(self):
            self.title = 'hello world'
            self.gui_functions = {}
    import sys
    app = QApplication(sys.argv)
    v = vi_obj()
    show_plot_window(v)
    sys.exit(app.exec_())
