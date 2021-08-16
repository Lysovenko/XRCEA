"""This is some interesting educational program"""
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

import os
from os.path import join, isdir, expanduser, normpath, isfile
from configparser import RawConfigParser


class Settings:
    def __init__(self):
        self.__config = RawConfigParser()
        self.items = self.__config.items
        if os.name == 'posix':
            aphom = expanduser("~/.config")
            if isdir(aphom):
                self.__app_home = join(aphom, "XRCEA")
            else:
                self.__app_home = expanduser("~/.XRCEA")
        elif os.name == 'nt':
            if isdir(expanduser("~/Application Data")):
                self.__app_home = expanduser("~/Application Data/XRCEA")
            else:
                self.__app_home = expanduser("~/XRCEA")
        else:
            self.__app_home = normpath(expanduser("~/XRCEA"))
        if isfile(self.__app_home):
            os.remove(self.__app_home)
        if not isdir(self.__app_home):
            os.mkdir(self.__app_home, 0o755)
        self.__config.read(self.get_home("XRCEA.cfg"))
        self.declare_section("PALETTE")
        self.__default_colors = {}

    def declare_section(self, section):
        if not self.__config.has_section(section):
            self.__config.add_section(section)

    def get(self, name, default=None, section='DEFAULT'):
        if not self.__config.has_option(section, name):
            return default
        if default is not None:
            deft = type(default)
        else:
            deft = str
        try:
            if deft is float:
                return self.__config.getfloat(section, name)
            if deft is int:
                return self.__config.getint(section, name)
            if deft is bool:
                return self.__config.getboolean(section, name)
            return deft(self.__config.get(section, name))
        except ValueError:
            print("Warning: cannot convert {} into {}".format(
                repr(self.__config.get(section, name)), deft.__name__))
            return default

    def get_color(self, name):
        if name is None:
            return
        if not self.__config.has_option("PALETTE", name):
            return self.__default_colors.get(name)
        return self.__config.get("PALETTE", name)

    def set(self, name, val, section='DEFAULT'):
        if not isinstance(val, str):
            val = repr(val)
        self.__config.set(section, name, val)

    def set_color(self, name, val):
        self.__config.set("PALETTE", name, val)

    def add_default_colors(self, colors):
        self.__default_colors.update(colors)

    def get_home(self, name=''):
        if name:
            return join(self.__app_home, name)
        return self.__app_home

    def save(self):
        with open(self.get_home("XRCEA.cfg"), "w") as fobj:
            self.__config.write(fobj)
