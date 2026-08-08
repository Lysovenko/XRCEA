# XRCEA (C) 2026 Serhii Lysovenko
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
""" """

from xrcea.core.application import APPLICATION as APP
from xrcea.core.vi import Page

from .description import get_description, save_description
from .html import html_from_description

_descr = _("Description")
_sett = _("Settings")
_DATA = {}


class DescriptionWindow(Page):
    """Describer"""

    def __init__(self):
        title = _("Description ") + APP.get_name()
        self._describers = tuple(
            APP.runtime_data.get("Describers", {}).values()
        )
        super().__init__(title, None)
        self.menu.append_item((_descr,), _("Save description..."), self.m_save)
        self.menu.append_item((_descr,), _("Update description"), self.update)
        for des in self._describers:
            print(des.name)
            self.menu.append_item(
                (_descr, _sett), des.name, lambda: des.settings_dialog(self)
            )
        self.show()
        self.update()

    def update(self):
        self.description = get_description()
        self.set_text(html_from_description(self.description))

    def m_save(self):
        save_description(self.description)


def show_description():
    if not _DATA.get("Window"):
        _DATA["Window"] = DescriptionWindow()
    else:
        _DATA["Window"].show()
