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

from zipfile import ZipFile
import xml.etree.ElementTree as etree
from xrcea.core.application import APPLICATION as APP
from xrcea.core.idata import XrayData


def open_rasx(fname):
    """Open Rigaku X-ray data file."""
    xrd = XrayData(rasx_obj(fname))
    if xrd:
        APP.add_object(xrd)
        xrd.display()


def rasx_obj(fname):
    obj = {"objtype": "xrd"}
    with ZipFile(fname, "r") as zf:
        sl = (
            zf.read("Data0/Profile0.txt")
            .decode(encoding="utf-8-sig")
            .splitlines()
        )
        x_data = []
        y_data = []
        for line in sl:
            x, y = line.split()[:2]
            x = float(x)
            y = int(y)
            x_data.append(x)
            y_data.append(y)
        obj["x_data"] = x_data
        obj["y_data"] = y_data
        tree = etree.fromstring(
            zf.read("Data0/MesurementConditions0.xml").decode()
        )
        gen = tree.find("GeneralInformation")
        name = gen.find("SampleName").text
        if not name:
            name = fname
        obj["name"] = name
        obj["comment"] = gen.find("Comment").text
        hwc = tree.find("HWConfigurations")
        xrg = hwc.find("XrayGenerator")
        obj["lambda1"] = float(xrg.find("WavelengthKalpha1").text)
        obj["lambda2"] = float(xrg.find("WavelengthKalpha2").text)
        obj["lambda3"] = float(xrg.find("WavelengthKbeta").text)
        scan = tree.find("ScanInformation")
        axis = scan.find("AxisName").text
        if axis == "TwoThetaTheta":
            obj["x_units"] = "2theta"
        if axis == "TwoTheta":
            obj["x_units"] = "theta"
    return obj
