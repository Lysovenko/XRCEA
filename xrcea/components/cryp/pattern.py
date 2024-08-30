# XRCEA (C) 2024 Serhii Lysovenko
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
About adjustable patterns
"""
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum
from math import sqrt, tan, cos, sin


class Syngony(Enum):
    "Syngony of crystalline cell"
    Triclinic = 6
    Monoclinic = 5
    Rhombic = 4
    Trigonal = 3
    Rhombohedral = 3
    Tetragonal = 2
    Hexagonal = 1
    Cubic = 0


@dataclass
class CellParams:
    "Parameters of the cell"
    syngony: Syngony
    a: float
    b: Optional[float] = None
    c: Optional[float] = None
    alpha: Optional[float] = None
    beta: Optional[float] = None
    gamma: Optional[float] = None

    def _d_cubic(self, hkl):
        """Calculate d_hkl for Cubic unit cell"""
        h, k, el = hkl
        d2 = 1.0 / self.a**2 * (h**2 + k**2 + el**2)
        return sqrt(1.0 / d2)

    def _d_orhomb(self, hkl):
        """Calculate d_hkl for Orthorhombic unit cell"""
        h, k, el = hkl
        d2 = (
            1.0 / self.a**2 * h**2
            + 1.0 / self.b**2 * k**2
            + 1.0 / self.c**2 * el**2
        )
        return sqrt(1.0 / d2)

    def _d_hex(self, hkl):
        """Calculate d_hkl for Hexagonal unit cell"""
        h, k, el = hkl
        d2 = (
            4.0 / 3.0 / self.a**2 * (h**2 + h * k + k**2)
            + 1.0 / self.c**2 * el**2
        )
        return sqrt(1.0 / d2)

    def _d_tetra(self, hkl):
        """Calculate d_hkl for Tetrahonal unit cell"""
        h, k, el = hkl
        d2 = (
            1.0 / self.a**2 * (h**2 + k**2) + 1.0 / self.c**2 * el**2
        )
        return sqrt(1.0 / d2)

    def _d_rhombohedral(self, hkl):
        """Calculate d_hkl for Rhombohedral unit cell"""
        h, k, el = hkl
        d2 = (
            1.0
            / self.a**2.0
            * (1.0 + cos(self.alpha))
            * (
                (h**2 + k**2 + el**2)
                - (1.0 - tan(self.alpha / 2.0) ** 2)
                * (h * k + k * el + el * h)
            )
            / (1.0 + cos(self.alpha) - 2.0 * cos(self.alpha) ** 2)
        )
        return sqrt(1.0 / d2)

    def _d_monoclinic(self, hkl):
        """Calculate d_hkl for Monoclinic unit cell"""
        h, k, el = hkl
        d2 = (
            1.0 / self.a**2.0 * (h**2 / sin(self.beta) ** 2)
            + 1.0 / self.b**2 * k**2
            + 1 / self.c**2 * el**2 / (sin(self.beta) ** 2)
            - 2 * h * el / (self.a * self.c * sin(self.beta) * tan(self.beta))
        )
        return sqrt(1.0 / d2)

    def reflex(self, hkl):
        "Calculate reflexes"
        return [
            self._d_cubic,
            self._d_hex,
            self._d_tetra,
            self._d_rhombohedral,
            self._d_orhomb,
            self._d_monoclinic,
        ][self.syngony.value](hkl)


@dataclass
class AdjPat:
    "Adjustable pattern"
    cell: CellParams
    reflexes: List = field(default_factory=list)
