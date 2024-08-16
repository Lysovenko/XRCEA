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
import json
from locale import atof, format_string
from math import asin, pi, sin
from xrcea.core.vi.value import Tabular, TabCell, Value, lfloat
from xrcea.core.vi.spreadsheet import Spreadsheet
from xrcea.core.vi import ask_save_filename, ask_open_filename

_edit = _("Edit")  # type: ignore[undefined-variable]


class PeakLocator:
    "Locate peaks"

    def __init__(self, units, wavel):
        self.units = units
        self.wavel = wavel

    def to_units(self, val):
        "d to some units"
        if self.units == "sin":
            return self.wavel / (2.0 * val)
        if self.units == "d2":
            return val**-2
        if self.units == "theta":
            return asin(self.wavel / (2.0 * val)) * 180.0 / pi
        if self.units == "2theta":
            return asin(self.wavel / (2.0 * val)) * 360.0 / pi
        return val

    def to_d(self, val):
        "some units to d"
        if self.units == "sin":
            return self.wavel / (2.0 * val)
        if self.units == "d2":
            return val**-0.5
        if self.units == "theta":
            return self.wavel / (2.0 * sin(val * pi / 180.0))
        if self.units == "2theta":
            return self.wavel / (2.0 * sin(val * pi / 360.0))
        return val


class PosCell(TabCell):
    """Cell with peak position"""

    def __init__(self, cont, locator):
        self._locator = locator
        self.__cont = cont
        super().__init__()

    @property
    def value(self):
        "return cell's value"
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
                "%.5g", self._locator.to_units(self.__cont[0])
            )
        except (ValueError, ZeroDivisionError):
            return ""

    def shift_in_units(self, shift):
        "Shift peak in some units"
        try:
            self.__cont[0] = self._locator.to_d(
                self._locator.to_units(self.__cont[0]) + shift
            )
        except (ValueError, ZeroDivisionError):
            pass


class CompCard:
    """Card to compare with"""

    def __init__(self, crd, locator):
        self._crd = crd
        self._locator = locator
        self._parnames = [_("Number"), _("Name"), _("Formula")]
        self._par_ids = ["number", "name", "formula"]
        params = crd.get("params", ())
        self._cellpars = [
            i for i in "a b c alpha beta gamma".split() if i in params
        ]
        if crd.get("spacegroup"):
            self._parnames.append(_("Spacegroup"))
            self._par_ids.append("spacegroup")
        self._parnames.extend(self._cellpars)
        self.rows = max((len(crd["reflexes"]), len(self._parnames)))

    def __int__(self):
        return self._cno

    def get(self, row, col):
        if col == 0:
            try:
                return PosCell(self._crd["reflexes"][row], self._locator)
            except (KeyError, IndexError):
                return
        if col == 1:
            try:
                if row in self._crd.get("extinguished", ()):
                    return str(self._crd["reflexes"][row][1]) + " *"
                return str(self._crd["reflexes"][row][1])
            except (KeyError, IndexError):
                return
        if col == 2:
            try:
                return " ".join(map(str, self._crd["reflexes"][row][2]))
            except (KeyError, IndexError):
                return
        if col == 3:
            try:
                return self._parnames[row]
            except IndexError:
                return
        if col == 4:
            try:
                return self._crd[self._par_ids[row]]
            except KeyError:
                return
            except IndexError:
                pass
            try:
                return format_string(
                    "%.5g",
                    self._crd["params"][
                        self._cellpars[row - len(self._par_ids)]
                    ],
                )
            except (KeyError, IndexError):
                return

    def set(self, row, col, data):
        if col == 0:
            return self._fit_resize(row, data)

    def switch(self, rows):
        if not rows:
            return
        self._crd["extinguished"] = list(
            set(self._crd.get("extinguished", ())).symmetric_difference(rows)
        )

    def resize_by(self, factor):
        for r in self._crd["reflexes"]:
            r[0] *= factor
        for p in ("a", "b", "c"):
            try:
                self._crd["params"][p] *= factor
            except KeyError:
                pass

    def _fit_resize(self, row, data):
        try:
            before = self._crd["reflexes"][row][0]
            after = self._locator.to_d(atof(str(data)))
            factor = abs(after / before)
        except (KeyError, IndexError, ValueError, ZeroDivisionError):
            return
        self.resize_by(factor)


