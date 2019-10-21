#!/usr/bin/env python3
"""Wrap a GUI plot"""
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

from .menu import DMenu
from .mixins import DialogsMixin


class Plot(DialogsMixin):
    def __init__(self, name,
                 class_name=None, identifier=None):
        self.title = name
        self.identifier = identifier
        self.close_lock = None
        self.currently_alive = False
        self.gui_functions = {}
        self.icon = None
        self.class_name = class_name
        self.shortcuts = {}
        self.menu = DMenu()
        self.plots = {}

    def show(self):
        from ..application import get_actual_interface
        get_actual_interface().show_vi(self)

    def draw(self, pl_name):
        """Try to draw a plot"""
        try:
            self.gui_functions["draw"](self.plots[pl_name])
        except KeyError:
            pass

    def add_plot(self, pl_name, plt):
        """ adds plot with name, where plt is:
        {"plots": [{"type": "-" ("pulse" or MathPlotLib types),
        "color": None,
        "x1": Array(),
        "y1": Array(),
        "y2": Array() (optionally replaces y1)}],
        "x1label": "X axis title",
        "y1label": "Y axis title",
        "picker": None}"""
        self.plots[pl_name] = plt

    def set_close_lock(self, close_lock):
        self.close_lock = close_lock
        if "set_close_lock" in self.gui_functions:
            self.gui_functions["close_lock"](close_lock)

    def set_icon(self, icon):
        self.icon = icon
        if "set_icon" in self.gui_functions:
            self.gui_functions["set_icon"](icon)

    def add_shortcut(self, key, func):
        self.shortcuts[key] = func
        try:
            self.gui_functions["add_shortcut"](key, func)
        except KeyError:
            pass

    def __bool__(self):
        return self.currently_alive

    def __eq__(self, val):
        return self.identifier == val
