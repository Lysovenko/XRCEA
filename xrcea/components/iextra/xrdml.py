# XRCEA (C) 2025 Serhii Lysovenko
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
""" """

import xml.etree.ElementTree as etree
from xrcea.core.application import APPLICATION as APP
from xrcea.core.idata import XrayData


def open_xrdml(fname):
    """Open PANalytica X-ray data file"""
    xrd = XrayData(xrdml_obj(fname))
    if xrd:
        APP.add_object(xrd)
        xrd.display()


def xrdml_obj(fname):
    obj = {"objtype": "xrd"}

    tree = etree.parse(fname)
    root = tree.getroot()
    ns = {"xrd": root.tag[1:].split("}")[0]}
    try:
        obj["comment"] = "\n".join(
            i.text for i in root.find("xrd:comment", ns)
        )
    except TypeError:
        obj["comment"] = "No comments"
    try:
        sample = root.find("xrd:sample", ns)
        obj["name"] = sample.find("xrd:name", ns).text
    except (AttributeError, TypeError):
        obj["name"] = "No name"
    measurement = root.find("xrd:xrdMeasurement", ns)
    wavels = measurement.find("xrd:usedWavelength", ns)
    for par, tag in (
        ("lambda1", "kAlpha1"),
        ("lambda2", "kAlpha2"),
        ("lambda3", "kBeta"),
        ("I2", "ratioKAlpha2KAlpha1"),
        ("I3", "ratioKBetaKAlpha1"),
    ):
        try:
            obj[par] = float(wavels.find("xrd:" + tag, ns).text)
        except AttributeError:
            pass
    x_data = []
    scan = measurement.find("xrd:scan", ns)
    dpoints = scan.find("xrd:dataPoints", ns)
    for pos in dpoints.findall("xrd:positions", ns):
        if pos.get("axis") == "2Theta":
            start = float(pos.find("xrd:startPosition", ns).text)
            end = float(pos.find("xrd:endPosition", ns).text)
            obj["x_units"] = "2theta"
    pts = dpoints.find("xrd:intensities", ns).text
    y_data = list(map(int, pts.split()))
    step = (end - start) / (len(y_data) - 1.0)
    x_data = [start + i * step for i in range(len(y_data))]
    obj["x_data"] = x_data
    obj["y_data"] = y_data
    return obj
