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
from xrcea.core.description import Description, Title, Paragraph
from os.path import splitext, isfile


def introduce():
    APP.menu.append_item(APP.prj_path, _("Save description..."),
                         save_description, None)


def get_description():
    res = Description()
    res.title = APP.get_name()
    res.append(Title(APP.get_name(), 1))
    for obj in APP.get_objects():
        res.append(Title(obj.name, 2))
        if isinstance(getattr(obj, "comment", None), str):
            res.append(Title(_("Comment"), 3))
            for c in obj.comment.splitlines():
                res.append(Paragraph(c))
        for Desc in APP.runtime_data.get("Describers", {}).values():
            descr = Desc(obj)
            descr.write(res)
    return res


def save_description():
    fname = ask_save_filename(
        _("Save description"), "",
        [("*.html", _("HTML files")), ("*.txt", _("Plain text")),
         ("*.tex", _("TeX files"))])
    if fname:
        if splitext(fname)[1] not in (".html", ".tex", ".txt"):
            fname += ".html"
        ext = splitext(fname)[1]
        if ext == ".html":
            from .html import write_html
            write_html(get_description(), fname)
