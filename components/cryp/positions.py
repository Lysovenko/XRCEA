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
from core.vi import Button, print_information, print_error
from .integers import find_integers, correct_angle
_treat = _("Treat")
CELL_TYPE_C, CELL_TYPE_N = zip(*(
    ("hex", _("Hexagonal")),
))


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


class HklCell(TabCell):
    """Cell with Miller indices"""
    def __init__(self, indices):
        self.__value = None
        self._indices = indices
        super().__init__()

    @property
    def value(self):
        return self._indices.get(self.row)

    @value.setter
    def value(self, val):
        try:
            ls = list(map(int, val.split()[:3]))
        except (ValueError, AttributeError):
            return
        ls += [0] * (3 - len(ls))
        self._indices[self.row] = self.__value = ls

    def __str__(self):
        v = self.value
        if v is None:
            return ""
        return "%d %d %d" % tuple(v)


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


class FoundBells(Spreadsheet):
    def __init__(self, xrd):
        self._xrd = xrd
        self._uindex = xrd.extra_data.setdefault("UserIndexes", {})
        cryb = xrd.extra_data.get("crypbells")
        self.cryb = cryb = sorted(map(tuple, cryb.reshape(len(cryb) // 4, 4)))
        val = Tabular(colnames=["x\u2080", "h", "w", "s"])
        self.display = display = DisplayX0("sin", xrd)
        for i, data in enumerate(cryb):
            val.insert_row(i, [X0Cell(data[0], display)] + [
                IFloat(i) for i in data[1:]])
        super().__init__(str(xrd.name) + _(" (found reflexes)"), val)
        self.load_miller_indices()
        self.int_groups = []
        self.menu.append_item((_treat,), _("Find integers"),
                              self._find_ints, None)
        self.menu.append_item((_treat,), _("Correct angle"),
                              self._theta_correction, None)
        self.menu.append_item((_treat,), _("Add user indexes..."),
                              self.add_user_indexes, None)
        self.show()
        self.set_form([(_("Units to display x\u2080:"), (
            "sin(\u03b8)", "d (\u212b)", "d\u207b\u00b2 (\u212b\u207b\u00b2)",
            "\u03b8 (\u00b0)", "2\u03b8 (\u00b0)"), self.select_units)])

    def _find_ints(self):
        groups = find_integers([i[0] for i in self.cryb])
        int_groups = self.int_groups
        ngroups = 0
        shown_groups = []
        for group in groups:
            grp = group[0]
            if grp in shown_groups:
                continue
            shown_groups.append(grp)
            ngroups += 1
            self.value.insert_column(self.value.columns,
                                     f"ints ({ngroups})", int)
            int_groups.append(group[1])
            j = self.value.columns - 1
            for k, v in grp.items():
                self.value.set(k, j, v)

    def _theta_correction(self):
        if self.value.columns < 6:
            return
        if self.value.columns > 6:
            sels = self.get_selected_cells()
            if not sels or not self.value.colname(sels[0][1]).startswith(
                    "ints ("):
                self.print_error(_("select at least one cell "
                                   "from appropriate ints column"))
                return
            c = sels[0][1]
        else:
            c = 5
        grp = c - 5
        keys = set(r for r in range(self.value.rows) if self.value.get(r, c))
        ang = correct_angle([i[0] for i in self.cryb],
                            keys, *self.int_groups[grp])
        print_information("Corrected angle",
                          f"Angle is {ang}\n{keys}\n{self.int_groups[grp]}")

    def select_units(self, u):
        self.display.units = ["sin", "d", "d2", "theta", "2theta"][u]
        self.value.refresh()

    def add_user_indexes(self):
        dlgr = self.input_dialog(_("New index column"), [
            (_("Name:"), ""), (_("Cell:"), CELL_TYPE_N)])
        if dlgr is None:
            return
        name, cell = dlgr
        if name in self._uindex:
            self.print_error(
                _("Index with name `%s' already exists") % name)
            return
        indices = {}
        self._uindex[name] = {"cell": CELL_TYPE_C[cell], "indices": indices}
        self.value.insert_column(self.value.columns, name,
                                 lambda x=indices: HklCell(x))

    def load_miller_indices(self):
        for name in self._uindex:
            try:
                indices = self._uindex[name]["indices"]
            except KeyError:
                continue
            try:
                indices = dict((int(k), v) for k, v in indices.items())
            except ValueError:
                continue
            self._uindex[name]["indices"] = indices
            self.value.insert_column(self.value.columns, name,
                                     lambda x=indices: HklCell(x))


def show_sheet(xrd):
    if "crypbells" not in xrd.extra_data:
        return
    cryb = xrd.extra_data.get("crypbells")
    cryb = sorted(map(tuple, cryb.reshape(len(cryb) // 4, 4)))
    p = xrd.UIs.get("FoundReflexes")
    if p:
        p.show()
        return
    xrd.UIs["FoundReflexes"] = FoundBells(xrd)
