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
"""Spreadsheet with some peaks positions"""

from locale import atof, format_string
from math import asin, pi
from core.vi.spreadsheet import Spreadsheet
from core.application import APPLICATION as APP
from core.vi.value import Tabular, TabCell, Value
from core.vi import Button
from .integers import find_integers
_treat = _("Treat")


class IFloat(TabCell):
    """Immutable cell with floating poin value"""
    def __init__(self, *args, **kvargs):
        self.__value = None
        super().__init__(*args, **kvargs)

    @property
    def value(self):
        try:
            return format_string("%.5g", self.__value)
        except TypeError:
            return ""

    @value.setter
    def value(self, val):
        if isinstance(val, float):
            self.__value = val


class X0Cell(TabCell):
    """Immutable cell with floating poin value"""
    def __init__(self, value, display):
        self.__value = value
        self._display = display
        super().__init__()

    @property
    def value(self):
        return format_string("%.5g", self._display(self.__value))

    @value.setter
    def value(self, val):
        pass


class DisplayX0:
    def __init__(self, units, idat):
        self.units = units
        self._idata = idat

    def __call__(self, val):
        if self.units == "sin":
            return val
        if self.units == "d":
            return self._idata.lambda1 / 2. / val
        if self.units == "d2":
            return (2. * val / self._idata.lambda1) ** 2
        if self.units == "theta":
            return asin(val) * 180. / pi
        if self.units == "2theta":
            return asin(val) * 360. / pi


def show_sheet(idat):
    cryb = idat.extra_data.get("crypbells")
    if cryb is None:
        return
    val = Tabular(colnames=["x\u2080", "h", "w", "s", "h k l"])
    display = DisplayX0("sin", idat)
    for i, data in enumerate(cryb.reshape(len(cryb) // 4, 4)):
        val.insert_row(i, [X0Cell(data[0], display)] + [
            IFloat(i) for i in data[1:]] + [None])
    p = Spreadsheet(str(idat.name) + _(" (found reflexes)"), val)

    def _find_ints():
        grps = find_integers(cryb)
        if grps:
            val.insert_column(val.columns, "ints", int)
            grp = grps[0][0]
            j = val.columns - 1
            for i, k in grp.items():
                val.set(i, j, k)

    p.menu.append_item((_treat,), _("Find integers"), _find_ints, None)
    p.show()

    def select_units(u):
        display.units = ["sin", "d", "d2", "theta", "2theta"][u]
        val.refresh()

    p.set_form([(_("Units to display x\u2080:"), (
        "sin(\u03b8)", "d (\u212b)", "d\u207b\u00b2 (\u212b\u207b\u00b2)",
        "\u03b8 (\u00b0)", "2\u03b8 (\u00b0)"), select_units)])
