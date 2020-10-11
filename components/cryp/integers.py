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
"""Find integers in sin^2 correlations"""
from numpy import min, ceil, floor, pi, arcsin, sin, ndarray, max
from scipy.optimize import minimize, Bounds


def theta_correction(delta: ndarray, x_: ndarray, this: ndarray,
                     p: int, m: int):
    y = sin(arcsin(x_) + delta)
    y = y / y[p] * m
    return max(min([y - floor(y), ceil(y) - y], axis=0)[this])


def find_integers(cryb):
    sin2x = cryb.reshape(len(cryb) // 4, 4)[:, 0] ** 2
    bounds = Bounds(-pi / 2., pi / 2.)
    for i in range(len(sin2x)):
        for j in range(1, 6):
            y = sin2x / sin2x[i] * j
            found = min([y - floor(y), ceil(y) - y], axis=0) < .09
            print(i, j, y[found], theta_correction([0], sin2x, found, i, j))
            x = ndarray(1)
            x[0] = 0.
            print(minimize(theta_correction, x, (sin2x, found, i, j),
                           'Powell', bounds))


if __name__ == "__main__":
    from numpy import frombuffer, zeros
    from base64 import b64decode
    x = frombuffer(b64decode(
        "5shDxKGE0z/0PuUcDlLRP7xlqNnAGNo/LeE06kpQ4T9VZPfs9+bgP1P+dlSs5uM/"
        "kGbvLWSJ4z93i4n09QLjP/wZKisxYOU/GBY1NAs66D/gwQIOoibqP6B4akjV5ek/"
        "KAo+DOnk6T8SzWnwQFbrPw=="))
    example = zeros(len(x) * 4)
    example.reshape(len(x), 4)[:, 0] = x
    print(find_integers(example))
