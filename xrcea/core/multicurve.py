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
"""Multiple curves"""

from .idata import XrayData
from .vi import Lister
from .vi.value import Value


class MultiXrCurve:
    objtype = "multi_xrd"
    type = _("Multiple diffractograms")

    def __init__(self, obj=None):
        self._curves = []
        self._uis = {}
        if isinstance(obj, dict):
            self.from_obj(obj)

    def add(self, xrd):
        self._curves.append(xrd)

    def get_curves(self):
        self._curves.sort(key=lambda x: x.psi)
        return self._curves

    def get_obj(self):
        """Convets X-ray data into object."""
        mxrd = {"objtype": self.objtype}
        mxrd["xrds"] = [i.get_obj() for i in self._curves]
        return mxrd

    def from_obj(self, mxrd):
        """Get Multicurve from dict"""
        assert mxrd["objtype"] == self.objtype
        self._curves = [XrayData(obj) for obj in mxrd["xrds"]]
        self.name = mxrd.get("name", "Undefined")
        return self

    def display(self):
        lst = self._uis.get("main")
        if not lst:
            self._uis["main"] = lst = ViMultiXrCurve(self)
        lst.show()

    def set_container(self, container):
        for c in self.get_curves():
            c.set_container(container)


class ViMultiXrCurve(Lister):
    def __init__(self, multicurve: MultiXrCurve):
        self.multicurve = multicurve
        self.curves = curves = Value(list)
        curves.update(
            [(str(c.psi), c.name, None, c) for c in multicurve.get_curves()]
        )
        styles = {}
        super().__init__(
            multicurve.name,
            [
                (_("Curves"), ("\u03c8", _("Name"))),
            ],
            [curves],
            styles,
        )
        self.show()
        self.set_choicer(self.click_component, False, 0)

    def click_component(self, item):
        item[-1].display()
