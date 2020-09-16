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
from core.vi import Page, Button, print_error, input_dialog
from core.vi.value import Value
from core.application import APPLICATION as APP
from .pddb import switch_number

PARAMS = {}


class Browser(Page):
    def __init__(self, db):
        self.cards = Value(list)
        self.nums = set()
        self._database = db
        self._cur_card = None
        self._query = Value(str)
        self.search()
        styles = {"D": (None, "red")}
        super().__init__(_("Database browser"),
                         self.cards,
                         (_("Number"), _("Name"), _("Formula")),
                         styles)
        self.show()
        self.set_form([(Button(_("Search:"), self.search), self._query)], True)
        self.set_choicer(self.click_card)
        self.set_list_context_menu([
            (_("Delete"), self.del_the_card),
            (_("Print GNUPlot labels"), self.print_gp_labels),
            (_("Clear deleted"), self.remove_deleted),
            (_("Save cards list"), self.save_list),
            (_("Remember peaks positions"), self.predefine_reflexes),
        ])

    def click_card(self, tup):
        card = tup[-1]
        self._database.add_card(card, True)
        self._cur_card = card
        self.set_text(self.mkhtext(card))
        self.plot()

    def del_the_card(self, row, c=None):
        cl = self.cards.get()
        cl.remove(row)
        self.cards.update(cl)
        self.nums = set(i[-1] for i in self.cards.get())

    def remove_deleted(self, row, c=None):
        cl = self.cards.get()
        self.cards.update(i for i in cl if "D" not in i[3][0])
        self.nums = set(i[-1] for i in self.cards.get())

    def search(self, query=None):
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
               {"num": switch_number(cid), "nam": db.card_name(cid),
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
                    ((locale.format("%.5f", reflex[0]),) + tuple(reflex[1:2]))
            else:
                rtblr += "<td><pre> %s %3d  %4d%4d%4d </pre></td>" % \
                    ((locale.format("%.5f", reflex[0]),) + tuple(reflex[1:]))
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
        wavis = [(wavel, intens) for wavel, intens in (
            (xrd.lambda1, 1.), (xrd.lambda2, xrd.I2), (xrd.lambda3, xrd.I3))
            if wavel is not None and intens is not None]
        wavels = tuple(i[0] for i in wavis)
        dis = self._database.get_di(card, units, wavels, (xmin, xmax))
        for (x, y), clr, (w, i) in zip(dis, ("red", "orange", "green"), wavis):
            eplt = {"type": "pulse", "color": clr}
            eplt["x1"] = x
            eplt["y2"] = y * i
            plt["plots"].append(eplt)
        plot.add_plot(_name, plt)
        plot.draw(_name)

    def print_gp_labels(self, row, c=None):
        cid = row[-1]
        xrd = PARAMS.get("XRD")
        if not xrd:
            return
        plot = PARAMS.get("Plot")
        if not plot:
            return
        name, plt = plot.get_current()
        if plt is None:
            return
        units = plt["x1units"]
        wavis = [(wavel, intens) for wavel, intens in (
            (xrd.lambda1, 1.), (xrd.lambda2, xrd.I2), (xrd.lambda3, xrd.I3))
            if wavel is not None and intens is not None]
        wavels = tuple(i[0] for i in wavis)
        print(self._database.gnuplot_lables(cid, units, wavels[0]))

    def save_list(self, r=None, c=None):
        """Save cards list in project"""
        db = self._database
        if not db.name:
            pars = input_dialog(_("Card list"), _("Card list"),
                                [(_("Name:"), "")])
            if not pars:
                return
            name, = pars
            if not name:
                return
            db.name = name
        db.update_content(self.nums)
        if not db.in_container():
            APP.add_object(db)

    def set_list(self, objdb):
        self._database = objdb
        self.cards.update([])
        self.search()

    def predefine_reflexes(self, row, c=None):
        cid = row[-1]
        APP.runtime_data["User refl"] = [
            r[0] for r in self._database.reflexes(cid, True)]


def set_plot(plotting):
    PARAMS["Plot"] = plotting.UI
    PARAMS["XRD"] = plotting
    if PARAMS.get("Browser"):
        PARAMS["Browser"].plot()
