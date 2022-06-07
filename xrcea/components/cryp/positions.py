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
from xrcea.core.vi.spreadsheet import Spreadsheet
from xrcea.core.application import APPLICATION as APP
from xrcea.core.vi.value import Tabular, TabCell, Value, lfloat
from xrcea.core.vi import (Button, print_information, print_error,
                           copy_to_clipboard)
from .indexer import find_indices
from .vcellparams import show_cell_params
_treat = _("Treat")
CELL_TYPE_C, CELL_PARAMS, CELL_TYPE_N = zip(*(
    ("cubic", 1, _("Cubic")),
    ("tetra", 2, _("Tetragonal")),
    ("orhomb", 3, _("Orthorhombic")),
    ("hex", 2, _("Hexagonal")),
    ("rhombohedral", 2, _("Rhombohedral")),
    ("monoclinic", 4, _("Monoclinic")),
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
        try:
            return format_string("%.5g", self._display(self.__value))
        except (ZeroDivisionError, ValueError):
            return _("#VALUE!")

    @value.setter
    def value(self, val):
        pass


class HklCell(TabCell):
    """Cell with Miller indices"""
    def __init__(self, indices, ro=False):
        self._indices = indices
        self._readonly = ro
        super().__init__(False)

    @property
    def value(self):
        return self._indices.get(self.row)

    @value.setter
    def value(self, val):
        if self._readonly:
            return
        try:
            ls = list(map(int, val.split()[:3]))
        except (ValueError, AttributeError):
            if val is None:
                self._indices.pop(self.row, None)
            return
        ls += [0] * (3 - len(ls))
        self._indices[self.row] = ls

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
        self.menu.append_item((_treat,), _("Try find Miller's indices..."),
                              self._find_millers, None)
        self.menu.append_item((_treat,), _("Add user indexes..."),
                              self.add_user_indexes, None)
        self.menu.append_item((_treat,), _("Calculate Cell parameters"),
                              self.calc_cell_params, None)
        self.menu.append_item((_treat,), _("Clear automatic indexation"),
                              self._clear_auto, None)
        self.show()
        self.set_form([(_("Units to display %s:") % "x\u2080", (
            "sin(\u03b8)", "d (\u212b)", "d\u207b\u00b2 (\u212b\u207b\u00b2)",
            "\u03b8 (\u00b0)", "2\u03b8 (\u00b0)"), self.select_units)])
        self.set_context_menu([
            (_("Copy all"), lambda a, b, c: copy_to_clipboard(
                "\n".join("\t".join(
                    str(val.get(r, c)) for c in range(
                        val.columns)) for r in range(val.rows))))])

    def _find_millers(self):
        cryb = self._xrd.extra_data.get("crypbells")
        if cryb is None:
            return
        hwave = self._xrd.lambda1 / 2.
        ipd = sorted(hwave / cryb.reshape(len(cryb) // 4, 4)[:, 0],
                     reverse=True)
        Nless0 = lfloat(0.)
        Angle = lfloat(0., 180.)
        a, b, c = [Value(Nless0) for i in range(3)]
        alp, bet, gam = [Value(Angle) for i in range(3)]
        for i in (alp, bet, gam):
            i.update(90.)

        def relevance(cti):
            rel = {"cubic": (), "tetra": (c,), "orhomb": (b, c), "hex": (c,),
                   "rhombohedral": (alp,), "monoclinic": (b, c, bet)}
            for i in (b, c, alp, bet, gam):
                i.is_relevant(False)
            for i in rel[CELL_TYPE_C[cti]]:
                i.is_relevant(True)
            return ()

        relevance(0)
        dlgr = self.input_dialog(_("Params for search indices"), [
            (_("Minimum peaks:"), len(ipd)),
            (_("Max index:"), 4),
            (_("Max results:"), 5),
            ("a:", a),
            ("b:", b),
            ("c:", c),
            ("\u03b1:", alp),
            ("\u03b2:", bet),
            ("\u03b3:", gam),
            (_("Cell:"), CELL_TYPE_N, relevance)
        ])
        if dlgr is None:
            return
        mp, mi, mr, x, x, x, x, x, x, cs = dlgr
        ipars = [i.get() for i in (a, b, c, alp, bet, gam)]
        if mp > len(self.cryb):
            mp = len(self.cryb)
        if mp <= CELL_PARAMS[cs]:
            self.print_error(
                _("Number of peaks should be greater than number "
                  "of free members"))
            return
        groups = []
        self.bg_process(find_indices(
            ipd, ipars, CELL_TYPE_C[cs],
            mi, mp, mr, groups))
        curauto = 0
        for name in self._uindex:
            if name.startswith("auto"):
                try:
                    curauto = max(curauto, int(name[4:]))
                except ValueError:
                    pass
        for group in groups:
            curauto += 1
            name = "auto%d" % curauto
            hkl = list(map(list, zip(*group[2])))
            indices = {}
            p_hkl = 0
            for i, j in enumerate(group[3]):
                if j:
                    indices[i] = hkl[p_hkl]
                    p_hkl += 1
            self._uindex[name] = {"cell": CELL_TYPE_C[cs],
                                  "indices": indices, "auto": True}
            self.value.insert_column(self.value.columns, name,
                                     lambda x=indices: HklCell(x, True))

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
            if self._uindex[name]["cell"] != CELL_TYPE_C[cell]:
                self._uindex[name]["cell"] = CELL_TYPE_C[cell]
            else:
                self.print_error(
                    _("Index with name `%(n)s' of type %(t)s already exists")
                    % {"n": name, "t": CELL_TYPE_N})
            return
        indices = {}
        self._uindex[name] = {"cell": CELL_TYPE_C[cell], "indices": indices}
        self.value.insert_column(self.value.columns, name,
                                 lambda x=indices: HklCell(x))

    def _clear_auto(self):
        if not self.ask_question(_("Do remove automatically "
                                   "calculated Miller indices?")):
            return
        val = self.value
        for i in reversed(range(val.columns)):
            name = val.colname(i)
            if name.startswith("auto") and self._uindex[name].get("auto"):
                self._uindex.pop(name)
                val.remove_column(i)

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
            ro = self._uindex[name].get("auto")
            self.value.insert_column(self.value.columns, name,
                                     lambda x=indices, y=ro: HklCell(x, y))

    def calc_cell_params(self):
        show_cell_params(self._xrd)


def show_sheet(xrd):
    if "crypbells" not in xrd.extra_data:
        return
    p = xrd.UIs.get("FoundReflexes")
    if p:
        p.show()
        return
    xrd.UIs["FoundReflexes"] = FoundBells(xrd)
