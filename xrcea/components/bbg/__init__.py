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

from xrcea.core.application import APPLICATION as APP
from .splane import detect_plane_shift
from .polynomial import detect_polynome


def introduce():
    """Entry point. Declares menu items."""
    cryp = APP.runtime_data.setdefault("cryp", {})
    extra = cryp.setdefault("extra_calcs", [])
    extra.append((_("Fix angle"), detect_polynome))
    extra.append((_("Detect plane shift"), detect_plane_shift))
    APP.settings.declare_section("BBG")


def terminate():
    """"""
