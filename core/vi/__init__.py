#!/usr/bin/env python
"""start from here"""
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

from .plot import Plot
from .lister import Lister
from ..application import get_actual_interface


def new_frame(user_data, xml_file, frame_name):
    f = Frames(xml_file)
    puzzle = f.get(frame_name)
    puzzle.set_data(user_data)
    return get_actual_interface().new_frame(puzzle)


def run_dialog(user_data, xml_file, frame_name):
    f = Frames(xml_file)
    puzzle = f.get(frame_name)
    puzzle.set_data(user_data)
    return get_actual_interface().run_dialog(puzzle)


def input_dialog(*args, **kwargs):
    return get_actual_interface().input_dialog(*args, **kwargs)


def print_information(*args, **kwargs):
    return get_actual_interface().print_information(*args, **kwargs)


def print_error(*args, **kwargs):
    return get_actual_interface().print_error(*args, **kwargs)


def ask_question(*args, **kwargs):
    return get_actual_interface().ask_question(*args, **kwargs)


def print_status(*args, **kwargs):
    return get_actual_interface().print_status(*args, **kwargs)


def copy_to_clipboard(text):
    return get_actual_interface().copy_to_clipboard(text)


def register_dialog(dlg):
    return get_actual_interface().register_dialog(dlg)
