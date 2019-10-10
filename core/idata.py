#!/usr/bin/env python
"""Input data"""
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

import numpy as np
from json import loads
from .application import APPLICATION as APP, icon_file
from .vi import Plot


def introduce_input():
    """Add to menu "open" item"""
    APP.menu.append_item(
        (_("&File"),), _("&Open"), open_xrd, None, None,
        icon_file("open"))


class XrayData:
    loaders = []

    def __init__(self, fname=None):
        self.__sample = None
        self.__dict = {}
        for i in ("contains", "density", "x_data", "y_data",
                  # diffraction angle of monochromer
                  "alpha",
                  "x_units", "lambda1", "lambda2", "lambda3",
                  "I2", "I3"):
            setattr(self, i, None)
        if not XrayData.loaders:
            XrayData.loaders.append(XrayData.open_xrd)
        if fname is not None:
            self.open(fname)
            self.name = str(fname)

    def from_dict(self, dct):
        self.__dict.update(dct)
        for i in ("lambda1", "lambda2", "lambda3", "alpha", "I2", "I3",
                  "density"):
            try:
                setattr(self, i, float(dct[i]))
            except(ValueError, KeyError):
                pass
        if 'x_units' in dct:
            if dct['x_units'] in ['2theta', "theta", "q"]:
                self.x_units = dct['x_units']
            else:
                self.x_units = None
        if 'contains' in dct:
            try:
                self.contains = loads(dct['contains'])
            except:
                self.contains = None
        if 'sample' in dct:
            self.__sample = dct['sample'].lower()
        if 'name' in dct:
            self.name = dct['name']

    @staticmethod
    def open_xrd(fname):
        arr = []
        odict = {}
        fobj = open(fname)
        with fobj:
            for line in fobj:
                line = line.strip()
                if line.startswith('#'):
                    n, p, v = (i.strip() for i in line[1:].partition(':'))
                    if p:
                        odict[n] = v
                    continue
                try:
                    x, y = map(float, line.split()[:2])
                    arr.append((x, y))
                except ValueError:
                    pass
        if arr:
            arr.sort()
            arr = np.array(arr)
            x = arr.transpose()[0]
            y = arr.transpose()[1]
        else:
            x, y = None, None
        return x, y, odict

    def open(self, fname):
        for loader in XrayData.loaders:
            try:
                x, y, dct = loader(fname)
            except IOError:
                return
            if x is not None:
                self.x_data = x
                self.y_data = y
                return self.from_dict(dct)

    def __bool__(self):
        return self.x_data is not None and self.y_data is not None

    def make_plot(self):
        x_label = {"theta": "$\\theta$", "2theta": "$2\\theta$",
                   "q": "q", None: _("Unknown")}[self.x_units]
        return {"plots": [{"x1": self.x_data, "y1": self.y_data}],
                "x1label": x_label, "y1label": _("pps")}


def open_xrd():
    """Open x-ray data file"""
    fn = APP.visual.ask_open_filename(
        _("Data"), "", [("*.xrd", _("Difractograms"))])
    if fn is not None:
        xrd = XrayData(fn)
        if xrd:
            plt = Plot(xrd.name, "exp_plot")
            plt.add_plot("exp_data", xrd.make_plot())
            plt.show()
            plt.draw("exp_data")
