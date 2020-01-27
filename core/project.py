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
try:
    from lxml.etree import fromstring, tostring, Element, SubElement
except ImportError:
    from xml.etree.ElementTree import fromstring, tostring, Element, SubElement
from .vi import Lister, input_dialog, print_error
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
        self._about = {"name": _("New"), "id": str(int(time()))}
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
        components = Value(list)
        components.update([(c.type, c.name, None, c)
                          for c in project.components()])
        styles = {}
        super().__init__(project.name(),
                         [(_("About"), (_("Name"), "Value")),
                          (_("Components"), (_("Type"), _("Name")))],
                         [abouts, components], styles)
        self.menu.append_item((), _("&Project"), {}, None)
        self.show()
        self.set_choicer(self.click_component, False, 1)

    def click_component(self, tup):
        component = tup[-1]
        if hasattr(component, "display"):
            component.display()


_CURRENT_PROJECT = None


def show_project():
    global _CURRENT_PROJECT
    if _CURRENT_PROJECT is None:
        pars = input_dialog(_("New project"),
                            _("Project parameters"),
                            [(_("Name"), "New project")])
        if pars:
            name, = pars
            _CURRENT_PROJECT = Project()
            _CURRENT_PROJECT.name(name)
        else:
            return
    if _CURRENT_PROJECT.UI is None:
        _CURRENT_PROJECT.UI = vi_Project(_CURRENT_PROJECT)
    else:
        _CURRENT_PROJECT.UI.show()

