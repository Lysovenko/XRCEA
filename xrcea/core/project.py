# XRCEA (C) 2019-2020 Serhii Lysovenko
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
"""Operate with project file"""

from zipfile import ZipFile, ZIP_DEFLATED
from time import time
from os.path import splitext, isfile
from json import loads, dumps
from .vi import (Lister, input_dialog, print_error, ask_open_filename,
                 ask_save_filename, ask_question)
from .vi.value import Value


class Project:
    __TREATERS = {}

    def __init__(self, filename=None):
        self.path = filename
        self.UI = None
        self._components = []
        self._about = {"name": "New", "id": str(int(time()))}
        self._content_modified = None
        if filename:
            self.read(filename)

    @classmethod
    def add_treater(self, treater):
        assert treater.objtype not in self.__TREATERS
        self.__TREATERS[treater.objtype] = treater

    def save(self, filename):
        with ZipFile(filename, "w", compression=ZIP_DEFLATED) as zipf:
            for i, c in enumerate(self._components):
                zipf.writestr("item%d" % i, dumps(c.get_obj()))
            zipf.writestr("about", dumps(self._about))
            self._content_modified = False
            try:
                self.UI.name = self.name()
            except AttributeError:
                pass

    def read(self, filename):
        with ZipFile(filename, "r") as zipf:
            for i in filter(lambda x: x.startswith("item"), zipf.namelist()):
                obj = loads(zipf.read(i))
                try:
                    self.add_component(
                        self.__TREATERS[obj["objtype"]](obj))
                except (KeyError, TypeError):
                    pass
            self._about.update(loads(zipf.read("about")))
        self._content_modified = False

    def add_component(self, component):
        if component not in self._components:
            self._components.append(component)
            if self.UI:
                self.UI.update_components()
            try:
                component.set_container(self)
            except AttributeError:
                pass
            self.element_changed(component)

    def remove_component(self, component):
        if component in self._components:
            self._components.remove(component)
            if self.UI:
                self.UI.update_components()
            self.element_changed(component)

    def components(self):
        return iter(self._components)

    def name(self, name=None):
        if name is None:
            return self._about.get("name")
        self._about["name"] = str(name)

    def abouts(self):
        return self._about.items()

    def element_changed(self, element):
        self._content_modified = True
        try:
            self.UI.modified()
        except AttributeError:
            pass

    def is_modified(self):
        return self._content_modified


class vi_Project(Lister):
    def __init__(self, project):
        self.project = project
        self.abouts = abouts = Value(list)
        abouts.update([i + (None,) for i in project.abouts()])
        self.components = components = Value(list)
        components.update([(c.type, c.name, None, c)
                          for c in project.components()])
        styles = {}
        self.__currently_alive = None
        super().__init__(project.name(),
                         [(_("About"), (_("Name"), "Value")),
                          (_("Components"), (_("Type"), _("Name")))],
                         [abouts, components], styles)
        self.show()
        self.set_choicer(self.click_component, False, 1)
        self.set_list_context_menu([(_("Delete"), self.del_component)], 1)

    @property
    def currently_alive(self):
        return self.__currently_alive

    @currently_alive.setter
    def currently_alive(self, cv):
        global _CURRENT_PROJECT
        if not cv:
            try:
                _CURRENT_PROJECT.UI = None
            except AttributeError:
                pass
        self.__currently_alive = cv

    @staticmethod
    def click_component(tup):
        component = tup[-1]
        if hasattr(component, "display"):
            component.display()
        component = tup[-1]

    def del_component(self, tup, c=None):
        component = tup[-1]
        self.project.remove_component(component)

    def update_components(self):
        self.components.update([(c.type, c.name, None, c)
                                for c in self.project.components()])

    def update(self):
        self.name = ("* " if self.project.is_modified() else "") + \
            self.project.name()
        self.abouts.update([i + (None,) for i in self.project.abouts()])
        self.update_components()

    def modified(self):
        self.name = "* " + self.project.name()


_CURRENT_PROJECT = None
_CURRENT_FILE = ""


def rename_project():
    pars = input_dialog(_("Rename project"),
                        _("New project name"),
                        [(_("Name"), _CURRENT_PROJECT.name())])
    if pars:
        name, = pars
        _CURRENT_PROJECT.name(name)
    if _CURRENT_PROJECT.UI:
        _CURRENT_PROJECT.UI.update()


def show_project():
    global _CURRENT_PROJECT
    if _CURRENT_PROJECT is None and _CURRENT_FILE != "":
        open_project(_CURRENT_FILE)
    if _CURRENT_PROJECT is None:
        _CURRENT_PROJECT = Project()
    if _CURRENT_PROJECT.UI is None:
        _CURRENT_PROJECT.UI = vi_Project(_CURRENT_PROJECT)
    else:
        _CURRENT_PROJECT.UI.show()


def save_project_as():
    global _CURRENT_FILE
    if _CURRENT_PROJECT is None:
        return
    fname = ask_save_filename(
        _("Save project"), _CURRENT_FILE,
        [("*.xrp", _("XRCEA project"))])
    if fname:
        if splitext(fname)[1] != ".xrp":
            fname += ".xrp"
        _CURRENT_PROJECT.save(fname)
        _CURRENT_FILE = fname


def save_project():
    if _CURRENT_FILE == "":
        return save_project_as()
    _CURRENT_PROJECT.save(_CURRENT_FILE)


def open_project(fname=None):
    global _CURRENT_PROJECT
    global _CURRENT_FILE
    previous = _CURRENT_PROJECT
    if previous is not None and previous.is_modified():
        if ask_question(_("Save project"),
                        _("""The %s project was changed.
Do you wish to save it before opening new?""" % previous.name())):
            save_project()
    if fname is None:
        fname = ask_open_filename(
            _("Open XRCEA project"), "",
            [("*.xrp", _("XRCEA project"))])
    if fname is None:
        return
    _CURRENT_PROJECT = Project(fname)
    _CURRENT_FILE = fname
    if getattr(previous, "UI", None):
        _CURRENT_PROJECT.UI = previous.UI
        _CURRENT_PROJECT.UI.project = _CURRENT_PROJECT
        _CURRENT_PROJECT.UI.update()


def open_later(fname):
    global _CURRENT_FILE
    if isfile(fname):
        _CURRENT_FILE = fname
    else:
        print(f"{fname} does not exists")


def add_object(component):
    _CURRENT_PROJECT.add_component(component)


class PreventExit:
    def __bool__(self):
        try:
            return bool(_CURRENT_PROJECT.is_modified())
        except AttributeError:
            return False

    def __str__(self):
        if self:
            return _("The \"%s\" project contains unsaved changes.") % \
                _CURRENT_PROJECT.name()
        return ""
