# XRCEA (C) 2023 Serhii Lysovenko
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
""" """

from math import asin, log, pi, sqrt

from xrcea.core.description import Cell, Paragraph, Row, Table, Title
from xrcea.core.idata import XrayData

from .broadening import BroadAn
from .cellparams import CellParams

_GAUSS_RAD_C = 360.0 / pi * 2.0 * sqrt(log(2))
_LORENTZ_RAD_C = 360.0 / pi * 2.0
_VOIT_RAD_C = 360.0 / pi * 2.0 * sqrt(sqrt(2.0) - 1.0)
CALCS_FWHM = {
    "GaussRad": lambda w: sqrt(w) * _GAUSS_RAD_C,
    "LorentzRad": lambda w: sqrt(w) * _LORENTZ_RAD_C,
    "VoitRad": lambda w: sqrt(w) * _VOIT_RAD_C,
}


class Describer:
    def __init__(self, sett):
        self.name = _("Crystal peaks")
        self.__sett = sett

    def write(self, xrd, doc):
        if not isinstance(xrd, XrayData):
            return
        if "crypbells" in xrd.extra_data:
            self._write_peaks(xrd, doc)

    def _write_peaks(self, xrd, doc):
        doc.write(Title(_("Crystall peaks"), 3))
        try:
            shape = xrd.extra_data["crypShape"]
            doc.write(Paragraph(_("Peak shape: %s") % shape))
        except KeyError:
            shape = None
        if self.__sett["show_cryps_tab"]:
            tab = self._cryps_tab(xrd, shape)
            doc.write(tab)
        cp = CellParams(xrd)
        if cp:
            doc.write(Title(_("Cell params"), 4))
            cp.to_doc(doc)
        try:
            bro = BroadAn(xrd)
        except KeyError:
            pass
        else:
            doc.write(Title(_("Broadening analysis"), 4))
            bro.to_doc(doc)

    def _cryps_tab(self, xrd, shape):
        uindex = xrd.extra_data.get("UserIndexes", dict())
        cryb = xrd.extra_data["crypbells"]
        cryb = sorted(map(tuple, cryb.reshape(len(cryb) // 4, 4)))
        tab = Table()
        heads = Row()
        tab.write(heads)
        transforms = [(lambda x: x) for i in range(4)]
        transforms[0] = lambda x: 2.0 * asin(x) * 180.0 / pi
        transforms[2] = CALCS_FWHM.get(shape, lambda x: x)
        w = _("FWHM") if shape in CALCS_FWHM else "w"
        inames = sorted(i for i in uindex if "indices" in uindex[i])
        indices = [
            {
                int(k): "%d %d %d" % tuple(v)
                for k, v in uindex[n]["indices"].items()
            }
            for n in inames
        ]
        for j in [_("#"), "x\u2080 (2\u03b8\u00b0)", "h", w, "s"] + inames:
            heads.write(Cell(j))
        for i, t in enumerate(cryb, 1):
            r = Row()
            r.write(Cell(i))
            for j, v in enumerate(t):
                r.write(Cell(transforms[j](v), 5))
            for ind in indices:
                r.write(Cell(ind.get(i - 1, ""), 5))
            tab.write(r)
        return tab

    def settings_dialog(self, caller):
        dlgr = caller.input_dialog(
            _("Describe peaks settings"),
            [(_("Show shapes table:"), self.__sett["show_cryps_tab"])],
        )
        if dlgr is None:
            return
        self.__sett["show_cryps_tab"] = dlgr[0]
