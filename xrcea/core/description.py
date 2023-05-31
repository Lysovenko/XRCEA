# XRCEA (C) 2023 Serhii Lysovenko
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
Description of results and provided actions.
"""
from locale import format_string


class Description:

    def __init__(self):
        self.document = []
        self.title = "Hello, world!"

    def __iter__(self):
        return self.document.__iter__()

    def __getitem__(self, i):
        return self.document.__getitem__(i)

    def __len__(self):
        return self.document.__len__()

    def append(self, val):
        self.document.append(val)

    write = append


class DescItem:
    def __init__(self):
        self.content = []

    def __iter__(self):
        return self.content.__iter__()

    def __getitem__(self, i):
        return self.content.__getitem__(i)

    def __len__(self):
        return self.content.__len__()

    def write(self, data):
        self.content.append(data)


class Title(DescItem):
    def __init__(self, text, level):
        self.text = text
        self.level = level


class Paragraph(DescItem):
    def __init__(self, text=None):
        super().__init__()
        if text is not None:
            self.write(text)


class Table(DescItem):
    pass


class Row(DescItem):
    pass


class Cell(DescItem):
    def __init__(self, value=None, digits=None):
        super().__init__()
        if isinstance(value, str):
            self.write(value)
        elif isinstance(value, int):
            self.number = value
            self.write(str(value))
        elif isinstance(value, float):
            self.number = value
            if digits is None:
                self.write(format_string("%G", value))
            else:
                self.write(format_string("%%.%dG" % digits, value))


class SubScript(DescItem):
    def __init__(self, text):
        self.text = text


class SuperScript(DescItem):
    def __init__(self, text):
        self.text = text
