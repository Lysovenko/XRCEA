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
from .reflex import calc_bg, refl_sects, ReflexDedect
_DEFAULTS = {"bg_sigmul": 2.0, "bg_polrang": 2, "refl_sigmin": 1e-3,
             "refl_consig": False, "refl_mbells": 10, "refl_bt": 0,
             "refl_ptm": 4, "refloc_sz": "(640,480)", "refl_bf": 2.}
_BELL_TYPES = ["Gaus", "Lorentz", "P-Voit"]
_BELL_NAMES = [_("Gaus"), _("Lorentz"), _("Pseudo Voit")]
_data = {}


def introduce():
    """Entry point. Declares menu items."""
    p = (_("Peak"),)
    pdr = PredefRefl(_data)
    mitems = [(p + (_("Find background..."),),
               Mcall(_data, 'calc_bg')),
              (p + (_("Calc. refl. shapes..."),),
               Mcall(_data, 'calc_reflexes')),
              (p + (_("Predefined reflexes..."),),
               pdr.call_grid)]
    for i in mitems:
        XrayData.actions[i[0]] = i[1]
    APP.settings.declare_section("Peaks")
    iget = APP.settings.get
    for n, v in _DEFAULTS.iteritems():
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
            sigmul, polrang = dlgr
            from formtext import poly1d2wiki
            dat["data"]["Background"], plts = dlg.calc_bg()
            if dat["data"]["Exp. data"].x_axis == "q":
                dat["the x units"] = x_units = "A^{-1}"
                x_title = r"$q,\,\AA^{-1}$"
            else:
                dat["the x units"] = x_units = 'sin(\\theta)'
                x_title = r'$\sin(\theta)$'
            pltn = _("Exp. background")
            pdat = dat['plot'].set_data(
                pltn, plts, x_title, _("I, rel. units"), x_units)
            pdat.tech_info['wavelength'] = dat["data"]["Exp. data"].wavel
            pdat.set_info(poly1d2wiki(dat["data"]["Background"][4]))
            dat['plot'].plot_dataset(pltn)
            dat['menu'].action_catch("bg found")

    def calc_reflexes(self):
        dat = self.data
        rv = calculate_reflexes(dat)
        if rv is None:
            return
        dat["data"]["Reflexes"], plts = rv
        pltn = _("Exp. reflexes")
        pdat = dat['plot'].set_data(
            pltn, plts, r'$\sin(\theta)$', _("I, rel. units"), 'sin(\\theta)')
        # set reflexes markup here
        pdat.set_info(reflexes_markup(dat["data"]["Reflexes"]))
        pdat.tech_info['wavelength'] = dat["data"]["Exp. data"].lambda1
        dat['plot'].plot_dataset(pltn)


class DlgPowBgCalc(wx.Dialog):
    "Missing docstring"
    def __init__(self, parent=None, data=None):
        self.data = data["data"]["Exp. data"]
        self.idat = data
        # GUI was here

    def calc_bg(self):
        plts = []
        if self.data:
            if self.data.x_axis != "q":
                x = np.sin(self.data.get_theta())
                y = self.data.corr_intens()
            else:
                x = self.data.get_qrange()
                y = self.data.get_y()
            sigmul = atof(self.sigmul_ea.GetValue())
            deg = self.bgpol_spin.GetValue()
            self.idat["bg_polrang"] = deg
            self.idat["bg_sigmul"] = sigmul
            self.bckgnd = (x, y) + calc_bg(x, y, deg, sigmul)
            plts.append((x, y, 1))
            plts.append((x, self.bckgnd[2], 1))
            plts.append((x, y - self.bckgnd[2], 1))
        return self.bckgnd, plts


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
    parent = idata["window"]
    exd = idata["data"]["Exp. data"]
    x, y, bg, sig2 = idata["data"]["Background"][:4]
    if exd.lambda2:
        l21 = exd.lambda2 / exd.lambda1
    else:
        l21 = None
    dreflexes = {}
    dreflexes["lambda"] = exd.lambda1
    I2 = exd.I2
    sigmin = _("Min. \u03c3:"), idata["refl_sigmin"]
    consig = _("Const. \u03c3"), idata["refl_consig"]
    mbells = _("Max. bells:"), idata["refl_mbells"]
    bell_t = _("Shape function:"), _BELL_NAMES, idata["refl_bt"]
    pts_mi = _("Ignore points:"), idata["refl_ptm"], 4
    bf = _("Believe factor:"), idata["refl_bf"]
    if idata["data"]["User refl"]:
        alg = 1
    else:
        alg = 0
    algorithm = _("Algorithm:"), [_("alg 1"), _("alg 2")], alg
    rv = v_input(parent, _("Shapes of reflexes"), sigmin, consig, mbells,
                 bell_t, bf, pts_mi, algorithm)
    if rv is None:
        return
    sigmin, consig, mbells, bell_t, bf, pts_mi, algorithm = rv
    idata["refl_sigmin"] = sigmin
    idata["refl_consig"] = consig
    idata["refl_mbells"] = mbells
    idata["refl_bt"] = bell_t
    idata["refl_ptm"] = pts_mi
    idata["refl_bf"] = bf
    sects = refl_sects(x, y, bg, sig2, bf)
    sects = [i for i in sects if len(i) > pts_mi]
    lsec = len(sects)
    titl = _("Calculate shapes")
    msg = _("Calculating shapes of the reflexes...")
    if lsec:
        dlgp = DlgProgressCallb(parent, titl, msg, lsec, can_abort=True)
    done = 0
    totreflexes = []
    totsigmas = []
    plts = []
    plts.append((x, y - bg, 1, 'black', '.'))
    if algorithm == 1:
        apposs = [(i[0], i[3]) for i in idata["data"]["User refl"].get()]
    for sect in sects:
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
        totreflexes += reflexes
        totsigmas += [stdev] * len(reflexes)
        plts.append((rfd.x_ar, rfd.y_ar - rfd.calc_shape(), 1,
                     'magenta', '-'))
        rfd.x_ar = np.linspace(rfd.x_ar[0], rfd.x_ar[-1], len(rfd.x_ar) * 10)
        plts.append((rfd.x_ar, rfd.calc_shape(), 1, 'green', '-'))
        rfd.lambda21 = None
        for peak in reflexes:
            pv = np.array(peak)[:3]
            plts.append((rfd.x_ar, rfd.calc_shape(pv), 1, 'b', '-'))
        done += 1
        if not dlgp(done):
            break
    dreflexes["shape"] = _BELL_TYPES[bell_t]
    dreflexes["items"] = [i + (j,) for i, j in zip(totreflexes, totsigmas)]
    return dreflexes, plts


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
