#!/usr/bin/env python3
"""Menu abstraction"""
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


class DMenuItem:
    def __init__(self, priority, name, function):
        self.priority = priority
        self.name = name
        self.function = function
        self.description = None
        self.icon = None
        self.shortcut = None


class DMenu:
    """Dynamic menu"""
    def __init__(self):
        self.root = {}

    def get_items(self, path, other=None):
        if other is not None:
            o_con = other.get_container(path, {})
        else:
            o_con = {}
        t_con = self.get_container(path, {})
        isec = set(t_con).intersection(o_con)
        uniq = set(t_con).symmetric_difference(o_con)
        rlist = [((t_con[i].priority + o_con[i].priority) / 2, i, t_con[i])
                 for i in isec]
        rlist += [(t_con[i].priority, i, t_con[i])
                  for i in uniq.intersection(t_con)]
        rlist += [(o_con[i].priority, i, o_con[i])
                  for i in uniq.intersection(o_con)]
        rlist.sort()
        return [i[1:] for i in rlist]

    def get_container(self, path, default=None):
        rcont = self.root
        for i, name in enumerate(path):
            try:
                rcont = rcont[name].function
            except KeyError:
                if default is None:
                    rcont = {}
                    self.append_item(path[:i - 1], path[i], rcont)
                else:
                    return default
        return rcont

    def insert_item(self, path, priority, name, function, shortcut,
                    description=None, icon=None):
        """inserts an item to the menu"""
        if isinstance(path, dict):
            cont = path
        else:
            cont = self.get_container(path)
        if name in cont:
            if isinstance(cont[name].function, dict) and \
               isinstance(function, dict):
                return
            raise RuntimeError("only submenu can be registred twice %s/%s"
                               % ("/".join(path), name))
        cont[name] = mi = DMenuItem(priority, name, function)
        mi.shortcut = shortcut
        mi.description = description
        mi.icon = icon

    def append_item(self, path, name, function, shortcut=None,
                    description=None, icon=None):
        """appends an item to the menu"""
        cont = self.get_container(path)
        if cont:
            priority = max(val.priority for val in cont.values()) + 1
        else:
            priority = 1
        self.insert_item(cont, priority, name, function, shortcut,
                         description, icon)

    def insert_item_after(self, path, name, function,
                          shortcut, description=None, icon=None):
        """inserts an item to the menu after the appointed item"""
        cont = self.get_container(path[:-1])
        priority = cont[path[-1]].priority
        gt = [val.priority for val in cont.values() if val.priority > priority]
        if gt:
            priority = (priority + min(gt)) / 2.
        else:
            priority += 1
        self.insert_item(cont, priority, name, function, shortcut,
                         description, icon)

    def insert_item_before(self, path, name, title, function,
                           shortcut, description=None, icon=None,
                           visibility="", action_catch=None):
        """inserts an item to the menu before the appointed item"""
        cont = self.get_container(path[:-1])
        priority = cont[path[-1]].priority
        lt = [val.priority for val in cont.values() if val.priority < priority]
        if lt:
            priority = (priority + max(lt)) / 2.
        else:
            priority -= 1
        self.insert_item(cont, priority, name, function, shortcut,
                         description, icon)

    def remove_item(self, path):
        """removes an item from the menu"""
        if not path:
            return
        cont = self.get_container(path[:-1])
        cont.pop(path[-1])
