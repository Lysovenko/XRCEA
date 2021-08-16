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
from .cellparams import CALCULATORS, get_dhkl
from xrcea.core.application import APPLICATION as APP
_calculate = _("Calculate")


class DisplayCellParams(Page):
    def __init__(self, xrd):
        self._xrd = xrd
        super().__init__(str(xrd.name) + _(" (cell params)"), None)
        self.menu.append_item((_calculate,), _("Cell parameters"),
                              self.calc_pars, None)
        for name, func in APP.runtime_data["cryp"].get("extra_calcs", []):
            self.menu.append_item((_calculate,), name,
                                  self.wrap_extras(func), None)
        self.show()
        self.calc_pars()

    def calc_pars(self):
        cryb = self._xrd.extra_data.get("crypbells")
        hwave = self._xrd.lambda1 / 2.
        ipd = sorted(hwave / cryb.reshape(len(cryb) // 4, 4)[:, 0],
                     reverse=True)
        indset = self._xrd.extra_data.get("UserIndexes")
        res = {}
        for name in indset:
            inds = indset[name]["indices"]
            try:
                res[name] = CALCULATORS[indset[name]["cell"]](
                    get_dhkl(ipd, inds)), indset[name]["cell"]
            except KeyError:
                print(f"TODO: calculator for {indset[name]['cell']}")
                pass
        self.print_res(res)

    def print_res(self, res):
        pnr = ["a", "b", "c", "\u03b1", "\u03b2", "\u03b3", "\\chi^2",
               "\\sigma^2_a", "\\sigma^2_b", "\\sigma^2_c",
               "\\sigma^2_\\alpha", "\\sigma^2_\\beta",
               "\\sigma^2_\\gamma"]
        cells = []
        self.set_text(
            "\n".join(
                "%s (%s):\t" % (k, v[1]) + "\t".join(
                    "%s= %g" % t for t in zip(pnr, v[0]) if t[1] is not None)
                for k, v in res.items()))

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
