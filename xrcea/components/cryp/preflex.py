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
from xrcea.core.application import APPLICATION as APP
from xrcea.core.vi.value import Tabular, TabCell, Value, lfloat
from xrcea.core.vi.spreadsheet import Spreadsheet
_edit = _("Edit")


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
            return val**-2
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
            return val**-.5
        if self.units == "theta":
            return self.wavel / (2. * sin(val * pi / 180.))
        if self.units == "2theta":
            return self.wavel / (2. * sin(val * pi / 360.))


class PosCell(TabCell):
    """Cell with peak position"""
    def __init__(self, cont, locator):
        self._locator = locator
        self.__cont = cont
        super().__init__()

    @property
    def value(self):
        return self.__cont[0]

    @value.setter
    def value(self, val):
        if val is None:
            return
        try:
            self.__cont[0] = self._locator.to_d(atof(str(val)))
        except (ValueError, ZeroDivisionError):
            pass

    def __str__(self):
        try:
            return format_string(
                "%.5g", self._locator.to_units(self.__cont[0]))
        except (ValueError, ZeroDivisionError):
            return ""

    def shift_in_units(self, shift):
        try:
            self.__cont[0] = self._locator.to_d(
                self._locator.to_units(self.__cont[0]) + shift)
        except (ValueError, ZeroDivisionError):
            pass


class Table(Tabular):
    def __init__(self, origin, colnames):
        self._origin = origin
        super().__init__(colnames=colnames)

    def set(self, r, c, v):
        if c == 1:
            self._origin[r][1] = str(v)
        super().set(r, c, v)

    def on_del_pressed(self, cells):
        origin = self._origin
        rows = sorted(set(i[0] for i in cells), reverse=True)
        try:
            for i in rows:
                origin.pop(i)
        except IndexError:
            pass
        else:
            self.remove_rows(rows)

    def from_origin(self, locator):
        self.remove_rows()
        for i, row in enumerate(self._origin):
            self.insert_row(i, [PosCell(row, locator), row[1]])


class AssumedRefl(Spreadsheet):
    def __init__(self, idat):
        self._xrd = idat
        self._tab = tab = Table(
            idat.extra_data.setdefault("AssumedReflexes", []),
            ["x\u2080", _("Comment")])
        self._ploc = to_show = PeakLocator("sin", idat.lambda1)
        super().__init__(str(idat.name) + _(" (assumed reflexes)"), tab)
        self.reread()
        self.menu.append_item((_edit,), _("Shift by..."),
                              self.shift_by, None)
        self.show()

        def select_units(u):
            to_show.units = ["sin", "d", "d2", "theta", "2theta"][u]
            tab.refresh()

        self.set_form([(_("Units to display %s:") % "x\u2080", (
            "sin(\u03b8)", "d (\u212b)", "d\u207b\u00b2 (\u212b\u207b\u00b2)",
            "\u03b8 (\u00b0)", "2\u03b8 (\u00b0)"), select_units)])

    def reread(self):
        self._tab.from_origin(self._ploc)

    def shift_by(self):
        sels = [c[0] for c in self.get_selected_cells() if c[1] == 0]
        if not sels:
            self.print_error(_("No cells selected."))
            return
        shift = Value(lfloat())
        dlgr = self.input_dialog(_("Shift selected cells"),
                                 [(_("Shift by:"), shift)])
        if dlgr is None:
            return
        for i in sels:
            self._tab.get(i, 0).shift_in_units(shift.get())


def show_assumed(idat):
    predef = idat.UIs.get("AssumedReflexes")
    if predef:
        predef.show()
        return
    idat.UIs["AssumedReflexes"] = AssumedRefl(idat)
