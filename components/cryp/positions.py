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
from core.vi.spreadsheet import Spreadsheet
from core.application import APPLICATION as APP
from core.vi.value import Tabular, TabCell, Value
from core.vi import Button


class FloatCell(TabCell):
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
        if isinstance(val, str):
            try:
                self.__value = atof(val)
            except ValueError:
                pass
        elif isinstance(val, float):
            self.__value = val
        else:
            raise TypeError("Unknown value type")

    @property
    def real(self):
        return self.__value


def show_sheet(idat):
    cryb = idat.extra_data.get("crypbells")
    if cryb is None:
        return
    val = Tabular(colnames=["x_0", "h", "w", "s", "h k l"])
    for i, data in enumerate(cryb.reshape(len(cryb) // 4, 4)):
        val.insert_row(i, [FloatCell(i) for i in data] + [None])
    p = Spreadsheet("XRCEA", val)
    p.show()
