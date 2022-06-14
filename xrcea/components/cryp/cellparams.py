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
"""Calculate cell params"""

from numpy import (
    array, average as aver, arccos, sqrt, sin, cos, tan, zeros, var, unique,
    newaxis, logical_and)
from numpy.linalg import solve
from scipy.optimize import fmin
from itertools import product


def get_dhkl(ipd, inds):
    dinds = array([[d] + inds[i] for i, d in enumerate(ipd) if i in inds])
    return dinds.transpose()


def calc_orhomb(dhkl):
    """
    Orthorhombic

    Quadratic form:
    1 / d^2 = h^2 / a^2 + k^2 / b^2 + l^2 / c^2
    """
    d, h, k, el = dhkl
    y = d ** -2
    bl = el ** 2
    bk = k ** 2
    bh = h ** 2
    yh = aver(bh * y)
    yk = aver(bk * y)
    yl = aver(bl * y)
    h2 = aver(bh ** 2)
    k2 = aver(bk ** 2)
    l2 = aver(bl ** 2)
    hk = aver(bh * bk)
    hl = aver(bh * bl)
    kl = aver(bk * bl)
    matrA = array([[h2, hk, hl], [hk, k2, kl], [hl, kl, l2]])
    colB = array([yh, yk, yl])
    ba, bb, bc = solve(matrA, colB)
    a = ba ** -.5
    b = bb ** -.5
    c = bc ** -.5
    chi2 = ba ** 2 * h2 + 2 * ba * bb * hk + 2 * ba * bc * hl - \
        2 * ba * yh + bb ** 2 * k2 + 2 * bb * bc * kl - 2 * bb * yk + \
        bc ** 2 * l2 - 2 * bc * yl + aver(y ** 2)
    return (a, b, c, None, None, None,
            chi2, None, None, None, None, None, None)


def calc_hex(dhkl):
    """
    Hexagonal

    Quadratic form:
    1 / d^2 = 4/3 (h^2 + hk + k^2) / a^2 + l^2 / c^2
    """
    d, h, k, el = dhkl
    y = d ** -2
    bl = el ** 2
    bm = h ** 2 + h * k + k ** 2
    yl = aver(y * bl)
    ym = aver(y * bm)
    lm = aver(bl * bm)
    m2 = aver(bm ** 2)
    l2 = aver(bl ** 2)
    matrA = array([[lm, l2], [m2, lm]])
    colB = array([yl, ym])
    ba, bb = solve(matrA, colB)
    a = (4. / 3. / ba) ** .5
    c = bb ** -.5
    y2 = aver(y ** 2)
    chi2 = ba ** 2 * m2 + 2. * ba * bb * lm - 2. * ba * ym + \
        bb ** 2 * l2 - 2. * bb * yl + y2
    delta = m2 * l2 - lm ** 2
    sig2a = l2 / delta * chi2
    sig2b = m2 / delta * chi2
    sig2a /= 3 * ba ** 3
    sig2b /= 4 * bb ** 3
    return (a, None, c, None, None, 120.,
            chi2, sig2a, None, sig2b, None, None, None)


def calc_tetra(dhkl):
    """
    Tetrahonal

    Quadratic form:
    1 / d^2 = (h^2 + k^2) / a^2 + l^2 / c^2
    """
    d, h, k, el = dhkl
    y = d ** -2
    bl = el ** 2
    bm = h ** 2 + k ** 2
    yl = aver(y * bl)
    ym = aver(y * bm)
    lm = aver(bl * bm)
    m2 = aver(bm ** 2)
    l2 = aver(bl ** 2)
    matrA = array([[lm, l2], [m2, lm]])
    colB = array([yl, ym])
    ba, bb = solve(matrA, colB)
    a = ba ** -.5
    c = bb ** -.5
    chi2 = ba ** 2 * m2 + 2 * ba * bb * lm - 2 * ba * ym + bb ** 2 * l2 - \
        2 * bb * yl + aver(y ** 2)
    return (a, None, c, None, None, None,
            chi2, None, None, None, None, None, None)


def calc_cubic(dhkl):
    """
    Cubic

    Quadratic form:
    1 / d^2 = (h^2 + k^2 + l^2) / a^2
    """
    d, h, k, el = dhkl
    y = d ** -2
    bm = h ** 2 + k ** 2 + el ** 2
    ym = aver(y * bm)
    m2 = aver(bm ** 2)
    ba = ym / m2
    a = ba ** -.5
    chi2 = ba ** 2 * m2 - 2 * ba * ym + aver(y ** 2)
    return (a, None, None, None, None, None,
            chi2, None, None, None, None, None, None)


