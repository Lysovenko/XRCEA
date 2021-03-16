#!/usr/bin/env python3
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
"""Wrap a GUI listings"""


from .menu import DMenu
from .mixins import DialogsMixin


class Spreadsheet (DialogsMixin):
    def __init__(self, name, value,
                 class_name=None, identifier=None):
        self.name = name
        self.value = value
        self.choicer = None
        self.identifier = identifier
        self.close_lock = None
        self.currently_alive = False
        self.gui_functions = {}
        self.icon = None
        self.class_name = class_name
        self.shortcuts = {}
        self.menu = DMenu()

    def show(self):
        from ..application import get_actual_interface
        get_actual_interface().show_vi(self)

    def set_context_menu(self, list_context_menu):
        if "set_spreadsheet_context_menu" in self.gui_functions:
            self.gui_functions["set_spreadsheet_context_menu"](
                list_context_menu)

    def set_close_lock(self, close_lock):
        self.close_lock = close_lock
        if "set_close_lock" in self.gui_functions:
            self.gui_functions["close_lock"](close_lock)

    def set_icon(self, icon):
        self.icon = icon
        if "set_icon" in self.gui_functions:
            self.gui_functions["set_icon"](icon)

    def add_timer(self, seconds, func):
        try:
            self.gui_functions["add_timer"](seconds, func)
        except KeyError:
            raise RuntimeError("Show GUI before adding timer")

    def add_shortcut(self, key, func):
        self.shortcuts[key] = func
        try:
            self.gui_functions["add_shortcut"](key, func)
        except KeyError:
            pass

    def set_form(self, form, is_editable=True):
        """Sets fotrm. <form> is a list of tuples: (name/action, value)"""
        try:
            self.gui_functions["set_form"](form, is_editable)
        except KeyError:
            pass

    def get_form_values(self, which):
        """returns list of values"""
        try:
            return self.gui_functions["get_form_values"](which)
        except KeyError:
            return ()

    def get_selected_cells(self):
        """returns list of selected cells as (row, col) tuples"""
        try:
            return self.gui_functions["get_selected_cells"]()
        except KeyError:
            return ()

    def __bool__(self):
        return self.currently_alive

    def __eq__(self, val):
        return self.identifier == val
