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
"""
"""
from xrcea.core.idata import XrayData
from xrcea.core.description import *
from math import asin, pi, sqrt, log
from .broaderan import BroadAn
from .cellparams import CellParams
_GAUSS_RAD_C = 360. / pi * 2. * sqrt(log(2))
_LORENTZ_RAD_C = 360. / pi * 2.
_VOIT_RAD_C = 360. / pi * 2. * sqrt(sqrt(2.) - 1.)
CALCS_FWHM = {"GaussRad": lambda w: sqrt(w) * _GAUSS_RAD_C,
              "LorentzRad": lambda w: sqrt(w) * _LORENTZ_RAD_C,
              "VoitRad": lambda w: sqrt(w) * _VOIT_RAD_C}


class Describer:
    def __init__(self, xrd):
        if not isinstance(xrd, XrayData):
            return
        self.data = xrd

    def __bool__(self):
        return hasattr(self, "data")

    def write(self, doc):
        if not self:
            return
        if "crypbells" in self.data.extra_data:
            self._write_peaks(doc)

    def _write_peaks(self, doc):
        doc.write(Title(_("Crystall peaks"), 3))
        try:
            shape = self.data.extra_data["crypShape"]
            doc.write(Paragraph(_("Peak shape: %s") % shape))
        except KeyError:
            shape = None
        cryb = self.data.extra_data["crypbells"]
        cryb = sorted(map(tuple, cryb.reshape(len(cryb) // 4, 4)))
        tab = Table()
        heads = Row()
        tab.write(heads)
        transforms = [(lambda x: x) for i in range(4)]
        transforms[0] = lambda x: 2. * asin(x) * 180. / pi
        transforms[2] = CALCS_FWHM.get(shape, lambda x: x)
        w = _("FWHM") if shape in CALCS_FWHM else "w"
        for i in (_("#"), "x\u2080 (2\u03b8\u00b0)", "h", w, "s"):
            heads.write(Cell(i))
        for i, t in enumerate(cryb, 1):
            r = Row()
            r.write(Cell(i))
            for i, v in enumerate(t):
                r.write(Cell(transforms[i](v), 5))
            tab.write(r)
        doc.write(tab)
        cp = CellParams(self.data)
        if cp:
            doc.write(Title(_("Cell params"), 4))
            cp.to_doc(doc)
        try:
            bro = BroadAn(self.data)
        except KeyError:
            pass
        else:
            doc.write(Title(_("Broadering analysis"), 4))
            for name in self.data.extra_data["UserIndexes"].keys():
                doc.write(Title(name, 5))
                bro.to_doc(name, None, doc)
