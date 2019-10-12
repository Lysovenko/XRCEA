#!/usr/bin/env python
"""Operate with project file"""
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

from zipfile import ZipFile, ZIP_DEFLATED
try:
    from lxml.etree import fromstring, tostring
except ImportError:
    from xml.etree.ElementTree import fromstring, tostring


class Project:
    __TREATERS = {}

    def __init__(self, filename=None):
        self._compounds = []
        if filename:
            self.read(filename)

    @classmethod
    def add_treater(self, treater):
        assert treater.xmlroot not in self.__TREATERS
        self.__TREATERS[treater.xmlroot] = treater

    def save(self, filename):
        with ZipFile(filename, "w", compression=ZIP_DEFLATED) as zipf:
            for i, c in enumerate(self._compounds):
                xml = c.get_xml()
                try:
                    xml = tostring(xml, encoding="utf8", xml_declaration=True)
                except TypeError:
                    xml = tostring(xml, encoding="utf8")
                zipf.writestr("item%d" % i, xml)

    def read(self, filename):
        with ZipFile(filename, "r") as zipf:
            for i in zipf.namelist():
                xml = fromstring(zipf.read(i))
                try:
                    self._compounds.append(
                        self.__TREATERS[xml.tag]().from_xml(xml))
                except KeyError:
                    pass

    def add_compound(self, compound):
        if compound not in self._compounds:
            self._compounds.append(compound)

    def compounds(self):
        return iter(self._compounds)
