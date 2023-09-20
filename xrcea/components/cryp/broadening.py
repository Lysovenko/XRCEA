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
"""Analise peaks broadening"""
from locale import format_string
from numpy import pi, log, sqrt, array, corrcoef, vstack, ones
from numpy.linalg import lstsq
from scipy.optimize import fmin
from xrcea.core.description import Table, Row, Cell

_GAUSS_RAD_C = 360.0 / pi * 2.0 * sqrt(log(2))
_LORENTZ_RAD_C = 360.0 / pi * 2.0
_VOIT_RAD_C = 360.0 / pi * 2.0 * sqrt(sqrt(2.0) - 1.0)
CALCS_FWHM = {
    "GaussRad": lambda w: sqrt(w) * _GAUSS_RAD_C,
    "LorentzRad": lambda w: sqrt(w) * _LORENTZ_RAD_C,
    "VoitRad": lambda w: sqrt(w) * _VOIT_RAD_C,
}


# TODO: take into account variability of Young's modulus
# https://doi.org/10.1016/j.scriptamat.2004.05.007
# http://pd.chem.ucl.ac.uk/pdnn/peaks/broad.htm
class BroadAn:
    def __init__(self, xrd):
        extra_data = xrd.extra_data
        self._lambda = xrd.lambda1
        self._instr_broad = extra_data.get("crypInstrumental", {}).get(
            "Broadening"
        )
        cryb = extra_data["crypbells"]
        cryb = cryb.reshape(len(cryb) // 4, 4)
        self.shape = shape = extra_data["crypShape"]
        if self.shape not in ("GaussRad", "LorentzRad"):
            raise KeyError("Unsupported shape")
        cryb[:, 1] = CALCS_FWHM[shape](cryb[:, 2])
        self.cryb = array(sorted(map(tuple, cryb[:, :2])))
        indexed = {
            name: set(int(i) for i in v["indices"].keys())
            for name, v in extra_data["UserIndexes"].items()
        }
        self.selected = {
            name: [i in v for i in range(len(cryb))]
            for name, v in indexed.items()
        }

    def b_samp(self, b_instr, b_tot):
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
        cos_t = sqrt(1.0 - x**2)
        return x, y, cos_t

    def size_strain(self, name, b_instr):
        cryb = self.cryb[self.selected[name]]
        x, y, cos_t = self._x_y_cos_t(cryb)
        a, b = lstsq(
            vstack([x, ones(len(x))]).T,
            self.b_samp(b_instr, y) * cos_t,
            rcond=None,
        )[0]
        L = 0.9 * self._lambda / b
        E = a / 4
        return L, E

    def fmin_instrumental(self, name):
        cryb = self.cryb[self.selected[name]]
        inst = cryb[:, 1].mean()
        x, y, cos_t = self._x_y_cos_t(cryb)

        def min_it(instr):
            return -abs(self.corr(instr[0], x, y, cos_t))

        opt = fmin(min_it, [inst], initial_simplex=[[inst], [inst / 16.0]])
        return opt[0]

    def _params_to_display(self, name, b_instr):
        if b_instr is None:
            b_instr = self.fmin_instrumental(name)
        size, strain = self.size_strain(name, b_instr)
        cor = self.corr(
            b_instr, *self._x_y_cos_t(self.cryb[self.selected[name]])
        )
        return (size, strain, b_instr, cor)

    def as_text(self, name):
        b_instr = self._instr_broad
        size, strain, b_instr, cor = self._params_to_display(name, b_instr)
        x, y, c = self._x_y_cos_t(self.cryb[self.selected[name]])
        if len(y):
            brm = b_instr
            s = "\n".join(
                format_string(
                    "%g\t%.9g\t%g\t%g",
                    (br, self.corr(br, x, y, c)) + self.size_strain(name, br),
                )
                for br in map(lambda i: i * brm / 100.0, range(0, 125))
            )

            def ex(br=0):
                for j in range(len(x)):
                    ar = [True] * j + [False] + [True] * (len(x) - j - 1)
                    yield self.corr(br, x[ar], y[ar], c[ar])

            s += "\n\n\n" + "\n".join(
                format_string("%g\t%g\t%g\t%g", i)
                for i in zip(
                    x,
                    y * c,
                    self.b_samp(brm / 3, y) * c,
                    self.b_samp(brm / 2, y) * c,
                )
            )
        else:
            s = None
        return (
            f'name: "{name}"\nshape: {self.shape}\n'
            f"size = {size}\nstrain = {strain}\ncorr = {cor}\n"
            f"instr = {b_instr}\n{s}\n"
        )

    def to_text(self):
        return "\n".join(self.as_text(name) for name in self.selected)

    def to_doc(self, doc):
        b_instr = self._instr_broad
        tab = Table()
        r = Row()
        for cn in (
            _("Name"),
            _("Coherent block size"),
            _("Strain"),
            _("Instrumental broadening"),
            _("Correlation Coefficient"),
        ):
            r.write(Cell(cn))
        tab.write(r)
        for name in sorted(self.selected.keys()):
            size, strain, br_instr, cor = self._params_to_display(
                name, b_instr
            )
            r = Row()
            r.write(Cell(name))
            r.write(Cell(size))
            r.write(Cell(strain))
            r.write(Cell(br_instr))
            r.write(Cell(cor))
            tab.write(r)
        doc.write(tab)
