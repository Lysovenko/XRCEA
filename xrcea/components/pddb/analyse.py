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
"""
Put the pattern over the diffractogram
"""
from numpy import interp


def mul_plot(xrd, pddb, card):
    """
    Multiply scattering by pattern
    """
    units = xrd.x_units
    xmin = xrd.x_data.min()
    xmax = xrd.x_data.max()
    scattering = xrd.extra_data["stripped"]
    wavis = [(wavel, intens) for wavel, intens in (
        (xrd.lambda1, 1.), (xrd.lambda2, xrd.I2), (xrd.lambda3, xrd.I3))
        if wavel is not None and intens is not None]
    wavels = tuple(i[0] for i in wavis)
    dis = pddb.get_di(card, units, wavels, (xmin, xmax))
    ssum = 0.
    psum = 0.
    for (x, y), (w, i) in zip(dis, wavis):
        ys = interp(x, xrd.x_data, scattering, 0., 0.)
        ssum += (ys * y * i).sum()
        psum += ((y * i) ** 2).sum()
    return ssum / psum
