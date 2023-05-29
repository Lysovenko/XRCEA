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


class Describer:
    def __init__(self, xrd):
        if not isinstance(xrd, XrayData):
            return
        self.data = xrd

    def __bool__(self):
        return hasattr(self, "data")

    def write(self, doc):
        if self:
            doc.append(Paragraph(f"Hello {self.data.name}"))
