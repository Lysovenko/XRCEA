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
from numpy import pi, log, sqrt, array, corrcoef, vstack, ones
from numpy.linalg import lstsq
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
        self._lambda = xrd.lambda1
        cryb = extra_data["crypbells"]
        cryb = cryb.reshape(len(cryb) // 4, 4)
        self.shape = shape = extra_data["crypShape"]
        cryb[:, 1] = CALCS_FWHM[shape](cryb[:, 2])
        self.cryb = array(sorted(map(tuple, cryb[:, :2])))
        indexed = {name: set(int(i) for i in v["indices"].keys())
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

    @staticmethod
    def _x_y_cos_t(cryb):
        x = cryb[:, 0]
        y = cryb[:, 1]
        cos_t = sqrt(1. - x**2)
        return x, y, cos_t

    def size_strain(self, name, b_instr):
        cryb = self.cryb[self.selected[name]]
        x, y, cos_t = self._x_y_cos_t(cryb)
        a, b = lstsq(vstack([x, ones(len(x))]).T,
                     self.b_samp(b_instr, y) * cos_t, rcond=None)[0]
        L = 0.9 * self._lambda / b
        E = a / 4
        return L, E

    def fminstr(self, name):
        cryb = self.cryb[self.selected[name]]
        inst = cryb[:, 1].mean()
        x, y, cos_t = self._x_y_cos_t(cryb)

        def min_it(instr):
            return -abs(self.corr(instr[0], x, y, cos_t))
        opt = fmin(min_it, [inst], initial_simplex=[[inst], [inst / 16.]])
        return opt[0]

    def as_text(self, name, b_instr=None):
        if b_instr is None:
            b_instr = self.fminstr(name)
        size, strain = self.size_strain(name, b_instr)
        cor = self.corr(b_instr,
                        *self._x_y_cos_t(self.cryb[self.selected[name]]))
        x, y, c = self._x_y_cos_t(self.cryb[self.selected[name]])
        if len(y):
            brm = y.max()
            s = "\n".join("%g\t%.9g\t%g\t%g" % (
                (br, self.corr(br, x, y, c)) + self.size_strain(name, br))
                for br in map(lambda i: i * brm / 10000., range(-50, 75)))

            def ex(br=0):
                for j in range(len(x)):
                    ar = [True] * j + [False] + [True] * (len(x) - j - 1)
                    yield self.corr(br, x[ar], y[ar], c[ar])

            s += "\n\n" + "\n".join("%g\t%g\t%g\t%g" % i
                                    for i in zip(
                                        x, y * c,
                                        self.b_samp(brm / 3, y) * c,
                                        self.b_samp(brm / 2, y) * c))
        else:
            s = None
        return (f"name: \"{name}\"\nshape: {self.shape}\n"
                f"size = {size}\nstrain = {strain}\ncorr = {cor}\n"
                f"instr = {b_instr}\n{s}\n")

    def text_all(self, b_instr=None):
        return "\n".join(self.as_text(name, b_instr) for name in self.selected)
