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
from os.path import join, dirname, realpath, splitext, normcase, isfile
from .compman import CompMan
from .settings import Settings
from .vi.menu import DMenu
from .vi import input_dialog, print_error
from .project import (Project, show_project, save_project_as, save_project,
                      add_object, PreventExit, rename_project, open_project)

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
        self.register_opener = Opener.register_opener
        self.add_object = add_object
        self.prevent_exit = PreventExit()
        self.modules = [".qt", ".stdio"]

    @property
    def visual(self):
        return _ACTUAL_INTERFACE


def start():
    global _ACTUAL_INTERFACE
    _introduce_menu()
    APPLICATION.settings.add_default_colors({"exp_dat": "black"})
    for module in APPLICATION.modules:
        try:
            _ACTUAL_INTERFACE = import_module(module, "xrcea.core")
            break
        except ImportError:
            pass
    _ACTUAL_INTERFACE.main()


def get_actual_interface():
    return _ACTUAL_INTERFACE


class Opener:
    _openers = {}
    _descriptions = {}

    @classmethod
    def register_opener(cls, ext, how, descr):
        cls._openers[ext] = how
        cls._descriptions['*' + ext] = descr

    @classmethod
    def run_dialog(cls):
        fname = APPLICATION.visual.ask_open_filename(
            _("Open file"), "", [
                (" ".join(cls._descriptions.keys()),
                 _("All known files"))] + sorted(cls._descriptions.items()))
        if fname is not None:
            ext = splitext(normcase(fname))[1]
            if ext not in cls._openers:
                return
            cls._openers[ext](fname)

    @classmethod
    def open_by_name(cls, fname: str):
        if isinstance(fname, str) and isfile(fname):
            ext = splitext(normcase(fname))[1]
            if ext not in cls._openers:
                return
            cls._openers[ext](fname)


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
    from locale import getlocale
    lang = {"uk": "ukr", "uk_UA": "ukr"}.get(getlocale()[0], "eng")
    fname = abspath(join(dirname(dirname(
        __file__)), "doc", lang, "html", "index.html"))
    if not (isfile(fname) and open_new(fname)):
        print_error(_("Help window"), _("Unable to open help page."))


def _introduce_menu():
    from .sett_dialogs import edit_components
    from .idata import introduce_input
    from .vi import gui_exit
    mappend = APPLICATION.menu.append_item
    _opts = _("&Options")
    _file = _("&File")
    _prj = _("Project")
    _hlp = _("&Help")
    mappend((), _file, {}, None)
    mappend((_file,), _prj, {}, None)
    APPLICATION.prj_path = prj_p = (_file, _prj)
    mappend(prj_p, _("Show"), show_project, None)
    mappend(prj_p, _("Rename..."), rename_project, None)
    mappend(prj_p, _("Save"), save_project, None)
    mappend(prj_p, _("Save as..."), save_project_as, None)
    mappend(prj_p, "separ", None, None)
    mappend(prj_p, _("Open..."), open_project, None)
    mappend((), _opts, {}, None)
    mappend((_opts,), _("Components..."),
            edit_components, None, None)
    mappend((_file,), _("&Open"), Opener.run_dialog, None, None,
            icon_file("open"))
    APPLICATION.menu.insert_item((_file,), 99, _("&Quit"), gui_exit, None)
    APPLICATION.menu.insert_item((), 99, _hlp, {}, None)
    mappend((_hlp,), _("Contents"), _help, None)
    introduce_input()


def main():
    from . import initialize
    initialize()
    start()
