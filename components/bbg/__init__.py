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
Bragg-Brentano geometry
"""

from core.application import APPLICATION as APP
from core.idata import XrayData
from numpy import arcsin, sin, polyval
from scipy.optimize import fmin
from locale import format_string


def introduce():
    """Entry point. Declares menu items."""
    cryp = APP.runtime_data.setdefault("cryp", {})
    extra = cryp.setdefault("extra_calcs", [])
    extra.append((_("Fix angle"), fix_angle))


def terminate():
    """"""


def fix_angle(xrd, vis):
    """ """
    indset = xrd.extra_data.get("UserIndexes")
    res = {}
    calculs = APP.runtime_data.get("cryp", {}).get("cell_calc", {})
    for name in indset:
        inds = indset[name]["indices"]
        try:
            calc = calculs[indset[name]["cell"]]
            callb = ModAngle(xrd, calc, inds)
            no_fix = callb([1., 0.])
            if no_fix is None:
                continue
            xopt = fmin(callb, [0., 0., 1., 0.], initial_simplex=[
                [0.01, 0., 1., 0.],
                [0., 0.01, 1., 0.],
                [0., 0., 1.01, 0.],
                [0., 0., 1., 0.01],
                [-0.01, -0.01, .99, -0.01]])
            res[name] = "%s <b>%g => %g</b>" % (callb.to_markup(xopt),
                                                no_fix, callb(xopt))
        except KeyError:
            print(f"TODO: calculator for {indset[name]['cell']}")
            pass
    vis.set_text("<html><body>%s</body></html>" %
                 "<br/>".join("%s: %s" % i for i in res.items()))


class ModAngle:
    def __init__(self, xrd, calc, inds):
        cryb = xrd.extra_data.get("crypbells")
        hwave = xrd.lambda1 / 2.
        ipd = sorted(hwave / cryb.reshape(len(cryb) // 4, 4)[:, 0],
                     reverse=True)
        self.calc = calc
        self.hwave = hwave
        self.crybp = cryb.reshape(len(cryb) // 4, 4)[:, 0]
        self.inds = inds

    def __call__(self, corvec):
        crybp = sin(polyval(corvec, arcsin(self.crybp)))
        ipd = sorted(self.hwave / crybp, reverse=True)
        return self.calc(ipd, self.inds)[6]

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
