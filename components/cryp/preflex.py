# XRCEA (C) 2021 Serhii Lysovenko
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
"""
"""
from locale import atof, format_string
from math import asin, pi, sin
from core.application import APPLICATION as APP
from core.vi.value import Tabular, TabCell, Value
from core.vi.spreadsheet import Spreadsheet


class PeakLocator:
    def __init__(self, units, wavel):
        self.units = units
        self.wavel = wavel

    def to_units(self, val):
        if self.units == "sin":
            return self.wavel / (2. * val)
        if self.units == "d":
            return val
        if self.units == "d2":
            return val**2
        if self.units == "theta":
            return asin(self.wavel / (2. * val)) * 180. / pi
        if self.units == "2theta":
            return asin(self.wavel / (2. * val)) * 360. / pi

    def to_d(self, val):
        if self.units == "sin":
            return self.wavel / (2. * val)
        if self.units == "d":
            return val
        if self.units == "d2":
            return val**.5
        if self.units == "theta":
            return self.wavel / (2. * sin(val * pi / 180.))
        if self.units == "2theta":
            return self.wavel / (2. * sin(val * pi / 360.))


class PosCell(TabCell):
    """Cell with peak position"""
    def __init__(self, value, locator):
        self.__value = value
        self._locator = locator
        super().__init__()

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, val):
        if val is None:
            return
        try:
            arr = APP.runtime_data.get("User refl", [])
            try:
                i = arr.index(self.__value)
            except ValueError:
                i = None
            self.__value = self._locator.to_d(atof(str(val)))
            if i is not None:
                arr[i] = self.__value
        except ValueError:
            pass

    def __str__(self):
        try:
            return format_string("%.5g", self._locator.to_units(self.__value))
        except ValueError:
            return ""


class PredefRefl:
    def __init__(self, gdata):
        self.gdata = gdata
        self.spreadsheet = None

    def call_grid(self, idat):
        if self.spreadsheet:
            self.spreadsheet.show()
            return
        val = Tabular(colnames=["x\u2080", "?", "?", "?"])
        to_show = PeakLocator("sin", idat.lambda1)
        for i, pos in enumerate(APP.runtime_data.get("User refl", [])):
            val.insert_row(i, [PosCell(pos, to_show)] + [None] * 3)
        sps = Spreadsheet(str(idat.name) + _(" (found reflexes)"), val)
        self.spreadsheet = sps
        sps.show()

        def select_units(u):
            to_show.units = ["sin", "d", "d2", "theta", "2theta"][u]
            val.refresh()

        sps.set_form([(_("Units to display x\u2080:"), (
            "sin(\u03b8)", "d (\u212b)", "d\u207b\u00b2 (\u212b\u207b\u00b2)",
            "\u03b8 (\u00b0)", "2\u03b8 (\u00b0)"), select_units)])
