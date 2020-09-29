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
"""Dialogs"""
from sys import stderr
from os.path import isfile, isdir


def print_error(title, info):
    print(f"ERROR: {title}\n{info}", file=stderr)


def print_information(title, info):
    print(f"INFO: {title}\n{info}")


def ask_question(title, info):
    print(f"QUESTION: {title}\n{info}")
    ans = input("Answer [yes]: ")
    return not ans or ans.lower()[0] in "yt1"


def ask_open_filename(title, filename, masks):
    print(f"WARNING: {title}\n{filename}\n{masks}\n", file=stderr)
    fname = input("File name: ")
    if isfile(fname):
        return fname


def ask_save_filename(title, filename, masks):
    print(f"WARNING: {title}\n{filename}\n{masks}\n", file=stderr)
    fname = input("File name: ")
    if isfile(fname):
        ans = input(f"File: {fname}\nexists. Overwrite? [no]: ")
        if not ans or ans.lower()[0] not in "yt1":
            return
    if isdir(fname):
        print(f"{fname} is directory")
        return
    return fname


def input_dialog(title, question, fields, parent=None):
    print(title)
    print(question)
    res = []
    try:
        for t in fields:
            n, v = t[:2]
            print(f"{n} [{v}]", end='')
            ans = input(" ")
            if isinstance(v, tuple):
                if not ans:
                    if len(t) > 2:
                        res.append(t[2])
                    else:
                        res.append(0)
                else:
                    i = int(ans)
                    if i <= 0 or i > len(v):
                        raise ValueError(f"{i} is not in range 1..{len(v)}")
                    res.append(i - 1)
            elif isinstance(v, bool):
                if not ans:
                    res.append(v)
                else:
                    res.append(ans.lower()[0] in "yt1")
            else:
                if not ans:
                    res.append(v)
                else:
                    res.append(type(v)(ans))
    except (ValueError, KeyboardInterrupt) as err:
        print(res, "aborted by:", err, file=stderr)
        return
    return res


class Dialogs:
    def __init__(self, vi_obj):
        self.vi_obj = vi_obj
        guf = self.vi_obj.gui_functions
        for fun in ("input_dialog", "print_information", "print_error",
                    "ask_question", "ask_save_filename", "ask_open_filename",
                    "bg_process"):
            guf[fun] = getattr(self, fun)

    def input_dialog(self, question, fields):
        return input_dialog(self.vi_obj.name, question, fields, self)

    def print_information(self, info):
        print_information(self.vi_obj.name, info)

    def print_error(self, info):
        print_error(self.vi_obj.name, info)

    def ask_question(self, question):
        ask_question(self.vi_obj.name, info)

    def ask_save_filename(self, filename, masks):
        ask_save_filename(self.vi_obj.name, filename, masks)

    def ask_open_filename(self, filename, masks):
        ask_open_filename(self.vi_obj.name, filename, masks)

    def bg_process(self, status: dict):
        from time import sleep
        status["start"]()
        prev = status["part"]
        print("Something is running...")
        while not status['complete']:
            sleep(1)
            if prev < status["part"]:
                print(status["part"], status["description"])