class CompCards(Tabular):
    """Cards to compare with"""

    def __init__(self, xrd, locator):
        self._locator = locator
        self._cards = xrd.extra_data.setdefault("CompCards", {})
        self._comp_cards = []
        super().__init__(
            colnames=["x\u2080", "I", "(h k l)", _("Parameter"), _("Value")]
        )
        self.from_origin()

    @property
    def rows(self):
        return sum(i.rows for i in self._comp_cards)

    def from_origin(self):
        self._comp_cards.clear()
        self._comp_cards.extend(
            CompCard(self._cards[cno], self._locator)
            for cno in sorted(self._cards, key=int)
        )

    def get(self, row, col):
        nr = 0
        for card in self._comp_cards:
            if row < nr + card.rows:
                return card.get(row - nr, col)
            nr += card.rows

    def set(self, row, col, data):
        nr = 0
        for card in self._comp_cards:
            if row < nr + card.rows:
                return card.set(row - nr, col, data)
            nr += card.rows

    def on_del_pressed(self, cells):
        start = 0
        cells = list(cells)
        for card in self._comp_cards:
            end = start + card.rows
            card.switch(
                set(
                    c[0] - start for c in cells if c[0] >= start and c[0] < end
                )
            )
            start = end
        self.refresh()

    def resize_by(self, factor, cells):
        start = 0
        for card in self._comp_cards:
            end = start + card.rows
            if [1 for c in cells if c[0] >= start and c[0] < end]:
                card.resize_by(factor)
            start = end
        self.refresh()

    def export_cards(self, fname):
        "Export cards to file"
        with open(fname, "w", encoding="utf8") as fptr:
            json.dump(self._cards, fptr, indent=4)

    def import_cards(self, fname):
        "Import cards from file"
        with open(fname, encoding="utf8") as fptr:
            self._cards.update(json.load(fptr))


class AssumedCards(Spreadsheet):
    def __init__(self, idat):
        self._xrd = idat
        to_show = PeakLocator("sin", idat.lambda1)
        self._tab = tab = CompCards(idat, to_show)
        super().__init__(str(idat.name) + _(" (assumed cards)"), tab)
        self.reread()
        self.menu.append_item((_edit,), _("Shift by..."), self.shift_by, None)
        self.menu.append_item(
            (_edit,), _("Resize by..."), self.resize_by, None
        )
        self.menu.append_item((_edit,), _("Export..."), self.export_tab, None)
        self.menu.append_item((_edit,), _("Import..."), self.import_tab, None)
        self.show()

        def select_units(units):
            to_show.units = ["sin", "d", "d2", "theta", "2theta"][units]
            tab.refresh()

        self.set_form(
            [
                (
                    _("Units to display %s:") % "x\u2080",
                    (
                        "sin(\u03b8)",
                        "d (\u212b)",
                        "d\u207b\u00b2 (\u212b\u207b\u00b2)",
                        "\u03b8 (\u00b0)",
                        "2\u03b8 (\u00b0)",
                    ),
                    select_units,
                )
            ]
        )

    def reread(self):
        self._tab.from_origin()

    def shift_by(self):
        sels = [c[0] for c in self.get_selected_cells() if c[1] == 0]
        if not sels:
            self.print_error(_("No cells selected."))
            return
        shift = Value(lfloat())
        dlgr = self.input_dialog(
            _("Shift selected cells"), [(_("Shift by:"), shift)]
        )
        if dlgr is None:
            return
        for i in sels:
            self._tab.get(i, 0).shift_in_units(shift.get())

    def resize_by(self):
        sels = list(self.get_selected_cells())
        if not sels:
            self.print_error(_("No cards selected."))
            return
        factor = Value(lfloat(0.001, 5.0, 1.0))
        dlgr = self.input_dialog(
            _("Resize selected cards"), [(_("Resize by:"), factor)]
        )
        if dlgr is None:
            return
        self._tab.resize_by(factor.get(), sels)

    def export_tab(self):
        "export table to json"
        fname = ask_save_filename(
            _("Export table"), "", [("*.json", _("JSON dump"))]
        )
        if fname:
            if not fname.endswith(".json"):
                fname += ".json"
            self._tab.export_cards(fname)

    def import_tab(self):
        "Import table from JSON"
        fname = ask_open_filename(
            _("Import table"), "", [("*.json", _("JSON dump"))]
        )
        if fname:
            self._tab.import_cards(fname)
            self._tab.from_origin()
            self.show()


def show_assumed(idat):
    predef = idat.UIs.get("AssumedCards")
    if predef:
        predef.show()
        return
    idat.UIs["AssumedCards"] = AssumedCards(idat)
