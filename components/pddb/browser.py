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

from core.vi import Lister, Button, print_error
from core.vi.value import Value
from core.application import APPLICATION as APP
from .pddb import Database, formula_markup, switch_number


PARAMS = {}


class Browser(Lister):
    def __init__(self, db):
        self.cards = Value(list)
        self.nums = set()
        self._database = db
        styles = {"DC": (None, "red")}
        super().__init__(_("Database browser"),
                         [(_("Cards"),
                           (_("Number"), _("Name"), _("Formula")))],
                         [self.cards], styles)
        self.show()
        self.set_choicer(self.click_card, False)
        self.set_form(((Button(_("Search:"), self.search), ""),), 0, True)

    def click_card(self, tup):
        card = tup[-1]
        print(tup, type(card))

    def search(self, query):
        ""
        try:
            cards = self._database.select_cards(query)
        except ValueError:
            return print_error(_("Query error"), _("Wrong Query"))
        ext = [(str(c), n, f, (q, None, None), c)
               for c, n, f, q in cards if c not in self.nums]
        self.nums.update(r[-1] for r in ext)
        self.cards.update(self.cards.get() + ext)


def show_browser():
    if not PARAMS.get("Browser"):
        try:
            db = Database(APP.settings.get("db_file", "", "PDDB"))
        except RuntimeError as err:
            return print_error(_("DB opening error"),
                               _("Failed to open DB file: %s") % str(err))
        PARAMS["Browser"] = Browser(db)
    else:
        PARAMS["Browser"].show()
    
