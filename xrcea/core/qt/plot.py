# XRCEA (C) 2019-2022 Serhii Lysovenko
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
"""Display plots"""

from PyQt5.QtCore import (QFile, QFileInfo, QPoint, QSettings, QSize, Qt,
                          QTextStream)
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QApplication, QFileDialog,
                             QMessageBox, QSizePolicy)
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from .idialog import DialogsMixin
from .core import qMainWindow
from ..application import APPLICATION as APP


class Canvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = fig = Figure(figsize=(width, height), dpi=dpi)
        self.mk_axes()
        super().__init__(fig)
        self.setParent(parent)

        super().setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        super().updateGeometry()

    def mk_axes(self):
        self.axes1 = self.figure.add_subplot(111)
        self.axes1.grid(True)
        self.axes2 = None
        self.axes1.set_xlabel(r'$s,\, \AA^{-1}$')
        self.axes1.set_ylabel('Intensity')

    def get_limits(self):
        res = {}
        for axno, ax in enumerate(("axes1", "axes2")):
            try:
                ax = getattr(self, ax)
                res[axno] = {"xlim": ax.get_xlim(), "ylim": ax.get_ylim()}
            except AttributeError:
                pass
        return res

    def draw(self, dset=None):
        if dset is None:
            return super().draw()
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
            cc = APP.settings.get_color(color)
            extras = {}
            ls = plot.get("linestyle")
            if ls in ("solid", "dashed", "dashdot", "dotted"):
                extras["linestyle"] = ls
            try:
                extras["label"] = plot["legend"]
            except KeyError:
                pass
            if cc is not None:
                color = cc
            if "y2" in plot:
                a2p = self.axes2
            else:
                a2p = self.axes1
            if ltype == "pulse":
                a2p.vlines(plot["x1"], 0, plot.get("y1", plot.get("y2")),
                           color=color, **extras)
            else:
                a2p.plot(plot["x1"], plot.get("y1", plot.get("y2")), ltype,
                         color=color, **extras)
            if "legend" in plot:
                a2p.legend()
            for lim in ("xlim", "ylim"):
                try:
                    getattr(a2p, "set_" + lim)(plot[lim])
                except KeyError:
                    pass
        super().draw()


class PlotWindow(qMainWindow):
    """Plot and toolbar"""
    def __init__(self, vi_obj):
        super(PlotWindow, self).__init__(vi_obj)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.canvas = Canvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.addToolBar(self.toolbar)
        self.setCentralWidget(self.canvas)

    def closeEvent(self, event):
        self.vi_obj.currently_alive = False
        self.vi_obj.gui_functions.clear()

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
    vi_obj.gui_functions["get_limits"] = plt.canvas.get_limits
    plt.register_dialogs()
    for k, f in vi_obj.shortcuts.items():
        plt.add_shortcut(k, f)
    plt.show()
    vi_obj.currently_alive = True
