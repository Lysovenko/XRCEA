"""Share values with ui"""
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

from locale import atof
import locale as loc
try:
    type(unicode)
except NameError:
    unicode = str


class Value:
    def __init__(self, vclass):
        self.vclass = vclass
        self.value = vclass()
        self.relevance = True
        self.updater = None
        self.relevator = None

    def set_updater(self, updater):
        self.updater = updater

    def set_relevator(self, relevator):
        self.relevator = relevator

    def update(self, val, call_upd=True):
        self.value = self.vclass(val)
        if call_upd and self.updater is not None:
            try:
                self.updater(self.value)
            except Exception:
                pass

    def get(self):
        return self.value

    def is_relevant(self, relevance=None):
        if relevance is None:
            return self.relevance
        self.relevance = bool(relevance)
        if self.relevator is not None:
            self.relevator(self.relevance)

    def __str__(self):
        return self.value.__str__()

    def __int__(self):
        return self.value.__int__()

    def __float__(self):
        return self.value.__float__()


def lfloat(noless=None, nomore=None):
    "limited float"
    if nomore is not None and noless is not None and nomore <= noless:
        raise ValueError("minimal value is more or equal than maximum")

    class efloat(float):
        def __new__(self, value=0):
            if isinstance(value, (str, unicode)):
                value = atof(str(value))
            if value is None and noless is not None:
                value = noless
            if value is None and nomore is not None:
                value = nomore
            if noless is not None and value < noless or \
               nomore is not None and value > nomore:
                raise ValueError("value is not in range {0}:{1}".format(
                    noless, nomore))
            return float.__new__(self, value)

        def __format__(self, spec):
            return loc.format('%' + spec, self)

        def __str__(self):
            return loc.str(self)
    return efloat


class Tabular:
    def __init__(self, rows=None, cols=None, coltypes=None):
        if rows is not None and cols is not None:
            self._data = [[None] * cols] * rows
        self._coltypes = coltypes

    def get(self, row, col):
        try:
            return self._data[row][col]
        except IndexError:
            return None

    def set(self, row, col, data):
        try:
            self._data[row][col] = self._coltypes[col](data)
        except TypeError:
            self._data[row][col] = data
