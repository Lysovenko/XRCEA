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
"""
"""

import numpy as np
from core.application import APPLICATION as APP
from core.idata import XrayData
from .reflex import calc_bg, refl_sects, ReflexDedect, Cryplots
_DEFAULTS = {"bg_sigmul": 2.0, "bg_polrang": 2, "refl_sigmin": 1e-3,
             "refl_consig": False, "refl_mbells": 10, "refl_bt": 0,
             "refl_ptm": 4, "refloc_sz": "(640,480)", "refl_bf": 2.}
_BELL_TYPES = ("Gaus", "Lorentz", "Voit")
_BELL_NAMES = (_("Gaus"), _("Lorentz"), _("Pseudo Voit"))
_data = {}


def introduce():
    """Entry point. Declares menu items."""
    p = (_("Diffractogram"),)
    pdr = PredefRefl(_data)
    mitems = [(p + (_("Find background..."),),
               Mcall(_data, 'calc_bg')),
              (p + (_("Calc. refl. shapes..."),),
               Mcall(_data, 'calc_reflexes')),
              (p + (_("Predefined reflexes..."),),
               pdr.call_grid)]
    for p, e in mitems:
        XrayData.actions[p] = e
    for i in _BELL_TYPES:
        XrayData.plotters["cryp" + i] = getattr(Cryplots, "p" + i)
    APP.settings.declare_section("Peaks")
    iget = APP.settings.get
    for n, v in _DEFAULTS.items():
        _data[n] = iget(n, v, "Peaks")


def terminate():
    iset = APP.settings.set
    for i in _DEFAULTS:
        iset(i, _data[i], "Peaks")


class Mcall:
    def __init__(self, data, action):
        self.__action = getattr(self, action)
        self.idat = data

    def __call__(self, xrd):
        self.data = xrd
        return self.__action()

    def calc_bg(self):
        dat = self.data
        plot = dat.UI
        dlgr = plot.input_dialog(_("Calculate background"), [
            (_("Sigma multiplier:"), self.idat["bg_sigmul"]),
            (_("Background poynom's range:"), self.idat["bg_polrang"]),
        ])
        if dlgr is not None:
            sigmul, deg = dlgr
            if self.data.x_units != "q":
                x = np.sin(self.data.theta)
                y = self.data.corr_intens
            else:
                x = self.data.qrange
                y = self.data.y_data
            self.idat["bg_polrang"] = deg
            self.idat["bg_sigmul"] = sigmul
            dat.extra_data["background"] = bgnd = calc_bg(x, y, deg, sigmul)[0]
            dat.extra_data["stripped"] = y - bgnd
            x_label = {"theta": "$\\theta$", "2theta": "$2\\theta$",
                       "q": "q", None: _("Unknown")}[dat.x_units]
            plt = {"plots": [
                {"x1": "x_data", "y1": "corr_intens"},
                {"x1": "x_data", "y1": "background"},
                {"x1": "x_data", "y1": "stripped"}],
                "x1label": x_label, "y1label": _("pps"),
                "x1units": dat.x_units}
            _name = _("Background")
            dat.remember_plot(_name, plt)
            plt = {"plots": [{"x1": "x_data", "y1": "stripped"}],
                   "x1label": x_label, "y1label": _("pps"),
                   "x1units": dat.x_units}
            _name = _("Stripped")
            dat.remember_plot(_name, plt)
            plot.draw(_name)

    def calc_reflexes(self):
        dat = self.data
        rv = calculate_reflexes(dat)
        if rv is None:
            return
        itms = rv["items"]
        dat.extra_data["crypbells"] = np.array(itms).reshape(len(itms) * 4)
        _name = _("Peak description")
        dat.remember_plot(_name, "cryp" + rv["shape"])
        dat.UI.draw(_name)


class PredefRefl:
    def __init__(self, gdata):
        self.gdata = gdata
        self.ispowder = False
        self.data = []
        self.from_user = None
        self.frame = None
        self.user_reset = None

    def __nonzero__(self):
        return len(self.data) > 0

    def clear_data(self, evt):
        self.data = []

    def get(self, update=True):
        if update and self.from_user is not None:
            self.set(self.from_user())
        return sorted(self.data)

    def append(self, data):
        resd = dict([(i[0], i) for i in self.data])
        for i in data:
            resd[i[0]] = tuple(i) + (False,)
        self.data = resd.values()
        self.data.sort()
        if self.user_reset is not None:
            self.user_reset(self.data[:])

    def set(self, data):
        self.data = sorted(data)

    def call_grid(self, evt):
        if self.frame is None:
            from v_powder_tbl import RefLocFrame
            self.frame = RefLocFrame(self.gdata, self)
            self.from_user = self.frame.get_refpos
            self.user_reset = self.frame.set_cells
        else:
            self.frame.Raise()

    def del_frame(self):
        self.frame = None
        self.from_user = None
        self.user_reset = None


