#!/usr/bin/env python3
"""Page: list and text area"""
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


class Page(DialogsMixin):
    def __init__(self, name, lvalue, colnames=None, styles={}, identifier=None,
                 choicer=None, list_context_menu=None):
        self.__name = name
        self.styles = styles
        self.lvalue = lvalue
        self.colnames = colnames
        self.__identifier = identifier
        self.close_lock = None
        self.currently_alive = False
        self.choicer = choicer
        self.list_context_menu = list_context_menu
        self.gui_functions = {}
        self.icon = None
        self.shortcuts = {}
        self.menu = DMenu()

    @property
    def id(self):
        return self.__identifier

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

    def set_choicer(self, choicer):
        if "set_choicer" in self.gui_functions:
            self.gui_functions["set_choicer"](choicer)
        self.choicer = choicer

    def set_list_context_menu(self, list_context_menu):
        if "set_list_context_menu" in self.gui_functions:
            self.gui_functions["set_list_context_menu"](list_context_menu)
        self.list_context_menu = list_context_menu

    def set_close_lock(self, close_lock):
        self.close_lock = close_lock
        if "set_close_lock" in self.gui_functions:
            self.gui_functions["close_lock"](close_lock)

    def set_icon(self, icon):
        self.icon = icon
        if "set_icon" in self.gui_functions:
            self.gui_functions["set_icon"](icon)

    def set_text(self, text, is_editable=False):
        try:
            self.gui_functions["set_text"](text, is_editable)
        except KeyError:
            pass

    def add_shortcut(self, key, func):
        # TODO: protect the shortcuts (and maybe others) by __
        # TODO: write initialization function, wihich wil be
        # called in show_ticket_editor (show_vi) and activate
        # set_list_context_menu, set_close_lock, set_icon, add_shortcut
        self.shortcuts[key] = func
        try:
            self.gui_functions["add_shortcut"](key, func)
        except KeyError:
            pass

    def set_form(self, form, is_editable=False):
        """Sets fotrm. <form> is a list of tuples: (name, value)"""
        try:
            self.gui_functions["set_form"](form, is_editable)
        except KeyError:
            pass

    def set_selected(self, index):
        """Set selected list item. int: index"""
        try:
            self.gui_functions["set_selected"](index)
        except KeyError:
            pass

    def get_html(self):
        try:
            return self.gui_functions["get_html"]()
        except KeyError:
            return ""

    def get_text(self):
        try:
            return self.gui_functions["get_text"]()
        except KeyError:
            return ""

    def scroll_down(self):
        try:
            return self.gui_functions["scroll_down"]()
        except KeyError:
            return

    def get_form_values(self):
        """returns list of values"""
        try:
            return self.gui_functions["get_form_values"]()
        except KeyError:
            return ()

    def is_active(self):
        """Checks if the window / frame is active"""
        try:
            return self.gui_functions["is_active"]()
        except KeyError:
            return

    def __bool__(self):
        return self.currently_alive

    def __eq__(self, val):
        return self.__identifier == val

    def __hash__(self):
        if isinstance(self.__identifier, (int, str)):
            return hash(self.__identifier)
        return super().__hash__()
