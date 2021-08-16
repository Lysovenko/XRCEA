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
Sample's plane correction
"""

from xrcea.core.application import APPLICATION as APP
from numpy import sqrt, array
from scipy.optimize import fmin
from locale import format_string


def detect_plane_shift(xrd, vis):
    """Detect plane's shift"""
    aps = APP.settings
    params = vis.input_dialog(
        _("Initial simplex params"),
        [(_("Initial shift:"), aps.get("ini_shift", 1e-3, "BBG"))])
    if params is None:
        return
    ishift, = params
    aps.set("ini_shift", ishift, "BBG")
    simplex = array([[0.], [ishift]])
    indset = xrd.extra_data.get("UserIndexes")
    res = {}
    calculs = APP.runtime_data.get("cryp", {}).get("cell_calc", {})
    for name in indset:
        inds = indset[name]["indices"]
        try:
            calc = calculs[indset[name]["cell"]]
            callb = ShiftPlane(xrd, calc, inds)
            no_fix = callb([0.])
            if no_fix is None:
                continue
            xopt = fmin(callb, simplex[0], initial_simplex=simplex)
            res[name] = ("%s <b>%g => %g</b>"
                         "<div>%s</div><div>%s</div>") % (
                callb.to_markup(xopt), no_fix, callb(xopt),
                callb.mark_params([0]), callb.mark_params(xopt))
        except KeyError:
            print(f"TODO: calculator for {indset[name]['cell']}")
            pass
    vis.set_text("<html><body>%s</body></html>" %
                 "<br/>".join("%s: %s" % i for i in res.items()))


class ShiftPlane:
    def __init__(self, xrd, calc, inds):
        cryb = xrd.extra_data.get("crypbells")
        hwave = xrd.lambda1 / 2.
        ipd = sorted(hwave / cryb.reshape(len(cryb) // 4, 4)[:, 0],
                     reverse=True)
        self.calc = calc
        self.hwave = hwave
        self.crybp = cryb.reshape(len(cryb) // 4, 4)[:, 0]
        self.inds = inds

    def __call__(self, corvec, full=False):
        h = corvec[0]
        crybp = self.crybp / sqrt(
            1. - 2. * h * sqrt(1 - self.crybp ** 2) + h ** 2)
        ipd = sorted(self.hwave / crybp, reverse=True)
        inds = self.inds
        dinds = array([[d] + inds[i] for i, d in enumerate(ipd) if i in inds])
        res = self.calc(dinds.transpose())
        if full:
            return res
        return res[6]

    def to_markup(self, corvec):
        """Convert correction vector to text"""
        m, = corvec
        if m < 0.:
            sign = "-"
        else:
            sign = ""
        sr = ("%g" % abs(m)).split("e")
        if len(sr) == 2:
            sr[1] = "\u00b710<sup>%d</sup>" % int(sr[1])
        sr[0] = format_string("%g", float(sr[0]))
        sr.insert(0, sign)
        return "".join(sr)

    def mark_params(self, corvec):
        res = self(corvec, True)
        pnr = ["a", "b", "c", "\u03b1", "\u03b2", "\u03b3",
               "\u03c7<sup>2</sup>",
               "\u03c3<sup>2</sup><sub>a</sub>",
               "\u03c3<sup>2</sup><sub>b</sub>",
               "\u03c3<sup>2</sup><sub>c</sub>",
               "\u03c3<sup>2</sup><sub>\u03b1</sub>",
               "\u03c3<sup>2</sup><sub>\u03b2</sub>",
               "\u03c3<sup>2</sup><sub>\u03b3</sub>"]
        return "; ".join("%s= %s" % (n, format_string("%g", v))
                         for n, v in zip(pnr, res) if v is not None)
