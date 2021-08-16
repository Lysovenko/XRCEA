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
"""
"""

import locale
import logging
from os.path import dirname, join, isdir, pardir
from argparse import ArgumentParser
from .application import APPLICATION
from .project import open_later
VERSION = "0.2.1"
RELEASE = '0.2'


def install_gt():
    try:
        if APPLICATION.modules[0] == ".stdio":
            raise RuntimeError()
        from gettext import install
        locale_dir = join(dirname(__file__), pardir, 'i18n', 'locale')
        if isdir(locale_dir):
            install('xrcea', locale_dir)
        else:
            install('xrcea')
    except (ImportError, RuntimeError):
        __builtins__["_"] = str


def parse_args():
    parser = ArgumentParser(description="XRC extensible analyzer")
    parser.add_argument("-v", "--verbose", dest="verbose", default=False,
                        action="store_true", help="be verbose")
    parser.add_argument('--debug', dest="debug", default=False,
                        action="store_true",
                        help="show debug messages")
    parser.add_argument("-c", "--console", dest="console", default=False,
                        action="store_true", help="run as command line")
    parser.add_argument('prjfile', help='Project file', nargs="?")
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    if args.prjfile:
        open_later(args.prjfile)
    if args.console:
        location, = [p for p, m in enumerate(APPLICATION.modules)
                     if m == ".stdio"]
        APPLICATION.modules.insert(0, APPLICATION.modules.pop(location))
    else:
        locale.setlocale(locale.LC_NUMERIC, "")


def initialize():
    parse_args()
    APPLICATION.compman.set_active()
    install_gt()
