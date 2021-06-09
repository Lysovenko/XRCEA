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
"""Set Miller's indices automatically"""

from itertools import product
from numpy import array
from .cellparams import FitIndices


def find_indices(locations, ini_p, cs, max_index, min_peaks, max_results,
                 result):
    """Wrapper for Miller's indices searcher"""
    locations = array(locations)

    def progress(status):
        status["description"] = _("Trying to find Miller's indices...")
        total = 2 ** len(locations)
        fit_ = FitIndices(cs, max_index)
        max_res15 = int(1.5 * max_results)
        for i, c in enumerate(product(*(((0, 1),) * len(locations)))):
            npeaks = sum(c)
            if npeaks < min_peaks:
                continue
            status["part"] = i / total
            if status.get("stop"):
                break
            mask = array(c, dtype=bool)
            minc = (cs,) + fit_(locations[mask], ini_p)
            result.append(minc + (c,))
            if len(result) > max_res15:
                result.sort(key=lambda x: x[1][6])
                del result[max_results:]
        result.sort(key=lambda x: x[1][6])
        del result[max_results:]
        status["complete"] = True

    return progress