def calculate_reflexes(idata):
    "Search reflexes shapes"
    plot = idata.UI
    if idata.x_units != "q":
        x = np.sin(idata.theta)
    else:
        x = idata.qrange
    try:
        stripped_y = idata.extra_data["stripped"]
    except KeyError:
        return
    sig2 = _data["bg_sigmul"]
    if idata.lambda2:
        l21 = idata.lambda2 / idata.lambda1
    else:
        l21 = None
    dreflexes = {}
    dreflexes["lambda"] = idata.lambda1
    I2 = idata.I2
    sigmin = _("Min. \u03c3:"), _data["refl_sigmin"]
    consig = _("Const. \u03c3"), _data["refl_consig"]
    mbells = _("Max. bells:"), _data["refl_mbells"]
    bell_t = _("Shape function:"), _BELL_NAMES, _data["refl_bt"]
    pts_mi = _("Ignore points:"), _data["refl_ptm"], 4
    bf = _("Believe factor:"), _data["refl_bf"]
    alg = 0  # TODO: select optimal algorithm
    algorithm = _("Algorithm:"), (_("alg 1"), _("alg 2")), alg
    rv = plot.input_dialog(_("Shapes of reflexes"), [
        sigmin, consig, mbells, bell_t, bf, pts_mi, algorithm])
    if rv is None:
        return
    sigmin, consig, mbells, bell_t, bf, pts_mi, algorithm = rv
    _data["refl_sigmin"] = sigmin
    _data["refl_consig"] = consig
    _data["refl_mbells"] = mbells
    _data["refl_bt"] = bell_t
    _data["refl_ptm"] = pts_mi
    _data["refl_bf"] = bf
    sects = refl_sects(x, stripped_y, sig2, bf)
    sects = [i for i in sects if len(i) > pts_mi]
    totreflexes = []
    totsigmas = []
    if algorithm == 1:
        apposs = [(i[0], i[3]) for i in idata["data"]["User refl"].get()]

    def progress(status):
        status["description"] = _("Calculating shapes of the reflexes...")
        lsec = len(sects)
        for i, sect in enumerate(sects):
            status["part"] = i / lsec
            if status.get("stop"):
                break
            rfd = ReflexDedect(sect, l21, I2)
            if algorithm == 0:
                reflexes, stdev = rfd.find_bells(sigmin, not consig,
                                                 mbells, _BELL_TYPES[bell_t])
            else:
                mi = sect[0][0]
                ma = sect[-1][0]
                pposs = [i for i in apposs if mi <= i[0] <= ma]
                posfxs = [i for i in range(len(pposs)) if pposs[i][1]]
                pposs = [i[0] for i in pposs]
                reflexes, stdev = rfd.find_bells_pp(_BELL_TYPES[bell_t],
                                                    pposs, posfxs)
            totreflexes.extend(reflexes)
            totsigmas.extend([stdev] * (len(totreflexes) - len(totsigmas)))
            rfd.x_ar = np.linspace(rfd.x_ar[0], rfd.x_ar[-1],
                                   len(rfd.x_ar) * 10)
            rfd.lambda21 = None
            for peak in reflexes:
                pv = np.array(peak)[:3]
        status["complete"] = True
    plot.bg_process(progress)
    dreflexes["shape"] = _BELL_TYPES[bell_t]
    dreflexes["items"] = [i + (j,) for i, j in zip(totreflexes, totsigmas)]
    return dreflexes


def reflexes_markup(reflexes):
    "makes reflexes description in wiki format"
    info = "\n== %s ==\n\n" % _("Reflexes description")
    rti = _BELL_TYPES.index(reflexes["shape"])
    info += "* %s: %s\n" % (_("Mode"), _BELL_NAMES[rti])
    info += "\n\n{|\n! x_{0}\n! d\n! h\n! %s\n! S\n! std\n" % \
        ("\u03c3", "\u03b3", "\u03b3")[rti]
    tbl = []
    wav = reflexes["lambda"]
    for i in reflexes["items"]:
        tbl.append("|-")
        tbl.append("| %s" % loc.format("%g", i[0]))
        tbl.append("| %s" % loc.format("%g", wav / 2. / i[0]))
        hght = i[1]
        if rti == 1:
            wdth = np.sqrt(i[2]) / wav
            area = hght * np.pi * wdth
        elif rti == 2:
            wdth = np.sqrt(i[2]) / wav / 2.
            area = hght * np.pi * wdth
        else:
            wdth = np.sqrt(i[2] / 2.) / wav
            area = hght * wdth * np.sqrt(2. * np.pi)
        tbl.append("| %s" % loc.format("%g", hght))
        tbl.append("| %s" % loc.format("%g", wdth))
        tbl.append("| %s" % loc.format("%g", area))
        tbl.append("| %s" % loc.format("%g", i[3]))
    tbl.append("|}")
    return info + "\n".join(tbl)
