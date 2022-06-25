# XRCEA (C) 2019-2020 Serhii Lysovenko
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

from typing import Dict, Union
import numpy as np
from os.path import basename, splitext
from json import loads, dumps
from .application import APPLICATION as APP, icon_file
from .vi import Plot, input_dialog


def introduce_input():
    """Introduce input"""
    APP.register_treater(XrayData)
    APP.register_opener(".xrd", open_xrd, _("Diffractograms"))
    APP.register_opener(".dat", open_xrd, _("Generic diffractograms"))


def _diff_props(xrd):
    ans = ask_about_sample(xrd.get_description())
    if isinstance(ans, dict):
        xrd.set_description(ans)


class XrayData:
    """
    :param fname: Path to file with X-ray diffraction data.
    :type fname: string
    """
    loaders = []
    actions = {(_("Diffractogram"), _("Properties...")): _diff_props}
    plotters = {}
    objtype = "xrd"
    type = _("Diffractogram")

    def __init__(self, obj=None):
        self.__sample = None
        self.__dict = {}
        self.extra_data = {}
        self._saved_plots = {}
        self.UIs = {}
        for i in ("contains", "density", "x_data", "y_data",
                  # diffraction angle of monochromer
                  "alpha1", "alpha2", "name",
                  "x_units", "lambda1", "lambda2", "lambda3",
                  "I2", "I3"):
            setattr(self, i, None)
        if not XrayData.loaders:
            XrayData.loaders.append(XrayData.open_xrd)
        if isinstance(obj, str):
            self.open(obj)
        elif isinstance(obj, dict):
            self.from_obj(obj)

    def __eq__(self, other):
        if not isinstance(other, np.ndarray):
            return False
        return (
            (self.x_data == other.x_data) == (self.y_data == other.y_data)
        ).all()

    def set_description(self, dct):
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

    def _emit_changed(self):
        try:
            self._container.element_changed(self)
        except AttributeError:
            pass

    def set_container(self, container):
        self._container = container

    def get_container(self):
        return self._container

    @classmethod
    def dummy_by_dialog(cls, assumption=None):
        if assumption is None:
            assumption = {}
        description = ask_about_sample(assumption)
        if description is None:
            return
        self = cls()
        self.set_description(description)
        return self

    @staticmethod
    def open_xrd(fname):
        """
        Open xrd or dat file.

        :param fname: Path to xrd or dat file.
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
        if not arr:
            return
        arr.sort()
        arr = np.array(arr)
        x = arr.transpose()[0]
        y = arr.transpose()[1]
        odict.setdefault("name", splitext(basename(fname))[0])
        if not {"sample", "x_units", "lambda1"}.issubset(odict):
            odict = ask_about_sample(odict)
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
            except (TypeError, ValueError):
                continue
            if all(i is not None for i in (x, y, dct)):
                self.x_data = x
                self.y_data = y
                self.set_description(dct)
                return

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
        else:  # self.x_units == "theta"
            acoef = np.pi / 180.
        coffee = 4. * np.pi / self.wavelength
        return coffee * np.sin(self.x_data * acoef)

    @property
    def theta(self):
        if self.x_units == "q":
            return None
        if self.x_units == "2theta":
            acoef = np.pi / 360.
        else:  # self.x_units == "theta"
            acoef = np.pi / 180.
        return np.array(self.x_data) * acoef

    @property
    def two_theta(self):
        acoef = 1.
        if self.x_units == "q":
            return None
        if self.x_units == "2theta":
            acoef = np.pi / 180.
        else:  # self.x_units == "theta"
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

    @property
    def wavelength(self):
        try:
            res = getattr(self, "lambda1")
            n = 1.
        except AttributeError:
            res = 0.
            n = 0.
        for i, j in (("lambda2", "I2"), ("lambda3", "I3")):
            try:
                n += getattr(self, j)
                res += (getattr(self, i) - res) * getattr(self, j) / n
            except (AttributeError, TypeError):
                pass
        return res

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
        plt = self.UIs.get("main")
        for n, p in sorted(self._saved_plots.items()):
            plot = self.abstraction2plot(p)
            if plot is not None:
                plt.add_plot(n, plot)

    def abstraction2plot(self, abstr: Union[str, Dict[str, Dict]]):
        """

        :type abstr: Union[str, Dict[str, Any]]
        """
        if isinstance(abstr, str):
            try:
                return self.plotters[abstr](self)
            except KeyError:
                return
        plt = dict(abstr)
        plt["plots"] = pplots = []
        plot: Dict[str, str]
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
                        raise(RuntimeError(f"Incorrect data name {dname}"))
                pplot[axis] = axdata
            pplots.append(pplot)
        return plt

    def remember_plot(self, name, plot):
        self._saved_plots[name] = plot
        self.UIs["main"].add_plot(name, self.abstraction2plot(plot))
        self._emit_changed()

    def make_plot(self):
        x_label = {"theta": "$\\theta$", "2theta": "$2\\theta$",
                   "q": "q", None: _("Unknown")}[self.x_units]
        return {"plots": [{"x1": self.x_data, "y1": self.y_data,
                           "color": "exp_dat"}],
                "x1label": x_label, "y1label": _("pps"),
                "x1units": self.x_units,
                "Comment": self.__dict.get("comment")}

    def get_description(self):
        items = ((i, getattr(self, i, None)) for i in (
            "density", "alpha1", "alpha2", "lambda1", "lambda2", "lambda3",
            "I2", "I3", "contains", "name", "x_units"))
        return {k: v for k, v in items if v is not None}

    def get_obj(self):
        """Convets X-ray data into object."""
        xrd = {"objtype": self.objtype}
        xrd.update(self.get_description())
        for i in ("x_data", "y_data"):
            v = getattr(self, i, None)
            if v is not None:
                try:
                    xrd[i] = v.tolist()
                except AttributeError:
                    xrd[i] = list(map(float, v))
        if self.extra_data:
            e = {}
            for n, v in self.extra_data.items():
                if not len(v):
                    continue
                if isinstance(v, np.ndarray):
                    e[n] = v.tolist()
                else:
                    e[n] = v
            if e:
                xrd["extras"] = e
        if self._saved_plots:
            xrd["SavedPlots"] = self._saved_plots
        return xrd

    def from_obj(self, xrd):
        """Get X-ray data from dict"""
        assert xrd["objtype"] == self.objtype
        for i in ("density", "alpha1", "alpha2", "lambda1", "lambda2",
                  "lambda3", "I2", "I3", "contains", "name", "x_units"):
            try:
                setattr(self, i, xrd[i])
            except KeyError:
                pass
        for i in ("x_data", "y_data"):
            setattr(self, i, np.array(xrd[i]))
        try:
            for n, v in xrd["extras"].items():
                nda = np.array(v)
                if nda.dtype.kind in 'if':
                    self.extra_data[n] = nda
                else:
                    self.extra_data[n] = v
        except (KeyError, TypeError):
            pass
        try:
            self._saved_plots.update(xrd["SavedPlots"])
        except (KeyError, TypeError):
            pass
        return self

    def display(self):
        """Display X-ray data as plot."""
        exp_data = _("Experimental data")
        if not self:
            return
        plt = self.UIs.get("main")
        if not plt:
            actions = type(self).actions
            self.UIs["main"] = plt = Plot(self.name, "exp_plot")
            for mi in sorted(actions.keys()):
                args = actions[mi]
                if isinstance(args, tuple):
                    plt.menu.append_item(mi[:-1], mi[-1],
                                         lambda x=self, f=args[0]: f(x),
                                         *args[1:])
                else:
                    plt.menu.append_item(mi[:-1], mi[-1],
                                         lambda x=self, f=args: f(x))
            plt.add_plot(exp_data, self.make_plot())
        self.restore_plots()
        plt.show()
        plt.draw(exp_data)


def open_xrd(fname):
    """Open X-ray data file."""
    xrd = XrayData(fname)
    if xrd:
        APP.add_object(xrd)
        xrd.display()


def ask_about_sample(sdict):
    """Ask some details about the sample"""
    # Lambda in Angstroms:
    # Cr, Co, Cu, Mo
    # According to the last re-examination of Holzer et al. (1997)
    #    Ka1      Ka2      Kb1
    ANODES = {"Cr": (2.289760, 2.293663, 2.084920, .506, .21),
              "Fe": (1.93604, 1.93998, 1.75661, .491, .182),
              "Co": (1.789010, 1.792900, 1.620830, .532, .191),
              "Cu": (1.540598, 1.544426, 1.392250, .46, .158),
              "Mo": (0.709319, 0.713609, 0.632305, .506, .233),
              "Ni": (1.65784, 1.66169, 1.50010, .476, .171),
              "Ag": (0.55936, 0.56378, 0.49701, .5, .2),
              "W": (0.208992, 0.213813, 0.18439, .5, .2)}
    danodes = tuple(sorted(ANODES.keys()))
    sett = APP.settings.get
    filterings = (_("Monochromed"), _("With %s-filter") % "\u03b2",
                  _("No filtering"))
    axes = ["2theta", "theta", "q"]
    daxes = ("2\u03b8", "\u03b8", "q: 4\u03c0 sin(\u03b8)/\u03bb")
    samples = ("powder", "liquid")
    dsamples = (_("Powder"), _("Liquid"))
    try:
        sample_guess = samples.index(sdict["sample"])
    except (IndexError, KeyError):
        sample_guess = sett("last_sample", 0)
    try:
        l1 = float(sdict["lambda1"])
        wls = np.array([ANODES[i][0] for i in danodes])
        anode_guess = int(np.square(wls - l1).argmin())
    except (KeyError, ValueError):
        anode_guess = sett("last_anode", 0)
    if "lambda1" in sdict:
        filter_guess = len([i for i in sdict.keys() if i.startswith("I")])
    else:
        filter_guess = sett("last_filtering", 0)
    try:
        axis_guess = axes.index(sdict["x_units"])
    except (IndexError, KeyError):
        axis_guess = sett("last_axis", 0)
    fields = [(_("Name:"), sdict.get("name", "")),
              (_("Sample:"), dsamples, sample_guess),
              (_("Anticatode:"), danodes, anode_guess),
              (_("Radiation:"), filterings, filter_guess),
              (_("X axis:"), daxes, axis_guess),
              (_("Comment:"), sdict.get("comment", ""))]
    question = ""
    if "question" in sdict:
        question = sdict["question"]
        fields.pop(0)
        fields.pop(-1)
    res = input_dialog(_("Sample description"), question, fields)
    if res is None:
        return
    name, sample, anode, filtering, xaxis, rem = \
        res if "question" not in sdict else [None] + res + [None]
    sett = APP.settings.set
    sett("last_sample", sample)
    sett("last_anode", anode)
    sett("last_filtering", filtering)
    sett("last_axis", xaxis)
    sdict["name"] = name
    sdict["comment"] = rem
    sdict["sample"] = samples[sample]
    sdict["x_units"] = axes[xaxis]
    anode = ANODES[danodes[anode]]
    if filtering == 0:
        sdict["lambda1"] = anode[0]
    elif filtering == 1:
        sdict["lambda1"] = anode[0]
        sdict["lambda2"] = anode[1]
        sdict["I2"] = anode[3]
    elif filtering == 2:
        sdict["lambda1"] = anode[0]
        sdict["lambda2"] = anode[1]
        sdict["lambda3"] = anode[2]
        sdict["I2"] = anode[3]
        sdict["I3"] = anode[4]
    return sdict
