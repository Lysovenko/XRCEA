#!/usr/bin/env python3
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
"""Wrap a GUI listings"""


from .menu import DMenu
from .mixins import DialogsMixin


class Lister (DialogsMixin):
    def __init__(self, name, titles, lvalues, styles={},
                 class_name=None, identifier=None):
        self.gui_functions = {}
        self.name = name
        self.styles = styles
        self.lvalues = lvalues
        self.choicer = None
        self.identifier = identifier
        self.close_lock = None
        self.currently_alive = False
        self.icon = None
        self.titles = titles
        self.class_name = class_name
        self.shortcuts = {}
        self.menu = DMenu()

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name_):
        if "set_name" in self.gui_functions:
            self.gui_functions["set_name"](name_)
        self.__name = name_

    def show(self):
        from ..application import get_actual_interface
        get_actual_interface().show_vi(self)

    def set_choicer(self, choicer, separate_items=False, holder=None):
        try:
            self.gui_functions["set_choicer"](choicer, separate_items, holder)
        except KeyError:
            raise RuntimeError("Show GUI before adding choicer")

    def set_list_context_menu(self, list_context_menu, holder=None):
        if "set_list_context_menu" in self.gui_functions:
            self.gui_functions["set_list_context_menu"](list_context_menu,
                                                        holder)

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

    def set_form(self, form, which=0, is_editable=True):
        """Sets fotrm. <form> is a list of tuples: (name/action, value)"""
        try:
            self.gui_functions["set_form"](form, which, is_editable)
        except KeyError:
            pass

    def get_form_values(self, which):
        """returns list of values"""
        try:
            return self.gui_functions["get_form_values"](which)
        except KeyError:
            return ()

    def __bool__(self):
        return self.currently_alive

    def __eq__(self, val):
        return self.identifier == val
