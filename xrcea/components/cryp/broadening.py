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

from numpy import (
    array,
    corrcoef,
    iscomplexobj,
    linspace,
    log,
    ones,
    pi,
    radians,
    roots,
    sin,
    sqrt,
    vstack,
    zeros,
)
from numpy.linalg import lstsq
from scipy.optimize import fmin

from xrcea.core.description import Cell, Row, Table

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
        self.miller_indices = {
            name: [
                i[1]
                for i in sorted(v["indices"].items(), key=lambda x: int(x[0]))
            ]
            for name, v in extra_data["UserIndexes"].items()
        }
        self.selected = {
            name: [i in v for i in range(len(cryb))]
            for name, v in indexed.items()
        }

    def b_samp(self, b_instr, b_tot, sin_t=None, err=False):
        if isinstance(b_instr, float):
            if self.shape == "GaussRad":
                return sqrt(b_tot**2 - b_instr**2)
            if self.shape == "LorentzRad":
                return b_tot - b_instr
        cos_t = sqrt(1 - sin_t**2)
        tan_t = sin_t / cos_t
        if self.shape == "GaussRad":
            cag_u, cag_v, cag_w = b_instr
            b2_g = cag_u * tan_t**2 + cag_v * tan_t + cag_w
            root_of = b_tot**2 - b2_g
            if err:
                if b2_g.min() < 0.0:
                    raise ValueError(b2_g.min())
                if root_of.min() < 0.0:
                    raise ValueError(root_of.min())
                if not iscomplexobj(roots([cag_u, cag_v, cag_w])):
                    x = -cag_v / 2.0 / cag_u
                    raise ValueError(
                        sqrt(abs(cag_u * x**2 + cag_v * x + cag_w))
                    )
            return sqrt(root_of)
        if self.shape == "LorentzRad":
            tch_x, tch_y = b_instr
            b_l = tch_x * tan_t + tch_y / cos_t
            if err:
                if b_l.min() < 0.0:
                    raise ValueError(b_l.min())
            return b_tot - b_l

    def b_instr(self, sin_t, coefs):
        cos_t = sqrt(1 - sin_t**2)
        tan_t = sin_t / cos_t
        if self.shape == "GaussRad":
            cg_u, cg_v, cg_w = coefs
            b2_g = cg_u * tan_t**2 + cg_v * tan_t + cg_w
            return sqrt(b2_g)
        if self.shape == "LorentzRad":
            tch_x, tch_y = coefs
            return tch_x * tan_t + tch_y / cos_t

    def corr(self, b_instr, x, y, cos_t):
        return corrcoef(x, self.b_samp(b_instr, y, x) * cos_t)[0, 1]

    @staticmethod
    def _x_y_cos_t(cryb):
        x = cryb[:, 0]
        y = cryb[:, 1]
        cos_t = sqrt(1.0 - x**2)
        return x, y, cos_t

    def size_strain(self, name, b_instr, x_y_cos=None):
        """http://pd.chem.ucl.ac.uk/pdnn/peaks/sizedet.htm"""
        if x_y_cos is None:
            cryb = self.cryb[self.selected[name]]
            x, y, cos_t = self._x_y_cos_t(cryb)
        else:
            x, y, cos_t = x_y_cos
        a, b = lstsq(
            vstack([x, ones(len(x))]).T,
            self.b_samp(b_instr, y, x) * cos_t,
            rcond=None,
        )[0]
        size = 0.9 * self._lambda / b
        strain = a / 4
        return size, strain

    def opt_instrumental_cor(self, name):
        shape_len = {"GaussRad": 3, "LorentzRad": 2}
        cryb = self.cryb[self.selected[name]]
        x, y, cos_t = self._x_y_cos_t(cryb)
        x_0 = zeros(shape_len[self.shape])
        if x.size == 0:
            return x_0

        def min_it(instr):
            try:
                b_s = self.b_samp(instr, y, x, err=True)
            except ValueError as err:
                return 2.0 - err.args[0]
            if b_s.min() < 0.0:
                return 3.0 - b_s.min()
            penalty = 0.0
            b_sc = b_s * cos_t
            a, b = lstsq(
                vstack([x, ones(len(x))]).T,
                b_sc,
                rcond=None,
            )[0]
            if b < 0.0:
                penalty += sqrt(-b)
            return 1 - corrcoef(x, b_sc)[0, 1] ** 2 + penalty

        opt = fmin(min_it, x_0)
        return opt

    def opt_instrumental_size(self, name):
        cryb = self.cryb[self.selected[name]]
        x_y_cos = self._x_y_cos_t(cryb)
        inst = x_y_cos[1].mean() / 4.0

        def min_it(instr):
            return -self.size_strain(None, instr[0], x_y_cos)[0]

        opt = fmin(min_it, [inst], initial_simplex=[[inst], [inst / 2.0]])
        return opt[0]

    def _params_to_display(self, name, b_instr):
        if b_instr is None or b_instr == "cor":
            try:
                b_instr = self.opt_instrumental_cor(name)
            except ValueError:
                return (None,) * 4
        elif b_instr == "size":
            b_instr = self.opt_instrumental_size(name)
        size, strain = self.size_strain(name, b_instr)
        cor = self.corr(
            b_instr, *self._x_y_cos_t(self.cryb[self.selected[name]])
        )
        return (size, strain, str(b_instr), cor)

    def plot_instr_broad(self, start, stop, points):
        coefs = self._instr_broad
        if not isinstance(coefs, list):
            return
        if start < 0 or stop >= 180 or stop <= start:
            return
        angles = linspace(start, stop, points)
        sin_t = sin(radians(angles) / 2)
        try:
            y = self.b_instr(sin_t, coefs)
        except ValueError:
            return
        return [{"x1": angles, "y1": y, "type": "-"}]

    def plot_correlation(self, name, start, stop, points):
        x, y, c = self._x_y_cos_t(self.cryb[self.selected[name]])
        broadening = linspace(start, stop, points)
        correlation = array([self.corr(br, x, y, c) for br in broadening])
        return {"x1": broadening, "y1": correlation, "legend": name}

    def plot_lstsq(self, name, start, stop, points):
        x, y, cos_t = self._x_y_cos_t(self.cryb[self.selected[name]])
        broadening = linspace(start, stop, points)
        xmat = vstack([x, ones(len(x))]).T

        def ab_chi(b_instr):
            (a, b), c = lstsq(
                xmat, self.b_samp(b_instr, y, x) * cos_t, rcond=None
            )[:2]
            return a, b, c[0]

        abc = array([ab_chi(br) for br in broadening])
        return [
            {"x1": broadening, "y1": abc[:, 0], "type": "-", "legend": name},
            {"x1": broadening, "y1": abc[:, 1], "type": "--"},
            {"x1": broadening, "y2": abc[:, 2], "type": "."},
        ]

    def plot_size_strain(self, name, start, stop, points):
        broadening = linspace(start, stop, points)
        size_strain = array([self.size_strain(name, br) for br in broadening])
        return [
            {
                "x1": broadening,
                "y1": size_strain[:, 0],
                "legend": _("size ") + name,
                "type": "-",
            },
            {
                "x1": broadening,
                "y2": size_strain[:, 1],
                "legend": _("strain ") + name,
                "type": "--",
            },
        ]

    def plot_williamson_hall(self, name, do_opt):
        cryb = self.cryb[self.selected[name]]
        x, y, cos_t = self._x_y_cos_t(cryb)
        b_instr = (
            self._instr_broad if isinstance(self._instr_broad, list) else None
        )
        if b_instr is None or do_opt:
            b_instr = self.opt_instrumental_cor(name).tolist()
        y_t = y * cos_t
        y = self.b_samp(b_instr, y, x) * cos_t
        (a, b), c = lstsq(
            vstack([x, ones(len(x))]).T,
            y,
            rcond=None,
        )[:2]
        comment = f"A = {a}\nB = {b}\nC = {c}\nChi^2 = {c[0] / len(x)}\n"
        size, strain = self.size_strain(name, b_instr)
        comment += f"\nSize = {size}\nStrain = {strain}\n"
        comment += f"debug chi2: {c[0] - ((a * x + b - y) ** 2).sum()}"
        comment += f"\nDEBUG: instr. broadening coefs: {b_instr}\n"
        lin_x = array([0.0, x.max()])
        lin_y = lin_x * a + b
        millers = ["(%d %d %d)" % tuple(i) for i in self.miller_indices[name]]
        bi_x = linspace(0, x.max(), 100)
        bi_y = self.b_instr(bi_x, b_instr) * sqrt(1.0 - bi_x**2)
        return {
            "plots": [
                {"x1": x, "y1": y, "type": "+", "annotations": millers},
                {"x1": x, "y1": y_t, "type": "o"},
                {"x1": bi_x, "y1": bi_y, "type": "--", "color": "blue"},
                {"x1": lin_x, "y1": lin_y, "type": "-", "color": "green"},
            ],
            "Comment": comment,
        }, b_instr

    def _as_text(self, name):
        b_instr = self._instr_broad
        out = f"\n## Name: {name} ##\n"
        if isinstance(b_instr, list):
            size, strain, b_instr, cor = self._params_to_display(name, b_instr)
            out += (
                f"Predefined instrumental broadening: {b_instr}\n"
                f"size = {size}\nstrain = {strain}\ncorr = {cor}\n"
            )
        size, strain, b_instr, cor = self._params_to_display(name, "cor")
        out += (
            f"\nInstrumental broadening, optimized by correlation: {b_instr}\n"
            f"size = {size}\nstrain = {strain}\ncorr = {cor}\n"
        )
        size, strain, b_instr, cor = self._params_to_display(name, "size")
        out += (
            f"\nInstrumental broadening, optimized by size: {b_instr}\n"
            f"size = {size}\nstrain = {strain}\ncorr = {cor}\n"
        )

        return out

    def to_text(self):
        return f"Shape: {self.shape}\n" + "\n".join(
            self._as_text(name) for name in self.selected
        )

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
            if not any(self.selected[name]):
                continue
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
