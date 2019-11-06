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
        self._cur_card = None
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
        self._cur_card = card
        self.set_text(self.mkhtext(card))
        self.plot()

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

    def plot(self):
        card = self._cur_card
        plot = PARAMS.get("Plot")
        if not (plot and card):
            return
        name, plt = plot.get_current()
        if plt is None:
            return
        xrd = PARAMS.get("XRD")
        if not xrd:
            return
        _name = _("PDDB Pattern")
        if name == _name:
            for p in reversed(plt["plots"]):
                if p.get("type") == "pulse":
                    plt["plots"].pop()
                else:
                    break
        if not plt["plots"]:
            return
        xmin = min(plt["plots"][0]["x1"])
        xmax = max(plt["plots"][0]["x1"])
        for p in plt["plots"][1:]:
            xmin = min(xmin, min(p["x1"]))
            xmax = max(xmax, max(p["x1"]))
        units = plt["x1units"]
        for wavel, intens, clr in (
                (xrd.lambda1, 1., "red"), (xrd.lambda2, xrd.I2, "orange"),
                (xrd.lambda3, xrd.I3, "green")):
            if wavel is None or intens is None:
                continue
            eplt = {"type": "pulse", "color": clr}
            x, y = self._database.get_di(card, units, wavel)
            y *= intens
            x, y = zip(*(xy for xy in zip(x, y) if xmin <= xy[0] <= xmax))
            eplt["x1"] = x
            eplt["y2"] = y
            plt["plots"].append(eplt)
        plot.add_plot(_name, plt)
        plot.draw(_name)


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


def set_plot(plotting):
    PARAMS["Plot"] = plotting.UI
    PARAMS["XRD"] = plotting
    if PARAMS.get("Browser"):
        PARAMS["Browser"].plot()
