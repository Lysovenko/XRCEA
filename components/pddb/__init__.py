# XRCEA (C) 2019 Serhii Lysovenko
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

from core.application import APPLICATION as APP
from core.vi import input_dialog
from core.idata import XrayData
from .browser import show_browser, set_plot
show_me = show_browser
_opts = _("&Options")
_tools = _("&Tools")


def introduce():
    """Entry point. Declares menu items."""
    APP.menu.append_item((_opts,), _("Configure PDDB..."), configure, None)
    APP.menu.append_item((_tools,), _("DB browser"), show_browser, None)
    APP.settings.declare_section("PDDB")
    XrayData.actions[(_tools, _("Compare with DB pattern"))] = set_plot


def terminate():
    """unloader"""


def configure():
    db_file = APP.settings.get("db_file", "", "PDDB")
    masks = (("*.db", _("DB Files")),)
    db_file = {"Filename": db_file, "Masks": masks}
    sett = input_dialog(_("PDDB settings"), _("Database browser settings"),
                        [(_("Database file:"), db_file)])
    if sett is None:
        return
    for i, j in zip(("interval", "snd_new", "snd_imp", "snd_act",
                     "snd_rem", "snd_err", "clear_after"), sett):
        APP.settings.set("db_file", sett[0], "PDDB")
    pass
