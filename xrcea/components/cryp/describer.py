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
from math import asin, pi


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
        cryb = self.data.extra_data["crypbells"]
        cryb = sorted(map(tuple, cryb.reshape(len(cryb) // 4, 4)))
        tab = Table()
        heads = Row()
        tab.write(heads)
        for i in (_("#"), "x\u2080 (2\u03b8\u00b0)", "h", "w", "s"):
            heads.write(Cell(i))
        for i, t in enumerate(cryb, 1):
            r = Row()
            r.write(Cell(i))
            r.write(Cell(2. * asin(t[0]) * 180. / pi))
            for i in t[1:]:
                r.write(Cell(i, 5))
            tab.write(r)
        doc.write(tab)
