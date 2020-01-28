"""the Application class"""
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

from importlib import import_module
from os.path import join, dirname, realpath, splitext, normcase
from .compman import CompMan
from .settings import Settings
from .vi.menu import DMenu
from .vi import input_dialog, print_error
from .project import Project, show_project, save_project_as, save_project

_ACTUAL_INTERFACE = None


class Application:
    """container for 'global variables'"""

    def __init__(self):
        self.menu = DMenu()
        self.prj_path = None
        self.settings = Settings()
        self.compman = CompMan(self)
        self.runtime_data = dict()
        self.on_start = [show_project]
        self.register_treater = Project.add_treater
        self._projects = {}
        self.register_opener = Opener.register_opener

    @property
    def visual(self):
        return _ACTUAL_INTERFACE

    def _add_project(self, prj):
        name = prj.name()
        i = 0
        while name in self.menu.get_container(self.prj_path):
            i += 1
            name = "{} ({})".format(prj.name(), i)
        self._projects[name] = prj
        self.menu.append_item(self.prj_path, name,
                              lambda x=prj: show_project(x), None)

    def forget_project(self, prj):
        names = [k for k, v in self._projects.items() if v is prj]
        for name in names:
            self._projects.pop(name)
            self.menu.remove_item(self.prj_path + (name,))

    def open_project(self, fname):
        pathes = dict(i.path for i in self._projects.values())
        if fname in pathes:
            show_project(pathes[fname])
            return
        try:
            prj = Project(fname)
        except FileNotFoundError:
            print_error(_("File not found"),
                        _("File %s is not found") % fname)
        except Exception:
            print_error(_("File damaged"),
                        _("File %s is damaged") % fname)
        self._add_project(prj)
        show_project(prj)

    def new_project(self):
        pars = input_dialog(_("New project"),
                            _("Project parameters"),
                            [(_("Name"), "New project")])
        if pars:
            name, = pars
            prj = Project()
            prj.name(name)
            self._add_project(prj)
            show_project(prj)


def draw_plot():
    # TODO: this is for test. Do not leave so.
    for desc in APPLICATION.compman.descriptions:
        try:
            getattr(desc["module"], "show_me")()
            return
        except (KeyError, AttributeError):
            pass
    from .vi import Plot
    APPLICATION.runtime_data["MainWindow"] = p = Plot("XRCEA")
    p.show()


def start():
    global _ACTUAL_INTERFACE
    _introduce_menu()
    _ACTUAL_INTERFACE = import_module(".qt", "core")
    _ACTUAL_INTERFACE.main()


def get_actual_interface():
    return _ACTUAL_INTERFACE


class Opener:
    _openers = {}
    _descriptions = {}

    @classmethod
    def register_opener(self, ext, how, descr):
        self._openers[ext] = how
        self._descriptions['*' + ext] = descr

    @classmethod
    def run_dialog(self):
        fname = APPLICATION.visual.ask_open_filename(
            _("Open file"), "", [
                (" ".join(self._descriptions.keys()),
                 _("All known files"))] + sorted(self._descriptions.items()))
        if fname is not None:
            ext = splitext(normcase(fname))[1]
            if ext not in self._openers:
                return
            self._openers[ext](fname)


APPLICATION = Application()


def icon_file(name):
    """Returns icon filename
    arguments:
    name - name of icon"""
    return join(
        dirname(dirname(realpath(__file__))),
        "data", "icons", name + ".png")


def _help():
    from webbrowser import open_new
    from os.path import abspath, isfile
    from .vi import print_error
    fname = abspath(join(dirname(dirname(
        __file__)), "doc", "html", "index.html"))
    if not (isfile(fname) and open_new(fname)):
        print_error(_("Help window"), _("Unable to open help page."))


def _introduce_menu():
    from .sett_dialogs import edit_components
    from .idata import introduce_input
    mappend = APPLICATION.menu.append_item
    _opts = _("&Options")
    _file = _("&File")
    _prj = _("Project")
    _hlp = _("&Help")
    mappend((), _file, {}, None)
    mappend((_file,), _prj, {}, None)
    APPLICATION.prj_path = prj_p = (_file, _prj)
    mappend(prj_p, _("Show"), show_project, None)
    mappend(prj_p, _("Save"), save_project, None)
    mappend(prj_p, _("Save as..."), save_project_as, None)
    mappend(prj_p, "separ", None, None)
    mappend((), _opts, {}, None)
    mappend((_opts,), _("Components..."),
            edit_components, None, None)
    mappend((_file,), _("&Open"), Opener.run_dialog, None, None,
            icon_file("open"))
    APPLICATION.menu.insert_item((), 99, _hlp, {}, None)
    mappend((_hlp,), _("Contents"), _help, None)
    APPLICATION.register_opener(".xrp", APPLICATION.open_project,
                                _("XRCEA projects"))
    introduce_input()
