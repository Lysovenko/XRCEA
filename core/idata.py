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
        self.contains = None
        self.density = None
        self.__sample = None
        self.__dict = {}
        self.x_data = None
        self.y_data = None
        self.wavel = None
        # diffraction angle of monochromer
        self.alpha = None
        self.x_axis = None
        self.lambda1 = None
        self.lambda2 = None
        self.lambda3 = None
        self.sm_pars = None
        self.I2 = .5
        self.I3 = .2
        if not XrayData.loaders:
            XrayData.loaders.append(XrayData.open_xrd)
        if fname is not None:
            self.open(fname)
            self.name = str(fname)

    def from_dict(self, dct):
        self.__dict.update(dct)
        if 'lambda1' in dct:
            try:
                self.lambda1 = float(dct['lambda1'])
            except ValueError:
                pass
        if 'lambda2' in dct:
            try:
                self.lambda2 = float(dct['lambda2'])
            except ValueError:
                pass
        if 'lambda3' in dct:
            try:
                self.lambda3 = float(dct['lambda3'])
            except ValueError:
                pass
        if 'lambda' in dct:
            try:
                self.wavel = float(dct['lambda'])
            except ValueError:
                pass
        if 'alpha' in dct:
            try:
                self.alpha = float(dct['alpha']) * np.pi / 180.
            except ValueError:
                pass
        if 'I2' in dct:
            try:
                self.I2 = float(dct['I2'])
            except ValueError:
                pass
        if 'I3' in dct:
            try:
                self.I3 = float(dct['I3'])
            except ValueError:
                pass
        if 'x_axis' in dct:
            if dct['x_axis'] in ['2\\theta', "\\theta", "q"]:
                self.x_axis = dct['x_axis']
            else:
                self.x_axis = None
        if 'elements' in dct:
            try:
                self.elements = eval(dct['elements'])
            except SyntaxError:
                self.elements = None
        if 'rho0' in dct:
            self.rho0 = float(dct['rho0'])
        if 'sample' in dct:
            self.__sample = dct['sample'].lower()
        if 'name' in dct:
            self.name = dct['name']
        if not self.wavel:
            self.wavel = self.lambda1
        if not self.lambda1:
            self.lambda1 = self.wavel

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


def open_xrd():
    """Open x-ray data file"""
    fn = APP.visual.ask_open_filename(
        _("Data"), "", [("*.xrd", _("Difractograms"))])
    if fn is not None:
        xrd = XrayData(fn)
        if xrd:
            plt = Plot(xrd.name, "exp_plot")
            plt.add_plot("exp_data", {
                "plots": ({"x1": xrd.x_data, "y1": xrd.y_data},),
                "x1label": xrd.x_axis, "y1label": _("pps")})
            plt.show()
            plt.draw("exp_data")
