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
"""Analise peaks broadering"""
from numpy import sqrt, array, corrcoef
from scipy.optimize import fmin

_GAUSS_RAD_C = 360. / pi * 2. * sqrt(log(2))
_LORENTZ_RAD_C = 360. / pi * 2.
_VOIT_RAD_C = 360. / pi * 2. * sqrt(sqrt(2.) - 1.)
CALCS_FWHM = {"GaussRad": lambda w: sqrt(w) * _GAUSS_RAD_C,
              "LorentzRad": lambda w: sqrt(w) * _LORENTZ_RAD_C,
              "VoitRad": lambda w: sqrt(w) * _VOIT_RAD_C}


class BroadAn:
    def __init__(self, xrd):
        extra_data = xrd.extra_data
        cryb = extra_data["crypbells"].reshape(len(cryb) // 4, 4)
        self.shape = shape = extra_data["crypShape"]
        cryb[:, 1] = CALCS_FWHM[shape](cryb[:, 2])
        self.cryb = array(sorted(map(tuple, cryb[:, :2])))
        indexed = {name: set(int(i) for i in v.keys())
                   for name, v in extra_data["UserIndexes"].items()}
        self.selected = {name: [i in v for i in range(len(cryb))]
                         for name, v in indexed.items()}

    def b_samp(self, b_instr, b_tot):
        assert self.shape in ("GaussRad", "LorentzRad")
        if self.shape == "GaussRad":
            return sqrt(b_tot**2 - b_instr**2)
        if self.shape == "LorentzRad":
            return b_tot - b_instr

    def corr(self, b_instr, x, y, cos_t):
        return corrcoef(x, self.b_samp(b_instr, y) * cos_t)[0, 1]

    def fminstr(self, name):
        cryb = self.cryb[self.selected[name]]
        inst = cryb[:, 1].mean() / 2.
        x = cryb[:, 0]
        y = cryb[:, 1]
        cos_t = sqrt(1. - x**2)

        def min_it(instr):
            return 1. - self.corr(instr[0], x, y, cos_t)**2
        opt = fmin(min_it, [inst])
