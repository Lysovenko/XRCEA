#!/usr/bin/env python3
# XRCEA (C) 2022 Serhii Lysovenko
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

from .pddb import switch_number
_name = _("PDDB Pattern")


def plot_over(pddb, xrd, cur=None):
    """
    """
    try:
        plot = xrd.UIs["main"]
    except KeyError:
        return
    name, plt = plot.get_current()
    if plt is None:
        return
    limits = plot.get_limits()
    if name == _name:
        for p in reversed(plt["plots"]):
            if p.get("type") == "pulse":
                plt["plots"].pop()
            else:
                break
    if not plt["plots"]:
        return
    try:
        plt["plots"][0]["ylim"] = limits[0]["ylim"]
    except KeyError:
        pass
    xrd.remember_plot(_name, "pddb_pattern")
    plot.add_plot(_name, extend_plt(plt, xrd, pddb, cur))
    plot.draw(_name)


def restore_plot(xrd):
    pddb = None
    for comp in xrd.get_container().components():
        if comp.objtype == "opddb":
            pddb = comp
            break
    if pddb is None:
        return
    plt = xrd.make_plot()
    return extend_plt(plt, xrd, pddb)


def extend_plt(plt, xrd, pddb, cur=None):
    colors = dict(xrd.extra_data.get("pddb_colors", ()))
    if cur is not None and cur not in colors:
        colors[cur] = "red"
    if not colors:
        return
    xmin = xrd.x_data.min()
    xmax = xrd.x_data.max()
    units = xrd.x_units
    wavis = [(wavel, intens) for wavel, intens in (
        (xrd.lambda1, 1.), (xrd.lambda2, xrd.I2), (xrd.lambda3, xrd.I3))
        if wavel is not None and intens is not None]
    wavels = tuple(i[0] for i in wavis)
    for card, clr in ((int(i), j) for i, j in colors.items()):
        dis = pddb.get_di(card, units, wavels, (xmin, xmax))
        for (x, y), lstl, (w, i) in zip(dis, (
                "solid", "dashed", "dashdot"), wavis):
            eplt = {"type": "pulse", "linestyle": lstl, "color": clr}
            if lstl == "solid":
                eplt["legend"] = "{} ({})".format(
                    pddb.formula_markup(card, None),
                    switch_number(card))
            eplt["x1"] = x
            eplt["y2"] = y * i
            plt["plots"].append(eplt)
    return plt