def calc_monoclinic(dhkl):
    """
    Monoclinic

    Quadratic form:
    1/d^2 = h^2 / (a^2 sin^2 beta) + k^2 / b^2 +
    + l^2 / (c^2 sin(beta)^2) - 2 h l cos(beta) / (a c sin(beta)^2)
    """
    d, h, k, el = dhkl
    y = d ** -2
    bh = h ** 2
    bk = k ** 2
    bl = el ** 2
    bm = h * el
    h2 = aver(bh ** 2)
    hk = aver(bh * bk)
    hl = aver(bh * bl)
    hm = aver(bh * bm)
    k2 = aver(bk ** 2)
    kl = aver(bk * bl)
    km = aver(bk * bm)
    l2 = aver(bl ** 2)
    lm = aver(bl * bm)
    m2 = aver(bm ** 2)
    yh = aver(y * bh)
    yk = aver(y * bk)
    yl = aver(y * bl)
    ym = aver(y * bm)
    matrA = array([[h2, hk, hl, -hm],
                   [hk, k2, kl, -km],
                   [hl, kl, l2, -lm],
                   [hm, km, lm, -m2]])
    colB = array([yh, yk, yl, ym])
    ba, bb, bc, bd = solve(matrA, colB)
    b = sqrt(1 / bb)
    c = 2 * sqrt(ba / (4 * ba * bc - bd ** 2))
    a = bc * sqrt(1 / ba / bc) * c
    bet = arccos(bd / sqrt(ba * bc) / 2)
    chi2 = ba ** 2 * h2 + 2 * ba * bb * hk + 2 * ba * bc * hl - \
        2 * ba * bd * hm - 2 * ba * yh + \
        bb ** 2 * k2 + 2 * bb * bc * kl - 2 * bb * bd * km - \
        2 * bb * yk + \
        bc ** 2 * l2 - 2 * bc * bd * lm - 2 * bc * yl + \
        bd ** 2 * m2 + 2 * bd * ym + aver(y ** 2)
    return (a, b, c, None, bet, None,
            chi2, None, None, None, None, None, None)


def calc_rhombohedral(dhkl):
    """
    Rhombohedral

    Quadratic form:
1/d^2 = {(1+cos alpha)((h^2+k^2+l^2)-
    (1-tan^2(alpha/2))(hk+kl+lh))}/
    {a^2(1+cos alpha - 2 cos^2 alpha)}
    """
    d, h, k, el = dhkl
    y = d ** -2
    bl = h**2 + k**2 + el**2
    bm = h * k + k * el + el * h
    yl = aver(y * bl)
    ym = aver(y * bm)
    lm = aver(bl * bm)
    m2 = aver(bm ** 2)
    l2 = aver(bl ** 2)
    matrA = array([[l2, lm], [lm, m2]])
    colB = array([yl, ym])
    ba, bb = solve(matrA, colB)
    a = sqrt((2 * ba + bb) / ((ba + bb) * (2 * ba - bb)))
    alp = arccos(-bb / (2 * ba + bb))
    chi2 = ba ** 2 * l2 + 2 * ba * bb * lm - 2 * ba * yl + \
        bb ** 2 * m2 - 2 * bb * ym + aver(y ** 2)
    return (a, None, None, alp, None, None,
            chi2, None, None, None, None, None, None)


CALCULATORS = {"hex": calc_hex, "tetra": calc_tetra,
               "cubic": calc_cubic, "orhomb": calc_orhomb,
               "monoclinic": calc_monoclinic,
               "rhombohedral": calc_rhombohedral}


def d_hkl_orhomb(a, b, c, hkl):
    """Calculate d_hkl for Orthorhombic unit cell"""
    h, k, el = hkl
    d2 = 1. / a ** 2 * h ** 2 + 1. / b ** 2 * k ** 2 + \
        1. / c ** 2 * el ** 2
    return sqrt(1. / d2)


def d_hkl_hex(a, c, hkl):
    """Calculate d_hkl for Hexagonal unit cell"""
    h, k, el = hkl
    d2 = 4. / 3. / a ** 2 * (h ** 2 + h * k + k ** 2)\
        + 1. / c ** 2 * el ** 2
    return sqrt(1. / d2)


def d_hkl_tetra(a, c, hkl):
    """Calculate d_hkl for Tetrahonal unit cell"""
    h, k, el = hkl
    d2 = 1. / a ** 2 * (h ** 2 + k ** 2) + 1. / c ** 2 * el ** 2
    return sqrt(1. / d2)


def d_hkl_cubic(a, hkl):
    """Calculate d_hkl for Cubic unit cell"""
    h, k, el = hkl
    d2 = 1. / a ** 2 * (h ** 2 + k ** 2 + el ** 2)
    return sqrt(1. / d2)


def d_hkl_rhombohedral(a, alp, hkl):
    """Calculate d_hkl for Rhombohedral unit cell"""
    h, k, el = hkl
    d2 = 1. / a ** 2. * (1. + cos(alp)) * \
        ((h ** 2 + k ** 2 + el ** 2) - (
            1. - tan(alp / 2.) ** 2) * (
                h * k + k * el + el * h)) / \
        (1. + cos(alp) - 2. * cos(alp) ** 2)
    return sqrt(1. / d2)


