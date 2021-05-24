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
from time import sleep


def find_indices(locations, result):
    """Wrapper for Miller's indices searcher"""

    def progress(status):
        status["description"] = _("Trying to find Miller's indices...")
        total = 2 ** len(locations)
        for i, c in enumerate(product(*(((0, 1),) * len(locations)))):
            status["part"] = i / total
            if status.get("stop"):
                break
            sleep(0.001)
        status["complete"] = True

    return progress
