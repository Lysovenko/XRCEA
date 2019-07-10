#!/usr/bin/env python3
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

from core.application import APPLICATION
from numpy import sin, linspace, pi


def introduce():
    APPLICATION.on_start.append(draw_test)


def draw_test():
    p = APPLICATION.runtime_data["MainWindow"]
    x = linspace(0, pi * 2, 63)
    y = sin(x)
    pd = {"plots": [{"x1": x, "y1": y}], "x1label": "Bull", "y1label": "Shit"}
    p.add_plot("test", pd)
    print("Draw test")
    p.draw("test")


def terminate():
    return
