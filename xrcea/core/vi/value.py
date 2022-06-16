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


def lfloat(noless=None, nomore=None, default=0):
    """limited float"""
    if nomore is not None and noless is not None and nomore <= noless:
        raise ValueError("minimal value is more or equal than maximum")

    class efloat(float):
        def __new__(cls, value=default):
            if isinstance(value, str):
                value = atof(value)
            if value is None and noless is not None:
                value = noless
            if value is None and nomore is not None:
                value = nomore
            if noless is not None and value < noless or \
               nomore is not None and value > nomore:
                raise ValueError("value is not in range {0}:{1}".format(
                    noless, nomore))
            return float.__new__(cls, value)

        def __format__(self, spec):
            return loc.format_string('%' + spec, self)

        def __str__(self):
            return loc.str(self)
    return efloat


class TabCell:
    def __init__(self, value=None, foreground=None, background=None):
        self.value = value
        self.background = background
        self.foreground = foreground
        self.row = None
        self.col = None

    def __str__(self):
        return str(self.value)

    @property
    def edit(self):
        return str(self)


class Tabular:
    def __init__(self, rows=None,  # type: Optional[int]
                 colnames=None,    # type: Optional[List[String]]
                 coltypes=None     # type: Optional[List[Any]]
                 ):
        if rows is not None and cols is not None:
            self._data = [[None] * len(colnames)] * rows
        else:
            self._data = []
        self._coltypes = coltypes
        self._colnames = colnames
        if coltypes is not None and type(coltypes) is not type(colnames):
            raise RuntimeError("colnames and coltypes "
                               "should be the same type")
        try:
            if len(colnames) != len(coltypes):
                raise RuntimeError("colnames and coltypes "
                                   "should be the same length")
        except TypeError:
            pass
        self._updater = None

    def get(self, row, col):
        try:
            return self._data[row][col]
        except IndexError:
            return None

    def set(self, row, col, data):
        if isinstance(self._data[row][col], TabCell):
            self._data[row][col].value = data
            return
        try:
            value = self._coltypes[col](data)
        except TypeError:
            value = data
        except ValueError:
            value = None
        self._data[row][col] = value

    @property
    def rows(self):
        try:
            return len(self._data)
        except (TypeError, AttributeError):
            return 0

    @property
    def columns(self):
        try:
            return len(self._colnames)
        except TypeError:
            return 0

    def colname(self, column):
        try:
            return self._colnames[column]
        except (TypeError, IndexError):
            return f"col_{column}"

    def set_updater(self, updater):
        self._updater = updater

    def refresh(self):
        try:
            self._updater()
        except Exception:
            pass

    def insert_row(self, index: int,
                   row=None  # type: Optional[List[Any]]
                   ):
        if row is not None and len(row) != self.columns:
            raise RuntimeError(f"length of row is not appropriate "
                               "({len(row)} vs {self.columns})")
        if row is not None:
            row = list(row)
        try:
            self._data.insert(
                index, [None] * self.columns if row is None else row)
        except AttributeError:
            self._data = [[None] * self.columns if row is None else row]
        for i, c in enumerate(self._data[index]):
            try:
                c.col = i
            except AttributeError:
                pass
        for i, row in enumerate(self._data[index:], index):
            for c in row:
                try:
                    c.row = i
                except AttributeError:
                    pass
        self.refresh()

    def insert_column(self, index, colname, coltype=None):
        try:
            self._colnames.insert(index, colname)
            if self._coltypes is not None:
                self._coltypes.insert(index, coltype)
        except AttributeError:
            self._colnames = [colname]
            self._coltypes = [coltype]
        try:
            for i in self._data:
                if coltype is not None:
                    i.insert(index, coltype())
                else:
                    i.insert(index, None)
        except TypeError:
            self._data = []
        try:
            for i in range(len(self._data)):
                self._data[i][index].row = i
        except AttributeError:
            pass
        for row in self._data:
            for i, c in enumerate(row[index:], index):
                try:
                    c.col = i
                except AttributeError:
                    pass
        self.refresh()

    def remove_row(self, index):
        self._data.pop(index)
        for r in self._data[index:]:
            for c in r:
                try:
                    c.row -= 1
                except AttributeError:
                    pass
        self.refresh()

    def remove_rows(self, indexes=None):
        if indexes is None:
            self._data.clear()
        else:
            for index in sorted(indexes, reverse=True):
                self._data.pop(index)
            for r, dr in enumerate(self._data[index:], index):
                for c in dr:
                    try:
                        c.row = r
                    except AttributeError:
                        pass
        self.refresh()

    def remove_column(self, index):
        self._colnames.pop(index)
        if self._coltypes is not None:
            self._coltypes.pop(index)
        for row in self._data:
            row.pop(index)
            for c in row[index:]:
                try:
                    c.col -= 1
                except AttributeError:
                    pass
        self.refresh()

    def on_del_pressed(self, cells):
        for cell in cells:
            self.set(*cell, None)
