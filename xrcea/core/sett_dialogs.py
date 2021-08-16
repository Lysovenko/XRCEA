"""settings dialogs"""
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

from .application import APPLICATION
from .vi import input_dialog


def edit_components():
    descid = [(des['id'], des) for des in APPLICATION.compman.descriptions]
    descid.sort()
    complist = [(des['name'], des['isactive']) for i, des in descid]
    dlgr = input_dialog(_("Select components"),
                        _("Select required components"), complist)
    if dlgr:
        for d, a in zip(list(zip(*descid))[1], dlgr):
            d['isactive'] = a
        APPLICATION.compman.terminate()
        if not APPLICATION.compman.introduce():
            APPLICATION.compman.get_active()
