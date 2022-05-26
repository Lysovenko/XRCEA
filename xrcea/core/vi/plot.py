#!/usr/bin/env python3
"""Wrap a GUI plot"""
# XRCEA (C) 2019-2020 Serhii Lysovenko
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

from copy import deepcopy
from os.path import splitext
from .menu import DMenu
from .mixins import DialogsMixin


class Plot(DialogsMixin):
    def __init__(self, name,
                 class_name=None, identifier=None):
        self.__name = name
        self.identifier = identifier
        self.close_lock = None
        self.currently_alive = False
        self.gui_functions = {}
        self.icon = None
        self.class_name = class_name
        self.shortcuts = {}
        self.menu = DMenu()
        self.plots = {}
        self._currently_showing = None
        self.menu.append_item((_("Plot"),), _("Export DAT"), self.export_dat)
        self.menu.append_item((_("Plot"),), _("Show comment"),
                              self.show_comment)
        self.menu.append_item((_("Plot"),), None, None)

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name_):
        if "set_name" in self.gui_functions:
            self.gui_functions["set_name"](name_)
        self.__name = name_

    def show(self):
        from ..application import get_actual_interface
        get_actual_interface().show_vi(self)

    def draw(self, pl_name):
        """Try to draw a plot"""
        try:
            self.gui_functions["draw"](self.plots[pl_name])
            self._currently_showing = pl_name
        except (KeyError, ValueError):
            pass

    def add_plot(self, pl_name, plt):
        """ adds plot with name, where plt is:
        {"plots": [{
        "type": "-", # ("pulse" or MathPlotLib types)
        "color": None,
        "x1": Array(),
        "y1": Array(),
        "y2": Array(), # (optionally replaces y1)
        "legend": "plot's label",
        "xlim": (left, right),
        "ylim": (bottom, top)
        }],
        "x1label": "X axis title",
        "y1label": "Y axis title",
        "x1units": "2theta", # used for adding extra plots
        }"""
        if pl_name not in self.plots:
            self.menu.append_item((_("Plot"),), pl_name,
                                  lambda x=pl_name, f=self.draw: f(x))
        self.plots[pl_name] = plt

    def get_plot(self, pl_name):
        return deepcopy(self.plots.get(pl_name))

    def get_current(self):
        return self._currently_showing, self.get_plot(self._currently_showing)

    def get_limits(self):
        """Returns:
           --------

        Plot's limits setted by user.
        {int: {"xlim": (float, float), "ylim": (float, float)}}
        """
        try:
            return self.gui_functions["get_limits"]()
        except KeyError:
            return {}

    def set_close_lock(self, close_lock):
        self.close_lock = close_lock
        if "set_close_lock" in self.gui_functions:
            self.gui_functions["close_lock"](close_lock)

    def set_icon(self, icon):
        self.icon = icon
        if "set_icon" in self.gui_functions:
            self.gui_functions["set_icon"](icon)

    def add_shortcut(self, key, func):
        self.shortcuts[key] = func
        try:
            self.gui_functions["add_shortcut"](key, func)
        except KeyError:
            pass

    def _export_as_ssv(self, pl_name, fpout):
        plot = self.plots.get(pl_name)
        if plot is None:
            return
        plts = plot.get("plots")
        if plts is None:
            return
        for k in ("x1label", "y1label", "x1units"):
            v = plot.get(k)
            if v:
                print(f"#{k}\t{v}", file=fpout)
        print("########## PLOTS ##########", file=fpout)
        for plt in plts:
            for k in ("type", "color"):
                v = plt.get(k)
                if v:
                    print(f"#{k}\t{v}", file=fpout)
            xarr = plt.get("x1")
            yarr = plt.get("y1")
            if yarr is None:
                yarr = plt.get("y2")
                print("#Second Y", file=fpout)
            for x, y in zip(xarr, yarr):
                print(x, y, sep='\t', file=fpout)
            print('\n', file=fpout)

    def export_dat(self):
        if not self._currently_showing:
            return
        fname = self.ask_save_filename(
            self._currently_showing + ".dat", [("*.dat", _("DAT files"))])
        if fname:
            if splitext(fname)[1] != ".dat":
                fname += ".dat"
            try:
                with open(fname, "w") as fp:
                    self._export_as_ssv(self._currently_showing, fp)
            except OSError:
                self.print_error(_("Unable to write %s") % fname)
                return

    def show_comment(self):
        if not self._currently_showing:
            return
        comment = self.plots.get(self._currently_showing, {}).get("Comment")
        if comment is None:
            return
        self.print_information(comment)

    def __bool__(self):
        return self.currently_alive

    def __eq__(self, val):
        return self.identifier == val
