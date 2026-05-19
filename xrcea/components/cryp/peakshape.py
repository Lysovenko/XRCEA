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
"""Wrap XrayData with peak-related methods"""

import numpy as np


class PeaksShape:
    def __init__(self, xrd):
        self._xrd = xrd

    @property
    def shape(self):
        return self._xrd.extra_data.get("crypShape")

    @shape.setter
    def shape(self, shape):
        shapes = (
            "Gauss",
            "Lorentz",
            "Voit",
            "GaussRad",
            "LorentzRad",
            "VoitRad",
        )
        if shape not in shapes:
            raise ValueError(f"Unknown shape: {shape}")
        self._xrd.extra_data["crypShape"] = shape

    @property
    def bells(self):
        bls = self._xrd.extra_data.get("crypbells")
        if bls is None:
            return bls
        return np.reshape(bls, (len(bls) // 4, 4))

    @bells.setter
    def bells(self, bls):
        self._xrd.extra_data["crypbells"] = np.ravel(bls)
