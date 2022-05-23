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
from xrcea.core.idata import XrayData
from xrcea.core.vi import Page, Button, print_error, input_dialog
from xrcea.core.vi.value import Value
from xrcea.core.application import APPLICATION as APP
from .pddb import switch_number

PARAMS = {}
COLORS, COLORNAMES = zip(*(
    ("blue", _("Blue")),
    ("orange", _("Orange")),
    ("green", _("Green")),
    ("red", _("Red")),
    ("purple", _("Purple")),
    ("brown", _("Brown")),
    ("pink", _("Pink")),
    ("gray", _("Gray")),
    ("olive", _("Olive")),
    ("cyan", _("Cyan"))))


class Browser(Page):
    def __init__(self, db):
        self.cards = Value(list)
        self.nums = set()
        self._database = db
        self._cur_card = None
        self._query = Value(str)
        self._colored_cards = {}
        self._marked_cards = set()
        self.search()
        styles = {i: (i, None) for i in COLORS}
        styles["D"] = (None, "red")
        super().__init__(_("Database browser"),
                         self.cards,
                         (_("Number"), _("Name"), _("Formula"), _("On plot")),
                         styles)
        self.show()
        self.set_form([(Button(_("Search:"), self.search), self._query)], True)
        self.set_choicer(self.click_card)
        self.set_list_context_menu([
            (_("Clear deleted"), self.remove_deleted),
            (_("Clear non marked"), self.remove_nonmarked),
            (_("Show on plot as..."), self.add_colored),
            (_("Mark the card"), self.mark_card),
            (_("Delete"), self.del_the_card),
            (_("Save cards list"), self.save_list),
            (_("Show reflexes in data units"), self.print_in_xrd_units),
            (_("Print GNUPlot labels"), self.print_gp_labels),
        ])

    def click_card(self, tup):
        card = tup[-1]
        self._database.add_card(card, True)
        self._cur_card = card
        self.set_text(self.mkhtext(card))
        self._upd_clrs()
        self.plot()

    def mark_card(self, row, c=None):
        self._marked_cards.add(row[-1])
        nu, na, fo, pt, (snu, sna, sfo, spt), cn = row
        sna = "blue"
        cl = self.cards.get()
        cl[cl.index(row)] = nu, na, fo, pt, (snu, sna, sfo, spt), cn
        self.cards.update(cl)

    def del_the_card(self, row, c=None):
        cl = self.cards.get()
        self._marked_cards.discard(row[-1])
        self.nums.discard(row[-1])
        cl.remove(row)
        self.cards.update(cl)
        if self._colored_cards.pop(row[-1], None) is not None:
            self._upd_clrs()
            self.plot(True)

    def remove_deleted(self, row, c=None):
        cl = self.cards.get()
        self.cards.update(i for i in cl if "D" not in i[4][0])
        self.nums = set(i[-1] for i in self.cards.get())
        self._marked_cards.intersection_update(self.nums)
        ncolored = len(self._colored_cards)
        for i in self.nums.symmetric_difference(
                self._colored_cards).intersection(self._colored_cards):
            self._colored_cards.pop(i)
        if ncolored > len(self._colored_cards):
            self._upd_clrs()
            self.plot(True)

    def remove_nonmarked(self, row, c=None):
        cl = self.cards.get()
        self.cards.update(i for i in cl if i[-1] in self._marked_cards)
        self.nums.intersection_update(self._marked_cards)
        ncolored = len(self._colored_cards)
        for i in self.nums.symmetric_difference(
                self._colored_cards).intersection(self._colored_cards):
            self._colored_cards.pop(i)
        if ncolored > len(self._colored_cards):
            self._upd_clrs()
            self.plot(True)

    def search(self, query=None):
        """Run search"""
        try:
            cards = self._database.select_cards(query)
        except ValueError as err:
            return print_error(_("Query error"), str(err))
        self._query.update("")
        if query is None:
            nst = "blue"
            self._marked_cards.update(i[0] for i in cards)
        else:
            nst = None
        ext = [(switch_number(c), n, f, "", (set(q), nst, None, None), c)
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
                ppr.append("%s=%s" % (pnr[p], locale.format_string("%g", v)))
            res += "; ".join(ppr) + "</td></tr>\n"
        spc_grp = db.spacegroup(cid)
        if spc_grp:
            res += "<tr><td>%s</td><td>%s</td></tr>\n" % \
                (_("Space group:"), spc_grp)
        res += "</table>\n"
        rtbl = "<br>\n<br>\n<table border=1>\n"
        rtblr = "<tr>"
        rcels = 0
        for reflex in map(tuple, db.reflexes(cid, True)):
            if reflex[2] is None:
                rtblr += locale.format_string(
                    "<td><pre> %.5f %3d </pre></td>", reflex[:2])
            else:
                rtblr += locale.format_string(
                    "<td><pre> %.5f %3d  %4d%4d%4d </pre></td>", reflex)
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

    def plot(self, shrink=False):
        cards = dict(self._colored_cards)
        if self._cur_card is not None:
            cards[self._cur_card] = "red"
        plot = PARAMS.get("Plot")
        if not (plot and (cards or shrink)):
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
        for card, clr in cards.items():
            dis = self._database.get_di(card, units, wavels, (xmin, xmax))
            for (x, y), lstl, (w, i) in zip(dis, (
                    "solid", "dashed", "dashdot"), wavis):
                eplt = {"type": "pulse", "linestyle": lstl, "color": clr}
                if lstl == "solid":
                    eplt["legend"] = "{} ({})".format(
                        self._database.formula_markup(card, None),
                        switch_number(card))
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
        wavis = [(wavelength, intensity) for wavelength, intensity in (
            (xrd.lambda1, 1.), (xrd.lambda2, xrd.I2), (xrd.lambda3, xrd.I3))
            if wavelength is not None and intensity is not None]
        wavels = tuple(i[0] for i in wavis)
        self.set_text(self._database.gnuplot_lables(cid, units, wavels[0]))

    def print_in_xrd_units(self, row, c=None):
        cid = row[-1]
        xrd = PARAMS.get("XRD")
        if not xrd:
            xrd = XrayData.dummy_by_dialog({"question": _(
                "No plot assumed to compare.\nSet your sample params.")})
            if xrd is None:
                return
        units = xrd.x_units
        wavelength = xrd.wavelength
        self.set_text(self._database.xrd_units_table(cid, units, wavelength))

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

    def add_colored(self, row, c=None):
        """Add a card to colored"""
        exclude = set(self._colored_cards.values())
        exclude.add("red")
        try:
            clrs, nms = zip(*[i for i in zip(COLORS, COLORNAMES)
                              if i[0] not in exclude])
        except ValueError:
            self.print_error(_("No colors left."))
            return
        fields = [(_("Color:"), nms), (_("Remove"), False)]
        if row[-1] not in self._colored_cards:
            fields.pop(-1)
        ans = self.input_dialog(_("Select %s color") % row[1], fields)
        if ans is None:
            return
        if len(ans) == 2 and ans[1]:
            self._colored_cards.pop(row[-1], None)
        else:
            self._colored_cards[row[-1]] = clrs[ans[0]]
        self._upd_clrs()
        self.plot()

    def _upd_clrs(self):
        rcards = dict(self._colored_cards)
        rcards[self._cur_card] = "red"
        clrnms = {n: COLORNAMES[COLORS.index(v)] for n, v in rcards.items()}
        self.cards.update((sn, n, f, clrnms.get(c, ""),
                           (s1, s2, s3, rcards.get(c)), c)
                          for sn, n, f, d, (s1, s2, s3, s4), c
                          in self.cards.get())

    def set_list(self, objdb):
        self._database = objdb
        self.cards.update([])
        self.search()

    def export_to_xrd(self, xrd):
        cid = self._cur_card
        name = self._database.card_name(cid)
        tail = "%s %s" % (name, switch_number(cid))
        assumed = xrd.extra_data.setdefault("AssumedReflexes", [])
        old = set(i[0] for i in assumed)
        for r in self._database.reflexes(cid, True):
            if r[0] in old:
                continue
            if r[2] is None:
                comment = "%d%% %s" % (r[1], tail)
            else:
                comment = "%d%% (%d%3d%3d) %s" % (tuple(r[1:]) + (tail,))
            assumed.append([r[0], comment])
        ui = xrd.UIs.get("AssumedReflexes")
        if ui:
            ui.reread()


def set_plot(plotting):
    PARAMS["Plot"] = plotting.UIs.get("main")
    PARAMS["XRD"] = plotting
    if PARAMS.get("Browser"):
        PARAMS["Browser"].plot()


def set_positions(xrd):
    if PARAMS.get("Browser"):
        PARAMS["Browser"].export_to_xrd(xrd)
