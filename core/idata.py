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
"""Input data"""

import numpy as np
try:
    from lxml.etree import Element, SubElement
except ImportError:
    from xml.etree.ElementTree import Element, SubElement
from os.path import basename
from json import loads, dumps
from .application import APPLICATION as APP, icon_file
from .vi import Plot


def introduce_input():
    """Introduce input"""
    APP.register_treater(XrayData)
    APP.register_opener(".xrd", open_xrd, _("Difractograms"))


class XrayData:
    """
    :param fname: Path to file with X-ray difraction data.
    :type fname: string
    """
    loaders = []
    actions = {}
    plotters = {}
    xmlroot = "xrd"
    type = _("Difractogram")

    def __init__(self, fname=None):
        self.__sample = None
        self.__dict = {}
        self.extra_data = {}
        self._saved_plots = {}
        self.UI = None
        for i in ("contains", "density", "x_data", "y_data",
                  # diffraction angle of monochromer
                  "alpha1", "alpha2", "name",
                  "x_units", "lambda1", "lambda2", "lambda3",
                  "I2", "I3"):
            setattr(self, i, None)
        if not XrayData.loaders:
            XrayData.loaders.append(XrayData.open_xrd)
        if fname is not None:
            self.open(fname)

    def __eq__(self, other):
        if not isinstance(other, np.ndarray):
            return False
        return ((self.x_data == other.x_data) ==
                (self.y_data == other.y_data)).all()

    def _from_dict(self, dct):
        self.__dict.update(dct)
        for i in ("lambda1", "lambda2", "lambda3", "alpha1", "alpha2",
                  "I2", "I3", "density"):
            try:
                setattr(self, i, float(dct[i]))
            except(ValueError, KeyError):
                pass
        if 'x_units' in dct:
            if dct['x_units'] in ['2theta', "theta", "q"]:
                self.x_units = dct['x_units']
            else:
                self.x_units = None
        if 'contains' in dct:
            try:
                self.contains = loads(dct['contains'])
            except Exception:
                self.contains = None
        if 'sample' in dct:
            self.__sample = dct['sample'].lower()
        if 'name' in dct:
            self.name = dct['name']

    @staticmethod
    def open_xrd(fname):
        """
        Open xrd file.

        :param fname: Path to xrd file.
        :type fname: string
        """
        arr = []
        odict = {}
        fobj = open(fname)
        with fobj:
            for line in fobj:
                line = line.strip()
                if line.startswith('#'):
                    n, p, v = (i.strip() for i in line[1:].partition(':'))
                    if p:
                        odict[n] = v
                    continue
                try:
                    x, y = map(float, line.split()[:2])
                    arr.append((x, y))
                except ValueError:
                    pass
        if arr:
            arr.sort()
            arr = np.array(arr)
            x = arr.transpose()[0]
            y = arr.transpose()[1]
        else:
            x, y = None, None
        return x, y, odict

    def open(self, fname):
        """
        Open file with X-ray data.

        :param fname: Path to file with X-ray data.
        :type fname: string
        """
        for loader in XrayData.loaders:
            try:
                x, y, dct = loader(fname)
            except IOError:
                return
            if all(i is not None for i in (x, y, dct)):
                self.x_data = x
                self.y_data = y
                self._from_dict(dct)
                if self.name is None:
                    self.name = basename(fname)

    def __bool__(self):
        return self.x_data is not None and self.y_data is not None

    @property
    def qrange(self):
        if not self:
            return None
        if self.x_units == "q":
            return self.x_data
        if self.x_units == "2theta":
            acoef = np.pi / 360.
        if self.x_units == "theta":
            acoef = np.pi / 180.
        K = 4. * np.pi / self.wavel
        return K * np.sin(self.x_data * acoef)

    @property
    def theta(self):
        if self.x_units == "q":
            return None
        if self.x_units == "2theta":
            acoef = np.pi / 360.
        elif self.x_units == "theta":
            acoef = np.pi / 180.
        return np.array(self.x_data) * acoef

    @property
    def two_theta(self):
        if self.x_units == "q":
            return None
        if self.x_units == "2theta":
            acoef = np.pi / 180.
        elif self.x_units == "theta":
            acoef = np.pi / 90.
        return np.array(self.x_data) * acoef

    def get_y(self):
        return self.y_data

    @property
    def corr_intens(self):
        """correct intensity"""
        Iex = self.y_data
        ang = self.two_theta
        if ang is None:
            return Iex
        if self.alpha1 is self.alpha2 is None:
            return Iex / (np.cos(ang) ** 2 + 1.) * 2.
        if self.alpha2 is None:
            c2a = np.cos(self.alpha1 * np.pi / 90.) ** 2
            return Iex / (c2a * np.cos(ang) ** 2 + 1.) * (1. + c2a)
        if self.alpha1 is None:
            c2a = np.cos(self.alpha2 * np.pi / 90.) ** 2
            return Iex / (c2a * np.cos(ang) ** 2 + 1.) * 2.
        c2a1 = np.cos(self.alpha1 * np.pi / 90.) ** 2
        c2a2 = np.cos(self.alpha2 * np.pi / 90.) ** 2
        return Iex / (c2a1 * c2a2 * np.cos(ang) ** 2 + 1.) * (1. + c2a1)

    def rev_intens(self, Icor):
        """reverse correct intensity"""
        ang = self.two_theta
        if self.alpha1 is self.alpha2 is None:
            return Icor / 2. * (np.cos(ang) ** 2 + 1.)
        if self.alpha2 is None:
            c2a = np.cos(2. * self.alpha1) ** 2
            return Icor * (c2a * np.cos(ang) ** 2 + 1.) / (1. + c2a)
        if self.alpha1 is None:
            c2a = np.cos(2. * self.alpha2) ** 2
            return Icor * (c2a * np.cos(ang) ** 2 + 1.) / 2.
        c2a1 = np.cos(2. * self.alpha1) ** 2
        c2a2 = np.cos(2. * self.alpha2) ** 2
        return Icor * (c2a1 * c2a2 * np.cos(ang) ** 2 + 1.) / (1. + c2a1)

    def restore_plots(self):
        plt = self.UI
        for n, p in sorted(self._saved_plots.items()):
            plt.add_plot(n, self.abstraction2plot(p))

    def abstraction2plot(self, abstr):
        if isinstance(abstr, str):
            try:
                return self.plotters[abstr](self)
            except KeyError:
                pass
        plt = dict(abstr)
        plt["plots"] = pplots = []
        for plot in abstr["plots"]:
            pplot = dict(plot)
            for axis in ("x1", "y1", "y2"):
                try:
                    dname = plot[axis]
                except KeyError:
                    continue
                try:
                    axdata = getattr(self, dname)
                except AttributeError:
                    try:
                        axdata = self.extra_data[dname]
                    except KeyError:
                        raise(RuntimeError(f"Incorrect dataname {dname}"))
                pplot[axis] = axdata
            pplots.append(pplot)
        return plt

    def remember_plot(self, name, plot):
        self._saved_plots[name] = plot
        self.UI.add_plot(name, self.abstraction2plot(plot))

    def make_plot(self):
        x_label = {"theta": "$\\theta$", "2theta": "$2\\theta$",
                   "q": "q", None: _("Unknown")}[self.x_units]
        return {"plots": [{"x1": self.x_data, "y1": self.y_data,
                           "color": "exp_dat"}],
                "x1label": x_label, "y1label": _("pps"),
                "x1units": self.x_units}

    def get_xml(self):
        """Convets X-ray data into XML."""
        xrd = Element(self.xmlroot)
        for i in ("density", "alpha1", "alpha2", "lambda1", "lambda2",
                  "lambda3", "I2", "I3", "contains", "name", "x_units"):
            v = getattr(self, i, None)
            if v is not None:
                SubElement(xrd, i).text = dumps(v)
        for i in ("x_data", "y_data"):
            v = getattr(self, i, None)
            if v is not None:
                SubElement(xrd, i).text = dumps(list(map(float, v)))
        if self.extra_data:
            e = SubElement(xrd, "extras")
            for n, v in self.extra_data.items():
                SubElement(e, "array", name=n).text = dumps(
                    list(map(float, v)))
        if self._saved_plots:
            SubElement(xrd, "SavedPlots").text = dumps(self._saved_plots)
        return xrd

    def from_xml(self, xrd):
        """Get X-ray data from XML."""
        assert xrd.tag == self.xmlroot
        for e in xrd:
            if e.tag in {"density", "alpha1", "alpha2", "lambda1", "lambda2",
                         "lambda3", "I2", "I3", "contains", "name", "x_units"}:
                setattr(self, e.tag, loads(e.text))
            if e.tag in {"x_data", "y_data"}:
                setattr(self, e.tag, np.array(loads(e.text)))
            if e.tag == "extras":
                for l in e:
                    if l.tag != "array":
                        continue
                    name = l.get("name")
                    if name is None:
                        continue
                    self.extra_data[name] = np.array(loads(l.text))
            if e.tag == "SavedPlots":
                self._saved_plots = loads(e.text)
        return self

    def display(self):
        """Display X-ray data as plot."""
        if not self:
            return
        if self.UI:
            plt = self.UI
        else:
            actions = type(self).actions
            self.UI = plt = Plot(self.name, "exp_plot")
            for mi in sorted(actions.keys()):
                args = actions[mi]
                if isinstance(args, tuple):
                    plt.menu.append_item(mi[:-1], mi[-1],
                                         lambda x=self, f=args[0]: f(x),
                                         *args[1:])
                else:
                    plt.menu.append_item(mi[:-1], mi[-1],
                                         lambda x=self, f=args: f(x))
            plt.add_plot("exp_data", self.make_plot())
        self.restore_plots()
        plt.show()
        plt.draw("exp_data")


def open_xrd(fname):
    """Open X-ray data file."""
    xrd = XrayData(fname)
    if xrd:
        APP.add_object(xrd)
        xrd.display()
