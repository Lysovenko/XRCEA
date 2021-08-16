# XRCEA (C) 2021 Serhii Lysovenko
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
Polynomial fitting
"""

from xrcea.core.application import APPLICATION as APP
from numpy import arcsin, sin, polyval, zeros, sqrt, array, pi
from scipy.optimize import fmin
from locale import format_string


def detect_polynome(xrd, vis):
    """ """
    aps = APP.settings
    params = vis.input_dialog(
        _("Initial simplex params"),
        [(_("Range:"), aps.get("range", 3, "BBG")),
         (_("Radius:"), aps.get("radius", 1.e-5, "BBG")),
         (_("Mode:"), ("2\u03b8", "sin(\u03b8)"), aps.get("mode", 0, "BBG"))])
    if params is None:
        return
    rng, rad, mode = params
    if rng < 1 or rad < 0.:
        return
    aps.set("range", rng, "BBG")
    aps.set("radius", rad, "BBG")
    aps.set("mode", mode, "BBG")
    simplex = zeros((rng + 2, rng + 1), float)
    simplex[:, -2] = 1.
    simplex[-1] -= rad / sqrt(rng + 1)
    for i in range(rng + 1):
        simplex[i][i] += rad
    indset = xrd.extra_data.get("UserIndexes")
    res = {}
    calculs = APP.runtime_data.get("cryp", {}).get("cell_calc", {})
    for name in indset:
        inds = indset[name]["indices"]
        try:
            calc = calculs[indset[name]["cell"]]
            callb = FitPolynomial(xrd, calc, inds, mode)
            no_fix = callb([1., 0.])
            if no_fix is None:
                continue
            xopt = fmin(callb, simplex[0], initial_simplex=simplex)
            res[name] = ("%s <div><b>%g => %g</b></div>"
                         "<div>%s</div><div>%s</div>") % (
                callb.to_markup(xopt), no_fix, callb(xopt),
                callb.mark_params([1, 0]), callb.mark_params(xopt))
        except KeyError:
            print(f"TODO: calculator for {indset[name]['cell']}")
            pass
    vis.set_text("<html><body>%s</body></html>" %
                 "<br/>".join(
                     "<div><b>%s:</b> %s</div>" % i for i in res.items()))


class FitPolynomial:
    def __init__(self, xrd, calc, inds, way):
        cryb = xrd.extra_data.get("crypbells")
        hwave = xrd.lambda1 / 2.
        ipd = sorted(hwave / cryb.reshape(len(cryb) // 4, 4)[:, 0],
                     reverse=True)
        self.calc = calc
        self.hwave = hwave
        self.crybp = cryb.reshape(len(cryb) // 4, 4)[:, 0]
        self.inds = inds
        self._way = way

    def __call__(self, corvec, full=False):
        if self._way:
            crybp = polyval(corvec, self.crybp)
        else:
            crybp = sin(polyval(corvec, arcsin(self.crybp)))
        ipd = sorted(self.hwave / crybp, reverse=True)
        inds = self.inds
        dinds = array([[d] + inds[i] for i, d in enumerate(ipd) if i in inds])
        res = self.calc(dinds.transpose())
        if full:
            return res
        return res[6]

    def to_markup(self, corvec):
        """Convert correction vector to text"""
        rng = len(corvec)
        parts = []
        for m in corvec:
            rng -= 1
            if not m:
                continue
            if m < 0.:
                sign = "-"
            elif parts:
                sign = "+"
            else:
                sign = ""
            if not self._way:
                m *= (360 / pi) ** (1 - rng)
            sr = ("%g" % abs(m)).split("e")
            if len(sr) == 2:
                sr[1] = "\u00b710<sup>%d</sup>" % int(sr[1])
            sr[0] = format_string("%g", float(sr[0]))
            if rng > 1:
                sr.append(" <i>x</i><sup>%d</sup>" % rng)
            elif rng == 1:
                sr.append(" <i>x</i>")
            if parts:
                parts.append(sign)
            else:
                sr.insert(0, sign)
            parts.append("".join(sr))
        return " ".join(parts)

    def mark_params(self, corvec):
        pnr = ["a", "b", "c", "\u03b1", "\u03b2", "\u03b3",
               "\u03c7<sup>2</sup>",
               "\u03c3<sup>2</sup><sub>a</sub>",
               "\u03c3<sup>2</sup><sub>b</sub>",
               "\u03c3<sup>2</sup><sub>c</sub>",
               "\u03c3<sup>2</sup><sub>\u03b1</sub>",
               "\u03c3<sup>2</sup><sub>\u03b2</sub>",
               "\u03c3<sup>2</sup><sub>\u03b3</sub>"]
        return "; ".join("%s= %s" % (n, format_string("%g", v))
                         for n, v in zip(pnr, self(corvec, True))
                         if v is not None)
