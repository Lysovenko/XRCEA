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

from numpy import array, average as aver
from numpy.linalg import solve


def get_dhkl(ipd, inds):
    dinds = array([[d] + inds[i] for i, d in enumerate(ipd) if i in inds])
    return dinds.transpose()


def calc_orhomb(ipd, inds):
    """Orthorhombic"""
    d, h, k, el = get_dhkl(ipd, inds)
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
    return a, b, c, None, None, None


def calc_hex(ipd, inds):
    d, h, k, el = get_dhkl(ipd, inds)
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
    return a, None, c, None, None, 120.


def calc_tetra(ipd, inds):
    d, h, k, el = get_dhkl(ipd, inds)
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
    return a, None, c, None, None, None


def calc_cubic(ipd, inds):
    d, h, k, el = get_dhkl(ipd, inds)
    y = d ** -2
    bm = h ** 2 + k ** 2 + el ** 2
    ym = aver(y * bm)
    m2 = aver(bm ** 2)
    ba = ym / m2
    a = ba ** -.5
    return a, None, None, None, None, None


CALCULATORS = {"hex": calc_hex, "tetra": calc_tetra,
               "cubic": calc_cubic, "orhomb": calc_orhomb}
