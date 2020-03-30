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

import numpy as np
from .pddb import Database


class ObjDB:
    objtype = "opddb"
    type = _("XRD cards")

    def __init__(self, obj=None, dbpath=None):
        try:
            self._database = Database(dbpath)
        except (RuntimeError, TypeError) as err:
            self._database = None
            if obj is None:
                raise err
        if obj is None:
            self._db_obj = {"objtype": self.objtype, "cards": {}}
        else:
            self._db_obj = obj

    def get_obj(self):
        return self._db_obj

    def select_cards(self, query):
        if self._database is not None:
            return self._database.select_cards(query)
        return []

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

    def name(self, cid):
        if cid in self._db_obj["cards"]:
            return self._db_obj["cards"][cid].get("name")
        if self._database is not None:
            return self._database.name(cid)

    def formula_markup(self, cid):
        if cid in self._db_obj["cards"]:
            return self._db_obj["cards"][cid].get("formula")
        if self._database is not None:
            return self._database.formula_markup(cid)

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
                    "set label \"(%d %d %d)\" at %g, second %g left rotate" %
                    (reflex + (pos, intens)))
        return "\n".join(out)
