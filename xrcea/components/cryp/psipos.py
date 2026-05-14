# XRCEA (C) 2026 Serhii Lysovenko
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
"""Spreadsheet with peaks positions in Multicurve"""

from .positions import (
    DisplayX0,
    IFloat,
    Spreadsheet,
    Tabular,
    X0Cell,
    copy_to_clipboard,
)

_treat = _("Treat")


class PsiBells(Spreadsheet):
    def __init__(self, mxrd):
        self._xrds = xrds = list(mxrd.get_curves())
        self._uindex = [
            xrd.extra_data.setdefault("UserIndexes", {}) for xrd in xrds
        ]
        crybs = [xrd.extra_data.get("crypbells") for xrd in xrds]
        self.crybs = [
            sorted(map(tuple, cryb.reshape(len(cryb) // 4, 4)))
            for cryb in crybs
        ]
        val = Tabular(colnames=["\u03c8", "x\u2080", "h", "w", "s"])
        self.displays = [DisplayX0("sin", xrd) for xrd in xrds]
        start = 0
        for cryb, display, xrd in zip(self.crybs, self.displays, xrds):
            for i, data in enumerate(cryb, start):
                val.insert_row(
                    i,
                    [IFloat(xrd.psi), X0Cell(data[0], display)]
                    + [IFloat(i) for i in data[1:]],
                )
            start += len(cryb)
        super().__init__(str(mxrd.name) + _(" (found reflexes)"), val)
        self.show()
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
                    self.select_units,
                )
            ]
        )
        self.set_context_menu(
            [
                (
                    _("Copy all"),
                    lambda a, b, c: copy_to_clipboard(
                        "\n".join(
                            "\t".join(
                                str(val.get(r, c)) for c in range(val.columns)
                            )
                            for r in range(val.rows)
                        )
                    ),
                )
            ]
        )

    def select_units(self, u):
        units = ["sin", "d", "d2", "theta", "2theta"][u]
        for display in self.displays:
            display.units = units
        self.value.refresh()


def show_psi_sheet(mxrd):
    if any("crypbells" not in xrd.extra_data for xrd in mxrd.get_curves()):
        return
    p = mxrd._uis.get("FoundReflexes")
    if p:
        p.show()
        return
    mxrd._uis["FoundReflexes"] = PsiBells(mxrd)
