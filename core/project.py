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
"""Operate with project file"""

from zipfile import ZipFile, ZIP_DEFLATED
from time import time
from os.path import splitext, isfile
try:
    from lxml.etree import fromstring, tostring, Element, SubElement
except ImportError:
    from xml.etree.ElementTree import fromstring, tostring, Element, SubElement
from .vi import (Lister, input_dialog, print_error, ask_open_filename,
                 ask_save_filename, ask_question)
from .vi.value import Value


def xml_string(xml):
    try:
        res = tostring(xml, encoding="utf8", xml_declaration=True)
    except TypeError:
        res = tostring(xml, encoding="utf8")
    return res


class Project:
    __TREATERS = {}

    def __init__(self, filename=None):
        self.path = filename
        self.UI = None
        self._components = []
        self._about = {"name": "New", "id": str(int(time()))}
        if filename:
            self.read(filename)

    @classmethod
    def add_treater(self, treater):
        assert treater.xmlroot not in self.__TREATERS
        self.__TREATERS[treater.xmlroot] = treater

    def _about_xml(self):
        about = Element("about")
        for k, v in self._about.items():
            SubElement(about, k).text = v
        return about

    def _about_from_xml(self, xml):
        assert xml.tag == "about"
        self._about.update((i.tag, i.text) for i in xml)

    def save(self, filename):
        with ZipFile(filename, "w", compression=ZIP_DEFLATED) as zipf:
            for i, c in enumerate(self._components):
                xml = c.get_xml()
                zipf.writestr("item%d" % i, xml_string(xml))
            zipf.writestr("about", xml_string(self._about_xml()))

    def read(self, filename):
        with ZipFile(filename, "r") as zipf:
            for i in filter(lambda x: x.startswith("item"), zipf.namelist()):
                xml = fromstring(zipf.read(i))
                try:
                    self._components.append(
                        self.__TREATERS[xml.tag]().from_xml(xml))
                except KeyError:
                    pass
            self._about_from_xml(fromstring(zipf.read("about")))

    def add_component(self, component):
        if component not in self._components:
            self._components.append(component)
            if self.UI:
                self.UI.update_components()

    def components(self):
        return iter(self._components)

    def name(self, name=None):
        if name is None:
            return self._about.get("name")
        self._about["name"] = str(name)

    def abouts(self):
        return self._about.items()


class vi_Project(Lister):
    def __init__(self, project):
        self.project = project
        abouts = Value(list)
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
        self.menu.append_item((), _("&Project"), {}, None)
        self.show()
        self.set_choicer(self.click_component, False, 1)

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

    def click_component(self, tup):
        component = tup[-1]
        if hasattr(component, "display"):
            component.display()

    def update_components(self):
        self.components.update([(c.type, c.name, None, c)
                                for c in self.project.components()])



_CURRENT_PROJECT = None
_CURRENT_FILE = ""


def show_project():
    global _CURRENT_PROJECT
    if _CURRENT_PROJECT is None and _CURRENT_FILE is not None:
        open_project(_CURRENT_FILE)
    if _CURRENT_PROJECT is None:
        pars = input_dialog(_("New project"),
                            _("Project parameters"),
                            [(_("Name"), "New project")])
        if pars:
            name, = pars
            _CURRENT_PROJECT = Project()
            _CURRENT_PROJECT.name(name)
        else:
            open_project()
            if _CURRENT_PROJECT is None:
                return
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
    if fname is None:
        fname = ask_open_filename(
            _("Open XRCEA project"), "",
            [("*.xrp", _("XRCEA project"))])
    if fname is None:
        return
    _CURRENT_PROJECT = Project(fname)
    _CURRENT_FILE = fname


def open_later(fname):
    global _CURRENT_FILE
    if isfile(fname):
        _CURRENT_FILE = fname
    else:
        print(f"{fname} does not exists")


def add_object(component):
    _CURRENT_PROJECT.add_component(component)
