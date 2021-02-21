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
"""
"""


from .plot import Plot
from .lister import Lister
from .page import Page
from .spreadsheet import Spreadsheet


def _actual():
    from ..application import get_actual_interface
    return get_actual_interface()


def input_dialog(title, question, fields, parent=None):
    """
    :param title: Title of the window.
    :type title: string
    :param question: Question to ask.
    :type question: string or None
    :param fields: List of tuples (name, value, [optional]).
    :type fields: list
    :param parent: Not used.
    :type parent: NoneType
    """
    return _actual().input_dialog(title, question, fields, parent)


def print_information(title, info):
    """
    :param title: Title of the window.
    :type title: string
    :param info: Information itself.
    :type info: string
    """
    return _actual().print_information(title, info)


def print_error(title, info):
    """
    :param title: Title of the window.
    :type title: string
    :param info: Information about error.
    :type info: string
    """
    return _actual().print_error(title, info)


def ask_question(title, question):
    """
    :param title: Title of the window.
    :type title: string
    :param question: A simple question.
    :type question: string
    """
    return _actual().ask_question(title, question)


def print_status(status):
    """
    :param status: Status to print into statusbar.
    :type status: string
    """
    return _actual().print_status(status)


def copy_to_clipboard(text):
    """
    :param text: Text to copy into clipboard.
    :type text: string
    """
    return _actual().copy_to_clipboard(text)


def register_dialog(dlg):
    """
    Send a dlg function to execution queue, which should be executed
    in GUI thread.

    :param dlg: Some function, which gets no parameters.
    :type dlg: callable
    """
    return _actual().register_dialog(dlg)


def ask_open_filename(title, filename, masks):
    return _actual().ask_open_filename(title, filename, masks)


def ask_save_filename(title, filename, masks):
    return _actual().ask_save_filename(title, filename, masks)


class Button:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, val):
        self.func(val)


def gui_exit():
    """
    Quit the GUI.
    """
    return _actual().gui_exit()
