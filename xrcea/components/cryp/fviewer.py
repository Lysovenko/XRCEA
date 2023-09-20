# XRCEA (C) 2023 Serhii Lysovenko
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
"""View functional dependencies in plot"""

from xrcea.core.vi import Plot
from .broadening import BroadAn

_calculate = _("Calculate")


class FuncView(Plot):
    def __init__(self, xrd):
        self._xrd = xrd
        super().__init__(str(xrd.name) + "Plot Exploring")
        self.menu.append_item(
            (_calculate,),
            _("Peak broadening Correlation..."),
            self.calc_broad_corelation,
            None,
        )

    def calc_broad_corelation(self):
        """Display dialog to calc correlation"""
        try:
            names = tuple(self._xrd.extra_data["UserIndexes"].keys())
            dlgr = self.input_dialog(
                _("Set instrumental broadening range"),
                [
                    (_("From:"), 0.0),
                    (_("To:"), 1.0),
                    (_("Points:"), 100),
                    (_("Name:"), names),
                    (_("Show all:"), False),
                ],
            )
        except (KeyError, AttributeError):
            return
        if dlgr is None:
            return
        start, stop, points, name, show_all = dlgr
        name = names[name]
        try:
            bro = BroadAn(self._xrd)
        except KeyError:
            self.print_error(_("Can not launch broadening analyser"))
        if not show_all:
            names = (name,)
        plots = []
        for name in names:
            x, y = bro.plot_correlation(name, start, stop, points)
            plots.append({"x1": x, "y1": y, "legend": name})
        self.add_plot(
            "Correlation",
            {
                "plots": plots,
                "x1label": _("Instrumental broadening"),
                "y1label": _("Correlation"),
            },
        )
        self.draw("Correlation")


def show_func_view(xrd):
    if "crypbells" not in xrd.extra_data:
        return
    if not xrd.extra_data.get("UserIndexes"):
        return
    p = xrd.UIs.get("FuncView")
    if p:
        p.show()
        return
    xrd.UIs["FuncView"] = FuncView(xrd)
    xrd.UIs["FuncView"].show()
