# XRCEA (C) 2025 Serhii Lysovenko
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
"""Make structural assumptions"""

from json import loads, dumps, JSONDecodeError
from itertools import product
import numpy as np
from xrcea.core.vi import Page
from .cellparams import (
    d_hkl_orhomb,
    d_hkl_hex,
    d_hkl_tetra,
    d_hkl_cubic,
    d_hkl_rhombohedral,
    d_hkl_monoclinic,
)

_assumption = _("Assumption")


class StructAssume(Page):
    """Calculator"""

    def __init__(self, xrd):
        self._xrd = xrd
        self._calculs = {
            "orhomb": self.di_orhomb,
            "hex": self.di_hex,
            "tetra": self.di_tetra,
            "cubic": self.di_cubic,
            "rhombohedral": self.di_rhombohedral,
            "monoclinic": self.di_monoclinic,
        }
        self._milgens = {
            "orhomb": self.mills,
            "hex": self.mills_hk,
            "tetra": self.mills_hk,
            "cubic": self.mills_hkl,
            "rhombohedral": self.mills,
            "monoclinic": self.mills,
        }
        self._extinctions = {
            "P": self.condition_p,
            "I": self.condition_i,
            "A": self.condition_a,
            "B": self.condition_b,
            "C": self.condition_c,
            "F": self.condition_f,
        }
        super().__init__(str(xrd.name) + _(" (Assumptions)"), None)
        self.menu.append_item(
            (_assumption,), _("Plot") + "\tCtrl+P", self.calc_plot, None
        )
        self.add_shortcut("Ctrl+p", self.calc_plot)
        self.show()
        self.set_text(
            dumps(
                self._xrd.extra_data.setdefault(
                    "Assumptions", [{"t": "cubic", "a": 1}]
                ),
                indent=4,
            ),
            True,
        )

    def calc_plot(self):
        xrd = self._xrd
        try:
            plot = xrd.UIs["main"]
        except KeyError:
            return
        text = self.get_text()
        try:
            assobj = loads(text)
        except JSONDecodeError:
            print("Assumption parsing error")
            return
        if isinstance(assobj, dict):
            assobj = [assobj]
        elif not isinstance(assobj, list):
            print("Wrong request")
            return
        self._xrd.extra_data["Assumptions"] = assobj
        x_label = {
            "theta": "$\\theta$",
            "2theta": "$2\\theta$",
            "q": "q",
            None: _("Unknown"),
        }[xrd.x_units]
        plt = {
            "plots": [
                {"x1": xrd.x_data, "y1": xrd.y_data, "color": "exp_dat"},
            ],
            "x1label": x_label,
            "y1label": _("Relative units"),
            "x1units": xrd.x_units,
        }
        xmin = xrd.x_data.min()
        xmax = xrd.x_data.max()
        units = xrd.x_units
        wavis = [
            (wavel, intens)
            for wavel, intens in (
                (xrd.lambda1, 1.0),
                (xrd.lambda2, xrd.I2),
                (xrd.lambda3, xrd.I3),
            )
            if wavel is not None and intens is not None
        ]
        wavels = tuple(i[0] for i in wavis)
        for rec in assobj:
            dis = self.plt_di(rec, units, wavels, (xmin, xmax))
            if dis is None:
                continue
            dis, mils = dis
            annotations = ["(%d%3d%3d)" % i for i in mils]
            for (x, y), lstl, (w, i) in zip(
                dis, ("solid", "dashed", "dashdot"), wavis
            ):
                eplt = {
                    "type": "pulse",
                    "linestyle": lstl,
                    "color": rec.get("clr", "red"),
                }
                if lstl == "solid":
                    eplt["legend"] = rec.get("t", "nothing")
                eplt["x1"] = x
                eplt["y2"] = y * i
                if annotations:
                    eplt["annotations"] = annotations
                    annotations = None
                plt["plots"].append(eplt)
        plot_name = _("Assumed")
        plot.add_plot(plot_name, plt)
        plot.draw(plot_name)

    def plt_di(self, rec, xtype="q", wavel=(), between=None):
        try:
            reflexes = self.calc_reflexes(rec)
        except KeyError:
            return
        if not reflexes:
            return
        mils = [i[2] for i in reflexes]
        dis = np.array([i[:2] for i in reflexes], "f").transpose()
        intens = dis[1]
        if not isinstance(wavel, (tuple, list)):
            wavel = (wavel,)
            single = True
        else:
            single = False
        abscisas = []
        restore = np.seterr(invalid="ignore")
        for wave in wavel:
            if xtype == "sin(theta)":
                abscisas.append(wave / 2.0 / dis[0])
            elif xtype == "theta":
                abscisas.append(np.arcsin(wave / 2.0 / dis[0]) / np.pi * 180.0)
            elif xtype == "2theta":
                abscisas.append(np.arcsin(wave / 2.0 / dis[0]) / np.pi * 360.0)
        if xtype == "q":
            abscisas.append((2.0 * np.pi) / dis[0])
        elif not abscisas:
            abscisas.append(dis[0])
        milshrink = True
        if between:
            res = []
            for x in abscisas:
                b = x >= min(between)
                b &= x <= max(between)
                res.append((x[b], intens[b]))
                if milshrink:
                    milshrink = False
                    mils = [j for i, j in enumerate(mils) if b[i]]
        else:
            res = [(x, intens) for x in abscisas]
        np.seterr(**restore)
        if single:
            return res[0], mils
        return res, mils

    def calc_reflexes(self, record):
        mills = self._milgens[record["t"]](record.get("max", 4))
        if "ext" in record:
            mills = filter(self._extinctions.get(record["ext"]), mills)
            mills = list(mills)
        return sorted(self._calculs[record["t"]](record, mills))

    @staticmethod
    def mills_hkl(max):
        for h in range(1, max + 1):
            for k in range(h + 1):
                for el in range(k + 1):
                    yield (h, k, el)

    @staticmethod
    def mills_hk(max):
        for h in range(max + 1):
            for k in range(h + 1):
                for el in range(0 if h else 1, max + 1):
                    yield (h, k, el)

    @staticmethod
    def mills(max):
        itr = product(*((tuple(range(max + 1)),) * 3))
        next(itr)
        for i in itr:
            yield i

    @staticmethod
    def condition_p(hkl):
        return True

    @staticmethod
    def condition_i(hkl):
        return sum(hkl) % 2 == 0

    @staticmethod
    def condition_a(hkl):
        return (hkl[1] + hkl[2]) % 2 == 0

    @staticmethod
    def condition_b(hkl):
        return (hkl[0] + hkl[2]) % 2 == 0

    @staticmethod
    def condition_c(hkl):
        return (hkl[1] + hkl[0]) % 2 == 0

    @staticmethod
    def condition_f(hkl):
        return (hkl[0] % 2) == (hkl[1] % 2) == (hkl[2] % 2)

    @staticmethod
    def di_orhomb(rec, mills):
        a = rec["a"]
        b = rec["b"]
        c = rec["c"]
        return [(d_hkl_orhomb(a, b, c, hkl), 100, hkl) for hkl in mills]

    @staticmethod
    def di_hex(rec, mills):
        a = rec["a"]
        c = rec["c"]
        return [(d_hkl_hex(a, c, hkl), 100, hkl) for hkl in mills]

    @staticmethod
    def di_tetra(rec, mills):
        a = rec["a"]
        c = rec["c"]
        return [(d_hkl_tetra(a, c, hkl), 100, hkl) for hkl in mills]

    @staticmethod
    def di_cubic(rec, mills):
        a = rec["a"]
        return [(d_hkl_cubic(a, hkl), 100, hkl) for hkl in mills]

    @staticmethod
    def di_rhombohedral(rec, mills):
        a = rec["a"]
        alp = rec["alp"]
        return [(d_hkl_rhombohedral(a, alp, hkl), 100, hkl) for hkl in mills]

    @staticmethod
    def di_monoclinic(rec, mills):
        a = rec["a"]
        b = rec["b"]
        c = rec["c"]
        bet = rec["bet"]
        return [
            (d_hkl_monoclinic(a, b, c, bet, hkl), 100, hkl) for hkl in mills
        ]


def show_struct_assumptions(xrd):
    p = xrd.UIs.get("Assumptions")
    if p:
        p.show()
        return
    xrd.UIs["Assumptions"] = StructAssume(xrd)
