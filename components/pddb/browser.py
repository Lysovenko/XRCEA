#!/usr/bin/env python3
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

from .pddb import Database, formula_markup, switch_number
from core.vi import Lister, Button
from core.vi.value import Value


PARAMS = {}


class Browser(Lister):
    def __init__(self):
        cards = Value(list)
        styles = {}
        super().__init__(_("Database browser"),
                         [(_("Number"), (_("Name"), "Formula"))],
                         [cards], styles)
        self.show()
        self.set_choicer(self.click_card, False)
        self.set_form(((Button(_("Search:"), self.search), ""),), 0, True)

    def click_card(self, tup):
        card = tup[-1]

    def search(self, query):
        ""

def show_browser():
    if not PARAMS.get("Browser"):
        PARAMS["Browser"] = Browser()
    else:
        PARAMS["Browser"].show()
    
