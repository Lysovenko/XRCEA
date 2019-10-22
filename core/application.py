#!/usr/bin/env python
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
from .project import Project, vi_Project

_ACTUAL_INTERFACE = None


class Application:
    """container for 'global variables'"""

    def __init__(self):
        self.menu = DMenu()
        self.settings = Settings()
        self.compman = CompMan(self)
        self.runtime_data = dict()
        self.on_start = [draw_plot]
        self.register_treater = Project.add_treater
        self.projects = []
        self.register_opener = Opener.register_opener

    @property
    def visual(self):
        return _ACTUAL_INTERFACE

    def open_project(self, fname):
        self.projects.append(Project(fname))
        # just for test
        vi_Project(self.projects[-1])


def draw_plot():
    # TODO: this is for test. Do not leave so.
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
            _("Open file"), "", [(" ".join(self._descriptions.keys()),
                                 _("All known files"))] +
            sorted(self._descriptions.items()))
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


def _introduce_menu():
    from .sett_dialogs import edit_components
    from .idata import introduce_input
    mappend = APPLICATION.menu.append_item
    _edit = _("&Edit")
    _file = _("&File")
    mappend((), _file, {}, None)
    mappend((), _edit, {}, None)
    mappend((_edit,), _("Components..."),
            edit_components, None, None)
    mappend((_file,), _("&Open"), Opener.run_dialog, None, None,
            icon_file("open"))
    APPLICATION.register_opener(".xrp", APPLICATION.open_project,
                                _("XRCEA projects"))
    introduce_input()
