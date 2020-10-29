# XRCEA (C) 2020 Serhii Lysovenko
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
"""

import numpy as np
from scipy.optimize import fmin, curve_fit

_SH_FUNCTIONS = {"Gauss": lambda the_x, x0, h, w:
                 h * np.exp(-(the_x - x0) ** 2 / w),
                 "Lorentz": lambda the_x, x0, h, w:
                 h / (1. + (the_x - x0) ** 2 / w),
                 "Voit": lambda the_x, x0, h, w:
                 h / (1. + (the_x - x0) ** 2 / w) ** 2}


def calc_bg(sig_x, sig_y, deg, bf=3.):
    tbg = np.polyval(np.polyfit(sig_x, sig_y, deg), sig_x)
    sigma2 = ((sig_y - tbg) ** 2).sum() / (len(tbg) - 1. - deg)
    sigma2p = None
    coeffs = None
    while sigma2p != sigma2:
        sigma2p = sigma2
        sigma = sigma2 ** .5 * bf
        pts = zip(sig_x, sig_y, tbg)
        pts = [(a, b) for a, b, c in pts if b - c < sigma]
        pts = np.array(pts).transpose()
        coeffs = np.polyfit(pts[0], pts[1], deg)
        pbg = np.poly1d(coeffs)
        sigma2 = ((pts[1] - pbg(pts[0])) ** 2).sum() / (len(pts[0]) - 1. - deg)
        tbg = pbg(sig_x)
    return tbg, sigma2, coeffs


def refl_sects(s_x, stripped_y, sigma2, bf=3.):
    sigma = sigma2 ** .5 * bf
    sector = []
    prev = []
    for x, y in zip(s_x, stripped_y):
        if y > sigma:
            if prev:
                sector = prev
                prev = []
            sector.append((x, y))
        elif sector:
            sector.append((x, y))
            if y < 0.:
                yield sector
                sector = []
                prev.append((x, y))
        elif prev and prev[-1][1] - y > y or y <= 0.:
            prev = [(x, y)]
        else:
            prev.append((x, y))
    if sector:
        yield sector


class ReflexDedect:
    """treat sector of points positioned above background"""
    def __init__(self, sector, lambda21=None, i2=.5):
        tps = np.array(sector).transpose()
        self.x_ar = tps[0]
        self.y_ar = tps[1]
        if self.y_ar[0] < 0.:
            x1, x2 = self.x_ar[:2]
            y1, y2 = self.y_ar[:2]
            self.y_ar[0] = 0.
            self.x_ar[0] = x1 - y1 * (x2 - x1) / (y2 - y1)
        if self.y_ar[-1] < 0.:
            x1, x2 = self.x_ar[-2:]
            y1, y2 = self.y_ar[-2:]
            self.y_ar[-1] = 0.
            self.x_ar[-1] = x1 - y1 * (x2 - x1) / (y2 - y1)
        self.peaks = None
        self.lambda21 = lambda21
        self.I2 = i2
        self.sigma2 = (tps[1] ** 2).sum() / len(tps[0])
        self.y_max2 = tps[1].max() ** 2

    def calc_deviat(self, x, fixx=False, fixs=None):
        if fixx:
            the_x = np.zeros((len(x) // 2, 3))
            the_x[:, 0] = self.x0
            the_x[:, 1:3] = x.reshape(len(x) // 2, 2)
            x = the_x.flatten()
        elif fixs:
            the_x = np.zeros((len(self.x0), 3))
            nfl = len(self.x0) - len(fixs)
            x0 = x[:nfl].tolist()
            for i in fixs:
                x0.insert(i, self.x0[i])
            the_x[:, 0] = x0
            the_x[:, 1:3] = x[nfl:].reshape(len(self.x0), 2)
            x = the_x.flatten()
        if x.min() <= 0.:
            return np.inf
        shape = self.calc_shape(x)
        dev = self.y_ar - shape
        _x = x.reshape(len(x) // 3, 3)
        return (dev ** 2).sum() / len(self.y_ar) * (np.var(_x[:, 2]) + 1)

    def calc_deviat2(self, x):
        the_x = np.array([self.x0, self.h] + x.tolist())
        shape = self.calc_shape(the_x)
        return ((self.dy_ar - shape) ** 2).sum() / len(self.dy_ar)

    def calc_deviat3(self, x):
        the_x = np.zeros(((len(x) - 1) // 2, 3))
        the_x[:, :2] = x[: -1].reshape(len(the_x), 2)
        if the_x[:, 1].min() <= 0. or the_x[:, 1].max() > self.max_h:
            return np.inf
        the_x[:, 2] = x[-1]
        shape = self.calc_shape(the_x.flatten())
        dev = self.y_ar - shape
        rv = (dev ** 2).sum() / len(self.y_ar) * (np.var(the_x[:, 2]) + 1)
        return rv

    def calc_shape(self, *args):
        if len(args) == 0:
            x = None
        elif len(args) == 1:
            x, = args
        else:
            x = np.array(args[1:])
        the_x = self.x_ar
        shape = np.zeros(len(the_x))
        l21 = self.lambda21
        i2 = self.I2
        sh_func = self.sh_func
        if x is None:
            peaks = self.peaks
            if peaks is None:
                return shape
        else:
            peaks = x.reshape(len(x) // 3, 3)
        if l21 is None:
            for x0, h, w in peaks:
                shape += sh_func(the_x, x0, h, w)
        else:
            for x0, h, w in peaks:
                shape += sh_func(the_x, x0, h, w)
                shape += sh_func(the_x, x0 * l21, h * i2, w * l21 ** 2)
        return shape

    def curve_fit(self, opt_args, x_ar, y_ar):
        popt, pcov = curve_fit(self.calc_shape, x_ar, y_ar, p0=opt_args)
        print(popt, pcov)
        return popt, ((self.calc_shape(popt) - y_ar) ** 2).sum() / len(y_ar)

    def find_bells(self, sigmin, varsig, max_peaks=None, sh_type="Gauss"):
        """my new not so good algorithm"""
        self.sh_type = sh_type
        self.sh_func = _SH_FUNCTIONS[sh_type]
        wmin = 2. * sigmin ** 2
        y_ar = self.y_ar
        x_ar = self.x_ar
        area = np.trapz(y_ar, x_ar)
        hght = y_ar.max()
        if self.lambda21:
            area /= 1. + self.I2
            hght /= 1. + self.I2
        self.max_h = hght
        mp = (len(x_ar)) // 4
        if max_peaks is None or max_peaks <= 0 or max_peaks > mp:
            max_peaks = mp
        sigma2 = (y_ar ** 2).sum() / len(y_ar)
        self.peaks = None
        done = 0
        opt_x = np.array([])
        while True:
            prev_opt_x = opt_x
            prev_sigma2 = sigma2
            done += 1
            opt_x = np.zeros(done * 3)
            h = hght / done
            w = ((area / done) / h) ** 2 / np.pi
            opt_x = opt_x.reshape(done, 3)
            opt_x[:, 0] = np.linspace(x_ar[0], x_ar[-1], done + 2)[1: -1]
            opt_x[:, 1] = h
            opt_x[:, 2] = w
            opt_x = opt_x.flatten()
            opt_x, sigma2 = self.curve_fit(opt_x, x_ar, y_ar)
            print(f"previous: {prev_sigma2}; sigma2: {sigma2}")
            if prev_sigma2 < sigma2 * (done + 1) / done:
                if done > 1:
                    opt_x = prev_opt_x
                    done -= 1
                break
            if done == max_peaks:
                break
        bls = opt_x
        sig2 = 0.
        self.peaks = zip(*bls.reshape(done, 3).transpose())
        return self.peaks, np.sqrt(sig2)

    def find_bells_pp(self, sh_type, poss, fposs):
        self.peaks = None
        nbells = len(poss)
        self.sh_type = sh_type
        self.sh_func = _SH_FUNCTIONS[sh_type]
        if nbells == 0:
            return [], 0.
        y_ar = self.y_ar
        x_ar = self.x_ar
        area = np.trapz(y_ar, x_ar)
        hght = y_ar.max()
        if self.lambda21:
            area /= 1. + self.I2
            hght /= 1. + self.I2
        h = hght / nbells
        w = ((area / nbells) / h) ** 2 / np.pi
        opt_x = np.zeros((nbells, 2))
        opt_x[:, 0] = h
        opt_x[:, 1] = w
        self.x0 = np.array(poss)
        opt_x = opt_x.flatten()
        opt_x, sig2 = fmin(self.calc_deviat, opt_x, args=(True,),
                           full_output=True, disp=False)[:2]
        fx = np.zeros((nbells, 3))
        if fposs:
            flx = [self.x0[i] for i in range(len(self.x0)) if i not in fposs]
            opt_x = np.array(flx + opt_x.tolist())
            opt_x, sig2 = fmin(self.calc_deviat, opt_x, args=(False, fposs),
                               full_output=True, disp=False)[:2]
            nfx = len(self.x0) - len(fposs)
            x0 = opt_x[:nfx].tolist()
            for i in fposs:
                x0.insert(i, self.x0[i])
            fx[:, 0] = x0
            fx[:, 1:] = opt_x[nfx:].reshape(nbells, 2)
            opt_x = fx.flatten()
        else:
            fx[:, 0] = self.x0
            fx[:, 1:] = opt_x.reshape(nbells, 2)
            opt_x = fx.flatten()
            opt_x, sig2 = fmin(self.calc_deviat, opt_x, full_output=True,
                               disp=False)[:2]
        self.peaks = zip(*opt_x.reshape(nbells, 3).transpose())
        return self.peaks, np.sqrt(sig2)


class Cryplots:
    @staticmethod
    def _calc_shape(xrd, shfunc):
        shape = np.zeros(len(xrd.x_data))
        if xrd.x_units != "q":
            x = np.sin(xrd.theta)
        else:
            x = xrd.qrange
        lambdi = []
        if xrd.lambda2 is not None and xrd.I2 is not None:
            lambdi.append((xrd.lambda2 / xrd.lambda1, xrd.I2))
        if xrd.lambda3 is not None and xrd.I3 is not None:
            lambdi.append((xrd.lambda3 / xrd.lambda1, xrd.I3))
        cryb = xrd.extra_data["crypbells"]
        for x0, h, w, s in cryb.reshape(len(cryb) // 4, 4):
            shape += shfunc(x, x0, h, w)
            for l21, ri in lambdi:
                shape += shfunc(x, x0 * l21, h * ri, w * l21 ** 2)
        return shape

    @classmethod
    def _plot(cls, xrd, fname):
        x_label = {"theta": "$\\theta$", "2theta": "$2\\theta$",
                   "q": "q"}.get(xrd.x_units, _("Unknown"))

        plt = {"x1label": x_label, "y1label": _("Relative units"),
               "x1units": xrd.x_units}
        plots = [{"x1": xrd.x_data, "y1": xrd.extra_data["stripped"],
                  "color": "exp_dat"}]
        cryb = xrd.extra_data["crypbells"]
        shfunc = _SH_FUNCTIONS[fname]
        comment = "x0\th\tw\ts\n"
        for x0, h, w, s in cryb.reshape(len(cryb) // 4, 4):
            comment += f"{x0}\t{h}\t{w}\t{s}\n"
            halfwidth = 3 * np.sqrt(w)
            x = np.linspace(x0 - halfwidth, x0 + halfwidth, 100)
            y = shfunc(x, x0, h, w)
            if xrd.x_units == "theta":
                x = np.arcsin(x) * 180. / np.pi
            elif xrd.x_units == "2theta":
                x = np.arcsin(x) * 360. / np.pi
            plots.append({"x1": x, "y1": y, "color": "crp_refl"})
        plots.append({"x1": xrd.x_data, "y1": cls._calc_shape(xrd, shfunc),
                      "color": "crp_srefl"})
        plt["plots"] = plots
        plt["Comment"] = comment
        return plt

    @classmethod
    def pGauss(cls, xrd):
        return cls._plot(xrd, "Gauss")

    @classmethod
    def pLorentz(cls, xrd):
        return cls._plot(xrd, "Lorentz")

    @classmethod
    def pVoit(cls, xrd):
        return cls._plot(xrd, "Voit")
