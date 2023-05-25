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
    objtype = "description"

    def __init__(self, obj=None):
        self.document = []

    def get_obj(self):
        descr = {objtype: self.objtype}
        descr["document"] = [i if isinstance(i, dict) else i.get_obj()
                             for i in self.document]
        return rescr


class Paragraph:
    __name__ = "Paragraph"

    def __init__(self):
        self.content = []

    def get_obj(self):
        par = {type: self.__name__}
        par["content"] = [i.get_obj() for i in self.content]
        return par
