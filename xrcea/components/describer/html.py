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
Convert description to HTML
"""

from xml.etree.ElementTree import tostring, Element, SubElement
from xrcea.core.description import *


def _treat_paragraph(opar: Paragraph):
    hpar = Element("p")
    tailer = None
    for item in opar:
        if isinstance(item, DescItem):
            tailer = DESCITEMS[type(item)](item)
            hpar.append(tailer)
        else:
            if tailer is None:
                if hpar.text is None:
                    hpar.text = str(item)
                else:
                    hpar.text += str(item)
            else:
                if tailer.tail is None:
                    tailer.tail = str(item)
                else:
                    tailer.tail += str(item)
    return hpar


def _treat_table(otab: Table):
    htab = Element("table")
    for item in otab:
        assert isinstance(item, Row)
        htab.append(DESCITEMS[type(item)](item))
    return htab


def _treat_row(orow: Row):
    hrow = Element("tr")
    for item in orow:
        assert isinstance(item, Cell)
        hrow.append(DESCITEMS[type(item)](item))
    return hrow


def _treat_cell(ocell: Cell):
    hcell = Element("td")
    tailer = None
    for item in ocell:
        if isinstance(item, DescItem):
            tailer = DESCITEMS[type(item)](item)
            hcell.append(tailer)
        else:
            if tailer is None:
                if hcell.text is None:
                    hcell.text = str(item)
                else:
                    hcell.text += str(item)
            else:
                if tailer.tail is None:
                    tailer.tail = str(item)
                else:
                    tailer.tail += str(item)
    return hcell


def _treat_title(otitle: Title):
    htitle = Element("h%d" % (otitle.level,))
    htitle.text = otitle.text
    return htitle


def _treat_subscript(osub: SubScript):
    hsub = Element("sub")
    hsub.text = osub.text
    return hsub


def _treat_superscript(osup: SuperScript):
    hsup = Element("sup")
    hsup.text = osup.text
    return hsup


DESCITEMS = {Paragraph: _treat_paragraph, Title: _treat_title,
             Cell: _treat_cell, Row: _treat_row, Table: _treat_table,
             SubScript: _treat_subscript, SuperScript: _treat_superscript}


def _html_from_description(desc: Description):
    html = Element('html')
    head = SubElement(html, "head")
    SubElement(head, "title").text = desc.title
    SubElement(head, "style").text = "td {border: 1px solid;\n"\
        "padding: .4ex .7ex;}\n"\
        "table {border-collapse: collapse;}"
    doc = SubElement(html, 'body')
    for elem in desc:
        if isinstance(elem, DescItem):
            doc.append(DESCITEMS[type(elem)](elem))
    return tostring(html, encoding="unicode", method="html")


def write_html(descr, filename):
    """Write description as HTML"""
    with open(filename, "w") as file:
        file.write(_html_from_description(descr))
