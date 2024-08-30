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


class Syngony(Enum):
    "Syngony of crystalline cell"
    Triclinic = 1
    Monoclinic = 2
    Rhombic = 3
    Trigonal = 4
    Tetragonal = 5
    Hexagonal = 6
    Cubic = 7


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


@dataclass
class AdjPat:
    "Adjustable pattern"
    cell: CellParams
    reflexes: List = field(default_factory=list)
