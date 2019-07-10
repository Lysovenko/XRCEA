#!/usr/bin/env python3
"""Display plots"""
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
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from .menu import SDIMenu
# from .core import _DATA, Face, clearLayout


class Canvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = fig = Figure(figsize=(width, height), dpi=dpi)
        self.mk_axes()

        # self.compute_initial_figure()

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def mk_axes(self):
        self.axes1 = self.figure.add_subplot(111)
        self.axes1.grid(True)
        self.axes2 = None
        self.axes1.set_xlabel(r'$s,\, \AA^{-1}$')
        self.axes1.set_ylabel('Intensity')

    def draw(self, dset):
        self.figure.clear()
        self.axes1 = self.figure.add_subplot(111)
        self.axes1.grid(True)
        if any("y2" in p for p in dset.get("plots", ())):
            self.axes2 = self.axes1.twinx()
        else:
            self.axes2 = None
        if "x1label" in dset:
            self.axes1.set_xlabel(
                dset["x1label"], fontdict={"family": "serif"})
        if "y1label" in dset:
            self.axes1.set_ylabel(
                dset["y1label"], fontdict={"family": "serif"})
        for plot in dset["plots"]:
            ltype = plot.get("type", "-")
            color = plot.get("color")
            if "y2" in plot:
                a2p = self.axes2
            else:
                a2p = self.axes1
            if ltype == "pulse":
                a2p.bar(plot["x1"], plot.get("y1", plot.get("y2")),
                        edgecolor=color, align="center")
            else:
                a2p.plot(plot["x1"], plot.get("y1", plot.get("y2")), ltype,
                         color=color, picker=plot.get("picker"))


class PlotWindow(QMainWindow):
    """Plot and toolbar"""
    def __init__(self, vi_obj):
        super(PlotWindow, self).__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle(vi_obj.title)
        self.canvas = Canvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.addToolBar(self.toolbar)
        self.setCentralWidget(self.canvas)
        self.vi_obj = vi_obj
        self.menu = SDIMenu(self)
        self.vi_obj = vi_obj

    def closeEvent(self, event):
        pass

    def set_icon(self, icon):
        self.setWindowIcon(QIcon(icon))

    def draw(self, plt):
        self.canvas.draw(plt)


def show_plot_window(vi_obj):
    if vi_obj.gui_functions:
        vi_obj.gui_functions["%Window%"].raise_()
        return
    plt = PlotWindow(vi_obj)
    vi_obj.gui_functions["%Window%"] = plt
    if vi_obj.icon is not None:
        plt.set_icon(vi_obj.icon)
    vi_obj.gui_functions["set_icon"] = plt.set_icon
    vi_obj.gui_functions["draw"] = plt.draw
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
