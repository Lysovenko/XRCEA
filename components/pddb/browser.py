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

import locale
from core.vi import Page, Button, print_error
from core.vi.value import Value
from core.application import APPLICATION as APP
from .pddb import Database, formula_markup, switch_number


PARAMS = {}


class Browser(Page):
    def __init__(self, db):
        self.cards = Value(list)
        self.nums = set()
        self._database = db
        styles = {"D": (None, "red")}
        super().__init__(_("Database browser"),
                         self.cards,
                         (_("Number"), _("Name"), _("Formula")),
                         styles)
        self.show()
        self._query = Value(str)
        self.set_form([(Button(_("Search:"), self.search), self._query)], True)
        self.set_choicer(self.click_card)

    def click_card(self, tup):
        card = tup[-1]
        self.set_text(self.mkhtext(card))

    def search(self, query):
        ""
        try:
            cards = self._database.select_cards(query)
        except ValueError:
            return print_error(_("Query error"), _("Wrong Query"))
        self._query.update("")
        ext = [(switch_number(c), n, f, (set(q), None, None), c)
               for c, n, f, q in cards if c not in self.nums]
        self.nums.update(r[-1] for r in ext)
        self.cards.update(self.cards.get() + ext)

    def mkhtext(self, cid):
        db = self._database
        qual = db.quality(cid)
        qual = qual[1] + _(" (Deleted)") if qual[0] == "D" else qual[1]
        res = (_("""
<table>
<tr><td>Number:</td><td>%(num)s</td></tr>
<tr><td>Name:</td><td>%(nam)s</td></tr>
<tr><td>Formula:</td><td>%(fml)s</td></tr>
<tr><td>Quality:</td><td>%(qlt)s</td></tr>
""") %
               {"num": switch_number(cid), "nam": db.name(cid),
                "fml": db.formula_markup(cid), "qlt": qual})
        cell = db.cell_params(cid)
        if cell:
            pnr = ["a", "b", "c", "\u03b1", "\u03b2", "\u03b3"]
            res += "<tr><td>%s</td><td>" % _("Cell parameters:")
            ppr = []
            for p, v in cell:
                ppr.append("%s=%s" % (pnr[p], locale.format("%g", v)))
            res += "; ".join(ppr) + "</td></tr>\n"
        spc_grp = db.spacegroup(cid)
        if spc_grp:
            res += "<tr><td>%s</td><td>%s</td></tr>\n" % \
                (_("Space group:"), spc_grp)
        res += "</table>\n"
        rtbl = "<br>\n<br>\n<table border=1>\n"
        rtblr = "<tr>"
        rcels = 0
        for reflex in db.reflexes(cid, True):
            if reflex[2] is None:
                rtblr += "<td><pre> %s %3d </pre></td>" % \
                    ((locale.format("%.5f", reflex[0]),) + reflex[1:2])
            else:
                rtblr += "<td><pre> %s %3d  %4d%4d%4d </pre></td>" % \
                    ((locale.format("%.5f", reflex[0]),) + reflex[1:])
            rcels += 1
            if rcels == 3:
                rtbl += rtblr + "</tr>\n"
                rtblr = "<tr>"
                rcels = 0
        if rcels:
            for reflex in range(rcels, 3):
                rtblr += "<td></td>"
            rtbl += rtblr + "</tr>\n"
        res += rtbl + "</table>\n"
        comment = db.comment(cid)
        if comment:
            res += _("<h5>Comment</h5>")
            for cod, val in comment:
                if cod == "CL":
                    res += _("Color: ")
                res += val + "<br>\n"
        res += _("<h5>Bibliography</h5>\n")
        res += "<ul>\n"
        for source, vol, page, year, authors in db.citations(cid):
            lit = "<li>"
            if authors:
                lit += "%s // " % authors
            if source:
                lit += source
            if vol:
                lit += ", <b>%s</b>" % vol
            if page:
                lit += ", P. %s" % page
            if year:
                lit += " (%d)" % year
            res += lit + "</li>\n"
        res += "</ul>\n"
        return "".join(["<html><body>", res, "</body></html>"])


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
