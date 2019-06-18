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
from .compman import CompMan
from .settings import Settings
from .menu import DMenu
from .frameparser import Frames

_ACTUAL_INTERFACE = None


class Application:
    """container for 'global variables'"""

    def __init__(self):
        self.menu = DMenu()
        self.settings = Settings()
        self.compman = CompMan(self)
        self.runtime_data = dict()
        self.on_start = [draw_plot]


def draw_plot():
    # TODO: this is for test. Do not leave so.
    from .vi import Plot
    p = Plot("test")
    p.show()


def start():
    global _ACTUAL_INTERFACE
    _introduce_menu()
    _ACTUAL_INTERFACE = import_module(".qt", "core")
    _ACTUAL_INTERFACE.main()


def new_frame(user_data, xml_file, frame_name):
    f = Frames(xml_file)
    puzzle = f.get(frame_name)
    puzzle.set_data(user_data)
    return _ACTUAL_INTERFACE.new_frame(puzzle)


def run_dialog(user_data, xml_file, frame_name):
    f = Frames(xml_file)
    puzzle = f.get(frame_name)
    puzzle.set_data(user_data)
    return _ACTUAL_INTERFACE.run_dialog(puzzle)


def show_vi(vi_obj):
    return _ACTUAL_INTERFACE.show_vi(vi_obj)


def input_dialog(*args, **kwargs):
    return _ACTUAL_INTERFACE.input_dialog(*args, **kwargs)


def print_information(*args, **kwargs):
    return _ACTUAL_INTERFACE.print_information(*args, **kwargs)


def print_error(*args, **kwargs):
    return _ACTUAL_INTERFACE.print_error(*args, **kwargs)


def ask_question(*args, **kwargs):
    return _ACTUAL_INTERFACE.ask_question(*args, **kwargs)


def print_status(*args, **kwargs):
    return _ACTUAL_INTERFACE.print_status(*args, **kwargs)


def copy_to_clipboard(text):
    return _ACTUAL_INTERFACE.copy_to_clipboard(text)


def register_dialog(dlg):
    return _ACTUAL_INTERFACE.register_dialog(dlg)


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
    mappend = APPLICATION.menu.append_item
    _edit = _("&Edit")
    mappend((), _("&File"), {}, None)
    mappend((), _edit, {}, None)
    mappend((_edit,), _("Components..."),
            edit_components, None, None)
