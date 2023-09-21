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
"""Display cell params"""

from xrcea.core.vi import Page
from xrcea.core.application import APPLICATION as APP
from .cellparams import CellParams
from .broadening import BroadAn

_calculate = _("Calculate")


class DisplayCellParams(Page):
    """Calculator"""

    def __init__(self, xrd):
        self._xrd = xrd
        super().__init__(str(xrd.name) + _(" (cell params)"), None)
        self.menu.append_item(
            (_calculate,), _("Cell parameters"), self.calc_pars, None
        )
        self.menu.append_item(
            (_calculate,), _("Analyse Peak broadening"), self.calc_broad, None
        )
        for name, func in APP.runtime_data["cryp"].get("extra_calcs", []):
            self.menu.append_item(
                (_calculate,), name, self.wrap_extras(func), None
            )
        self.show()
        self.calc_pars()

    def calc_pars(self):
        cp = CellParams(self._xrd)
        if cp:
            self.set_text(cp.to_text())
        else:
            self.print_error(_("Unable to find cell params"))

    def calc_broad(self):
        try:
            bro = BroadAn(self._xrd)
        except KeyError:
            self.print_error(_("Unable to analyse broadening"))
            return
        self.set_text(bro.to_text())

    def wrap_extras(self, extra):
        def wrapped():
            extra(self._xrd, self)

        return wrapped


def show_cell_params(xrd):
    if "crypbells" not in xrd.extra_data:
        return
    if not xrd.extra_data.get("UserIndexes"):
        return
    p = xrd.UIs.get("CellParams")
    if p:
        p.show()
        return
    xrd.UIs["CellParams"] = DisplayCellParams(xrd)
