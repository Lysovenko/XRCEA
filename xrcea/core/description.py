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


class DescItem:
    pass


class Title(DescItem):
    def __init__(self, text, level):
        self.text = text
        self.level = level


class Paragraph(DescItem):
    def __init__(self, text=None):
        self.content = []
        if text is not None:
            self.content.append(text)

    def get_obj(self):
        par = {type: self.__name__}
        par["content"] = [i.get_obj() for i in self.content]
        return par

    def __iter__(self):
        return self.content.__iter__()

    def __getitem__(self, i):
        return self.content.__getitem__(i)

    def __len__(self):
        return self.content.__len__()


class Table(DescItem):
    def __init__(self):
        self.content = []

    def get_obj(self):
        par = {type: self.__name__}
        par["content"] = [i.get_obj() for i in self.content]
        return par

    def __iter__(self):
        return self.content.__iter__()

    def __getitem__(self, i):
        return self.content.__getitem__(i)

    def __len__(self):
        return self.content.__len__()


class Row(DescItem):
    def __init__(self):
        self.content = []

    def get_obj(self):
        par = {type: self.__name__}
        par["content"] = [i.get_obj() for i in self.content]
        return par

    def __iter__(self):
        return self.content.__iter__()

    def __getitem__(self, i):
        return self.content.__getitem__(i)

    def __len__(self):
        return self.content.__len__()


class Cell(DescItem):
    def __init__(self):
        self.content = []

    def get_obj(self):
        par = {type: self.__name__}
        par["content"] = [i.get_obj() for i in self.content]
        return par

    def __iter__(self):
        return self.content.__iter__()

    def __getitem__(self, i):
        return self.content.__getitem__(i)

    def __len__(self):
        return self.content.__len__()


class SubScript(DescItem):
    def __init__(self, text):
        self.text = text


class SuperScript(DescItem):
    def __init__(self, text):
        self.text = text
