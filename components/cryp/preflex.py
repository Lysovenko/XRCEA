# XRCEA (C) 2021 Serhii Lysovenko
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


class PredefRefl:
    def __init__(self, gdata):
        self.gdata = gdata
        self.ispowder = False
        self.data = []
        self.from_user = None
        self.frame = None
        self.user_reset = None

    def __nonzero__(self):
        return len(self.data) > 0

    def clear_data(self, evt):
        self.data = []

    def get(self, update=True):
        if update and self.from_user is not None:
            self.set(self.from_user())
        return sorted(self.data)

    def append(self, data):
        resd = dict([(i[0], i) for i in self.data])
        for i in data:
            resd[i[0]] = tuple(i) + (False,)
        self.data = resd.values()
        self.data.sort()
        if self.user_reset is not None:
            self.user_reset(self.data[:])

    def set(self, data):
        self.data = sorted(data)

    def call_grid(self, evt):
        if self.frame is None:
            from v_powder_tbl import RefLocFrame
            self.frame = RefLocFrame(self.gdata, self)
            self.from_user = self.frame.get_refpos
            self.user_reset = self.frame.set_cells
        else:
            self.frame.Raise()

    def del_frame(self):
        self.frame = None
        self.from_user = None
        self.user_reset = None
