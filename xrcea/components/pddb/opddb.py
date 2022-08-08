# XRCEA (C) 2020 Serhii Lysovenko
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
"""Representation of PDDB cards as Python's objects"""

from locale import atof
import numpy as np
from xrcea.core.application import APPLICATION as APP
from .pddb import Database, formula_markup, switch_number
from .browser import PARAMS, Browser, print_error


class ObjDB:
    objtype = "opddb"
    type = _("XRD cards")

    def __init__(self, obj=None):
        self.marked = set()
        if obj is None:
            err = self._database
            if isinstance(err, Exception):
                raise err
            self._db_obj = {"objtype": self.objtype, "cards": {}}
        else:
            self._db_obj = obj
        cards = self._db_obj["cards"]
        for k in list(cards.keys()):
            try:
                ik = int(k)
                cards[ik] = cards.pop(k)
            except ValueError:
                pass

    @property
    def _database(self):
        try:
            return self._db
        except AttributeError:
            try:
                self._db = Database(APP.settings.get("db_file", "", "PDDB"))
                return self._db
            except (RuntimeError, TypeError) as err:
                self._db = None
                return err

    @property
    def name(self):
        return _("DB Cards")

    def __eq__(self, x):
        if isinstance(x, str):
            return x == self.name
        if isinstance(x, type(self)):
            return self.name == x.name
        return False

    def get_obj(self):
        used = set()
        for comp in self._container.components():
            try:
                used.update(map(int, comp.extra_data["pddb_colors"].keys()))
            except (AttributeError, KeyError, ValueError):
                pass
        used.update(self.marked)
        cards = self._db_obj["cards"]
        cset = set(cards.keys())
        to_drop = cset - used
        for cid in to_drop:
            cards.pop(cid)
        for cid in used - cset:
            self.add_card(cid, emit=False)
        return self._db_obj

    def select_cards(self, query):
        if query is None:
            return [(k, v["name"], v["formula"], v["quality"])
                    for k, v in self._db_obj["cards"].items()]
        if isinstance(self._database, Database):
            return self._database.select_cards(query)
        return []

    def filter_cards(self, query, xtype, wavel, cids):
        conds = []
        for chunk in query.split(";"):
            vals = list(map(atof, chunk.split()))
            if len(vals) >= 3:
                a, b, c = vals[:3]
            elif len(vals) == 2:
                a, b = vals
                c = 0.
            else:
                raise ValueError("Too short chunk %s" % chunk)
            if a > b:
                a, b = b, a
            conds.append((a, b, c))
        result = []
        for cid in cids:
            refls = self.reflexes(cid)
            if not refls:
                continue
            dis = self.get_di(cid, xtype, wavel)
            passed = 0
            for f, t, mi in conds:
                gd = (dis[0] >= f).__and__(dis[0] <= t).__and__(dis[1] >= mi)
                if gd.any():
                    passed += 1
            if passed == len(conds):
                result.append(cid)
        return [(c, self.card_name(c), self.formula_markup(c, None),
                 self.quality(c)) for c in result]

    def list_cards(self, cids):
        return [(c, self.card_name(c), self.formula_markup(c, None),
                 self.quality(c)) for c in cids]

    def quality(self, cid):
        if cid in self._db_obj["cards"]:
            return self._db_obj["cards"][cid].get("quality")
        if self._database is not None:
            return self._database.quality(cid)

    def cell_params(self, cid):
        if cid in self._db_obj["cards"]:
            return self._db_obj["cards"][cid].get("params")
        if self._database is not None:
            return self._database.cell_params(cid)

    def spacegroup(self, cid):
        if cid in self._db_obj["cards"]:
            return self._db_obj["cards"][cid].get("spacegroup")
        if self._database is not None:
            return self._database.spacegroup(cid)

    def reflexes(self, cid, hkl=False):
        if cid in self._db_obj["cards"]:
            if hkl:
                return self._db_obj["cards"][cid].get("reflexes")
            else:
                return [i[:2] for i in
                        self._db_obj["cards"][cid].get("reflexes")]
        if self._database is not None:
            return self._database.reflexes(cid, hkl)

    def comment(self, cid):
        if cid in self._db_obj["cards"]:
            return self._db_obj["cards"][cid].get("comment")
        if self._database is not None:
            return self._database.comment(cid)

    def card_name(self, cid):
        if cid in self._db_obj["cards"]:
            return self._db_obj["cards"][cid].get("name")
        if self._database is not None:
            return self._database.name(cid)

    def formula_markup(self, cid, mtype="HTML"):
        formula = None
        if cid in self._db_obj["cards"]:
            formula = self._db_obj["cards"][cid].get("formula")
        elif self._database is not None:
            formula = self._database.formula(cid)
        if formula:
            if mtype == "HTML":
                return formula_markup(formula)
            return formula
        return ''

    def citations(self, cid):
        if cid in self._db_obj["cards"]:
            return self._db_obj["cards"][cid].get("citations")
        if self._database is not None:
            return self._database.citations(cid)

    def get_di(self, cid, xtype="q", wavel=(), between=None):
        reflexes = self.reflexes(cid)
        if not reflexes:
            return [], []
        dis = np.array(reflexes, "f").transpose()
        intens = dis[1]
        if intens.max() == 999.:
            for i in (intens == 999.).nonzero():
                intens[i] += 1.
            intens /= 10.
        if not isinstance(wavel, (tuple, list)):
            wavel = (wavel,)
            single = True
        else:
            single = False
        abscisas = []
        restore = np.seterr(invalid="ignore")
        for wave in wavel:
            if xtype == "sin(theta)":
                abscisas.append(wave / 2. / dis[0])
            elif xtype == "theta":
                abscisas.append(np.arcsin(wave / 2. / dis[0]) / np.pi * 180.)
            elif xtype == "2theta":
                abscisas.append(np.arcsin(wave / 2. / dis[0]) / np.pi * 360.)
        if xtype == "q":
            abscisas.append((2. * np.pi) / dis[0])
        elif not abscisas:
            abscisas.append(dis[0])
        if between:
            res = []
            for x in abscisas:
                b = x >= min(between)
                b &= x <= max(between)
                res.append((x[b], intens[b]))
        else:
            res = [(x, intens) for x in abscisas]
        np.seterr(**restore)
        if single:
            return res[0]
        return res

    def gnuplot_lables(self, cid, xtype="q", wavel=()):
        refl = [i[2:] for i in self.reflexes(cid, True)]
        dis = self.get_di(cid, xtype, wavel)
        if isinstance(dis, list):
            return ""
        out = []
        for pos, intens, reflex in zip(dis[0], dis[1], refl):
            out.append(
                "set arrow from %g, second 0 rto 0, second %g nohead" %
                (pos, intens))
            if reflex[0] is not None:
                out.append(
                    "set label \"%s (%d %d %d)\" "
                    "at %g, second %g left rotate" %
                    ((switch_number(cid),) + tuple(reflex) + (pos, intens)))
            else:
                out.append(
                    "set label \"%s\" "
                    "at %g, second %g left rotate" %
                    (switch_number(cid), pos, intens))
        return "\n".join(out)

    def xrd_units_table(self, cid, xtype="q", wavel=()):
        refl = [i[2:] for i in self.reflexes(cid, True)]
        dis = self.get_di(cid, xtype, wavel)
        if isinstance(dis, list):
            return ""
        out = []
        for pos, intens, reflex in zip(dis[0], dis[1], refl):
            if reflex[0] is not None:
                hkl = "%d %d %d" % tuple(reflex)
            else:
                hkl = ""
            out.append("<tr><td>%g</td><td>%g</td><td>%s</td></tr>" %
                       (pos, intens, hkl))
        xt = {'2theta': u"2\u03b8, \u00B0", "theta": u"\u03b8, \u00B0",
              "q": u"q, \u212b^{-1}", None: u"d, \u212b"}[xtype]
        return """<!DOCTYPE html><html>
        <head><style>
table {
  border-collapse: collapse;
  border-bottom: 1px solid;
  border-top: 1px solid;
  border-right: 1px solid;
  border-left: 1px solid;
}
th {border-bottom: 1px solid;
border-right: 1px solid;}
td {
  text-align: left;
  padding-right: 3ex;
  padding-left: 1ex;
  border-right: 1px solid;
}
        </style></head>
        <body>
        <h1>%(name)s</h1>
        <p>%(number)s</p>
        <p>%(formula)s</p>
        <table>
        <tr><th>%(thead)s</th><th>I, %%</th><th>h k l</th></tr>
        %(tbody)s</table></body></html>
        """ % {"thead": xt, "tbody": "\n".join(out),
               "name": self.card_name(cid),
               "formula": self.formula_markup(cid),
               "number": switch_number(cid)}

    def display(self):
        """Display pddb cards set"""
        show_browser(self)

    def _emit_changed(self):
        try:
            self._container.element_changed(self)
        except AttributeError:
            pass

    def set_container(self, container):
        self._container = container

    def add_card(self, cid, cache=False, emit=True):
        """
        Add card to "cache\"

        Parameters
        ----------
        cid : int
            card id
        cache : bool
            Chech if card in cache and do nothing if true
        """
        if cache and cid in self._db_obj["cards"]:
            return
        card = {}
        card["quality"] = self.quality(cid)
        card["params"] = self.cell_params(cid)
        card["spacegroup"] = self.spacegroup(cid)
        card["reflexes"] = self.reflexes(cid, True)
        card["comment"] = list(self.comment(cid))
        card["name"] = self.card_name(cid)
        if self._database:
            card["formula"] = self._database.formula(cid)
        card["citations"] = self.citations(cid)
        self._db_obj["cards"][cid] = card
        if emit:
            self._emit_changed()


def show_browser(objdb=None):
    if not PARAMS.get("Browser"):
        if objdb is None:
            try:
                db = ObjDB()
            except RuntimeError as err:
                return print_error(_("DB opening error"),
                                   _("Failed to open DB file: %s") % str(err))
        else:
            db = objdb
        PARAMS["Browser"] = Browser(db)
    else:
        PARAMS["Browser"].show()
        if objdb is not None:
            PARAMS["Browser"].set_list(objdb)