def d_hkl_monoclinic(a, b, c, bet, hkl):
    """Calculate d_hkl for Monoclinic unit cell"""
    h, k, el = hkl
    d2 = 1. / a ** 2. * (h ** 2 / sin(bet) ** 2) + \
        1. / b ** 2 * k ** 2 + 1 / c ** 2 * el ** 2 \
        / (sin(bet) ** 2) - 2 * h * el / \
        (a * c * sin(bet) * tan(bet))
    return sqrt(1. / d2)


def chi2n(d1a, d2a, poss):
    dev = array([((d2a**-2 - i)**2).min() for i in d1a**-2])
    inds = [((d2a**2 - i)**2).argmin() for i in d1a**2]
    iset = unique(inds)
    ave = aver(poss.transpose()[inds])
    return aver(dev) * var(dev)**2 * ((len(d1a) - len(iset))**2 + 1) * ave**2


class FitIndices:
    def __init__(self, crystal_system, max_ind):
        self._cs = getattr(self, crystal_system)
        hkl = array(
            list(product(*((tuple(range(max_ind + 1)),) * 3)))[1:]).transpose()
        if crystal_system in ("cubic", "rhombohedral"):
            self._hkl = hkl[:, logical_and(hkl[0] >= hkl[1], hkl[1] >= hkl[2])]
        elif crystal_system in ("hex", "tetra"):
            self._hkl = hkl[:, hkl[0] >= hkl[1]]
        else:
            self._hkl = hkl

    def __call__(self, *args, **dargs):
        return self._cs(*args, **dargs)

    def dhkl(self, dres, dlist):
        near_indices = ((dlist[:, newaxis] - dres)**2).argmin(1)
        _dhkl = zeros((4, len(dlist)))
        _dhkl[0, :] = dlist
        _dhkl[1:, :] = self._hkl.transpose()[near_indices].transpose()
        return _dhkl

    def hex(self, dlist, iniparams):
        poss_hkl = self._hkl

        def vec(abc):
            dfit = d_hkl_hex(*abc, poss_hkl)
            return chi2n(dlist, dfit, poss_hkl)

        opt = fmin(vec, [iniparams[0], iniparams[2]], disp=0)
        dres = d_hkl_hex(*opt, poss_hkl)
        dhkl = self.dhkl(dres, dlist)
        return calc_hex(dhkl), dhkl[1:]

    def tetra(self, dlist, iniparams):
        poss_hkl = self._hkl

        def vec(abc):
            dfit = d_hkl_tetra(*abc, poss_hkl)
            return chi2n(dlist, dfit, poss_hkl)

        opt = fmin(vec, [iniparams[0], iniparams[2]], disp=0)
        dres = d_hkl_tetra(*opt, poss_hkl)
        dhkl = self.dhkl(dres, dlist)
        return calc_tetra(dhkl), dhkl[1:]

    def cubic(self, dlist, iniparams):
        poss_hkl = self._hkl

        def vec(abc):
            dfit = d_hkl_cubic(*abc, poss_hkl)
            return chi2n(dlist, dfit, poss_hkl)

        opt = fmin(vec, [iniparams[0]], disp=0)
        dres = d_hkl_cubic(*opt, poss_hkl)
        dhkl = self.dhkl(dres, dlist)
        return calc_cubic(dhkl), dhkl[1:]

    def orhomb(self, dlist, iniparams):
        poss_hkl = self._hkl

        def vec(abc):
            dfit = d_hkl_orhomb(*abc, poss_hkl)
            return chi2n(dlist, dfit, poss_hkl)

        opt = fmin(vec, [iniparams[0], iniparams[1], iniparams[2]], disp=0)
        dres = d_hkl_orhomb(*opt, poss_hkl)
        dhkl = self.dhkl(dres, dlist)
        return calc_orhomb(dhkl), dhkl[1:]

    def monoclinic(self, dlist, iniparams):
        poss_hkl = self._hkl

        def vec(abc):
            dfit = d_hkl_monoclinic(*abc, poss_hkl)
            return chi2n(dlist, dfit, poss_hkl)

        opt = fmin(vec, [iniparams[0], iniparams[1], iniparams[2],
                         deg2rad(iniparams[4])], disp=0)
        dres = d_hkl_monoclinic(*opt, poss_hkl)
        dhkl = self.dhkl(dres, dlist)
        return calc_monoclinic(dhkl), dhkl[1:]

    def rhombohedral(self, dlist, iniparams):
        poss_hkl = self._hkl

        def vec(abc):
            dfit = d_hkl_rhombohedral(*abc, poss_hkl)
            return chi2n(dlist, dfit, poss_hkl)

        opt = fmin(vec, [iniparams[0], deg2rad(iniparams[3])], disp=0)
        dres = d_hkl_rhombohedral(*opt, poss_hkl)
        dhkl = self.dhkl(dres, dlist)
        return calc_rhombohedral(dhkl), dhkl[1:]
