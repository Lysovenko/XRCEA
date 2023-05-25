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
"""

from xrcea.core.application import APPLICATION as APP
from xrcea.core.vi import input_dialog, ask_save_filename
from os.path import splitext, isfile


def introduce():
    APP.menu.append_item(APP.prj_path, _("Save description..."),
                         save_description, None)


def save_description():
    fname = ask_save_filename(
        _("Save description"), "",
        [("*.tex", _("TeX files"))])
    if fname:
        if splitext(fname)[1] != ".tex":
            fname += ".tex"
        with open(fname, "w") as f:
            f.write("Hello world\n")
