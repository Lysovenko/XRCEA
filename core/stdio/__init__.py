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
"""Command line interpreter"""

from cmd import Cmd
from ..application import APPLICATION as APP, Opener
from .dialog import (
    print_error, print_information, ask_question, ask_open_filename,
    ask_save_filename, Dialogs)

_WIN_STACK = []


class Xrcmd(Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = "XRCEA> "
        self._components = APP.compman

    def do_EOF(self, line):
        """End Of File"""
        return True

    def do_load(self, line):
        """Load components by theit pathes"""
        pset = set(line.split())
        ids = set(d["id"] for d in self._components.descriptions
                  if d["path"] in pset)
        self._components.set_active(ids)
        self._components.introduce()

    def do_modules(self, line):
        """Show modules"""
        for d in self._components.descriptions:
            print(f"{d['path']}:\t{d['name']}")

    def do_open(self, line):
        """Open a file"""
        Opener.open_by_name(line)

    def do_menu(self, line):
        path = tuple(line.split("/"))
        last = dict(_WIN_STACK[-1].menu.get_items(path[:-1], APP.menu))
        mi = last.get(path[-1])
        if mi is not None and callable(mi.function):
            mi.function()


def main():
    xrcmd = Xrcmd()
    for e in APP.on_start:
        e()
    xrcmd.cmdloop()


def show_vi(vi_obj):
    """Do nothing"""
    vi_obj.gui_functions["set_choicer"] = lambda *args: None
    Dialogs(vi_obj)
    _WIN_STACK.append(vi_obj)
    print("\n".join(
        "/".join(p) for p, i in yield_menu(vi_obj.menu, APP.menu, ())))


def yield_menu(menu, other, path: tuple):
    for n, mi in menu.get_items(path, other):
        if isinstance(mi.function, dict):
            for i in yield_menu(menu, other, path + (n,)):
                yield i
        elif mi.function is not None:
            yield (path + (n,), mi.function)
