#!/usr/bin/env python3
"""Wrap a GUI ticket editor"""
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


class DialogsMixin:
    """Dialogs, called as children of widget"""
    def input_dialog(self, question, fields):
        try:
            return self.gui_functions["input_dialog"](question, fields)
        except KeyError:
            return

    def print_information(self, info):
        try:
            return self.gui_functions["print_information"](info)
        except KeyError:
            return

    def print_error(self, info):
        try:
            return self.gui_functions["print_error"](info)
        except KeyError:
            return

    def ask_question(self, question):
        try:
            return self.gui_functions["ask_question"](question)
        except KeyError:
            return

    def ask_save_filename(self, filename, masks):
        try:
            return self.gui_functions["ask_save_filename"](filename, masks)
        except KeyError:
            return

    def ask_open_filename(self, filename, masks):
        try:
            return self.gui_functions["ask_open_filename"](filename, masks)
        except KeyError:
            return
