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
        super().__init__(str(xrd.name) + _(" Visual Analyser"))
        self._default_instrumental_broadening_range = {
            "start": 0.0,
            "stop": 0.5,
            "points": 100,
            "name": 0,
        }
        self._default_williamson = {"name": 0, "instr": 0.0}
        self.menu.append_item(
            (_calculate,),
            _("Peak broadening Correlation..."),
            self.calc_broad_corelation,
            None,
        )
        self.menu.append_item(
            (_calculate,),
            _("Size and strain..."),
            self.calc_size_strain,
            None,
        )
        self.menu.append_item(
            (_calculate,),
            _("Parameters of approximation line..."),
            self.plot_least_sqares,
            None,
        )
        self.menu.append_item(
            (_calculate,),
            _("Draw Williamson-Hall Plot..."),
            self.williamson_hall_plot,
            None,
        )

    def _ask_instrumental_broadening_range(self, asker):
        ibr = self._default_instrumental_broadening_range
        try:
            names = tuple(self._xrd.extra_data["UserIndexes"].keys())
            dlgr = self.input_dialog(
                _("Set instrumental broadening range\nfor ") + asker,
                [
                    (_("From:"), ibr["start"]),
                    (_("To:"), ibr["stop"]),
                    (_("Points:"), ibr["points"]),
                    (_("Name:"), names, ibr["name"]),
                    (_("Show all:"), False),
                ],
            )
        except (KeyError, AttributeError):
            return
        if dlgr is not None:
            ibr["start"], ibr["stop"], ibr["points"], ibr["name"], _d = dlgr
            start, stop, points, name, all_names = dlgr
            if not all_names:
                names = (names[name],)
            return start, stop, points, names
        return dlgr

    def calc_broad_corelation(self):
        """Display dialog to calc correlation"""
        dlgr = self._ask_instrumental_broadening_range(
            _("broadening correlation plot")
        )
        if dlgr is None:
            return
        start, stop, points, names = dlgr
        try:
            bro = BroadAn(self._xrd)
        except KeyError:
            self.print_error(_("Can not launch broadening analyser"))
            return
        plots = []
        for name in names:
            plots.append(bro.plot_correlation(name, start, stop, points))
        self.add_plot(
            _("Correlation"),
            {
                "plots": plots,
                "x1label": _("Instrumental broadening"),
                "y1label": _("Correlation"),
            },
        )
        self.draw(_("Correlation"))

    def calc_size_strain(self):
        """Display dialog to calc siaze and strain"""
        dlgr = self._ask_instrumental_broadening_range(
            _("size and strain plot")
        )
        if dlgr is None:
            return
        start, stop, points, names = dlgr
        try:
            bro = BroadAn(self._xrd)
        except KeyError:
            self.print_error(_("Can not launch broadening analyser"))
        plots = []
        for name in names:
            plots.extend(bro.plot_size_strain(name, start, stop, points))
        self.add_plot(
            _("Size + Strain"),
            {
                "plots": plots,
                "x1label": _("Instrumental broadening"),
                "y1label": _("Size"),
                "y2label": _("Strain"),
            },
        )
        self.draw(_("Size + Strain"))

    def williamson_hall_plot(self):
        r"""Williamson-Hall Plot
        $\beta_{tot}\cos\theta$ versus $\sin\theta$"""
        def_will = self._default_williamson
        try:
            names = tuple(self._xrd.extra_data["UserIndexes"].keys())
            dlgr = self.input_dialog(
                _("Parameters for Williamson-Hall Plot"),
                [
                    (_("Name:"), names, def_will["name"]),
                    (_("Instrumental broadening:"), def_will["instr"]),
                ],
            )
        except (KeyError, AttributeError):
            return
        if dlgr is None:
            return
        name, instr_broad = dlgr
        def_will["name"], def_will["instr"] = dlgr
        name = names[name]
        try:
            bro = BroadAn(self._xrd)
            upd_plot = bro.plot_williamson_hall(name, instr_broad)
        except KeyError:
            self.print_error(_("Can not launch broadening analyser"))
            return
        pname = _("Williamson-Hall Plot")
        plot = {
            "x1label": r"$\sin\theta$",
            "y1label": r"$B\cos\theta$",
        }
        plot.update(upd_plot)
        self.add_plot(
            pname,
            plot,
        )
        self.draw(pname)

    def plot_least_sqares(self):
        dlgr = self._ask_instrumental_broadening_range(
            _("least squares optimization")
        )
        if dlgr is None:
            return
        start, stop, points, names = dlgr
        try:
            bro = BroadAn(self._xrd)
        except KeyError:
            self.print_error(_("Can not launch broadening analyser"))
            return
        plots = []
        for name in names:
            plots.extend(bro.plot_lstsq(name, start, stop, points))
        plot_name = _("Approximation line parameters")
        self.add_plot(
            plot_name,
            {
                "plots": plots,
                "x1label": _("Instrumental broadening"),
                "y1label": _("Correlation"),
            },
        )
        self.draw(plot_name)


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
