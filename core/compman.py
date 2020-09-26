""""This is the components manager"""
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

from sys import modules, path
from importlib import import_module
from os import listdir
from os.path import (dirname, realpath, split, splitext, join, isfile, exists,
                     isabs, normpath)
from weakref import ref

from typing import Dict


class CompMan:
    def __init__(self, app):
        """searches and reads components descriptions files"""
        self.application = ref(app)
        pth1 = join(dirname(dirname(realpath(__file__))), 'components')
        pth2 = app.settings.get_home("plugins")
        path.append(pth2)
        adds = []
        # find *.comp files
        for pth in (pth1, pth2):
            try:
                dir_lst = [i for i in listdir(pth) if i.endswith('.comp')]
            except FileNotFoundError:
                dir_lst = []
            appr = [join(pth, i) for i in dir_lst]
            # ensure that path is not directory or broken link
            adds += [i for i in appr if isfile(i)]
        descrs = []
        found_ids = set()
        for adf in adds:
            add_descr = {}  # type: Dict[AnyStr, AnyInt, ModuleType]
            # scanning *.comp file
            with open(adf) as fp:
                for line in fp:
                    ls = line.split('=', 1)
                    if len(ls) != 2:
                        continue
                    add_descr[ls[0]] = ls[1].strip()
            # validating the result of scanning
            if not set(add_descr).issuperset(('path', 'name', 'id')):
                continue
            d_id = add_descr['id']
            if d_id.isdigit():
                d_id = int(d_id)
                add_descr['id'] = d_id
            if d_id in found_ids:
                continue
            add_descr['keys'] = set(add_descr.get('keys', '').split())
            found_ids.add(d_id)
            descrs.append(add_descr)
        self.descriptions = sorted(descrs, key=lambda x: x['id'])

    def set_active(self, id_set=None):
        if id_set is None:
            id_set = self.application().settings.get("comps_ids", "{0}")
            try:
                id_set = set(map(int, id_set[1:-1].split(',')))
            except ValueError:
                id_set = set()
        for desc in self.descriptions:
            desc['isactive'] = desc['id'] in id_set

    def get_active(self, wgs=True):
        id_set = set()
        for desc in self.descriptions:
            if desc['isactive']:
                id_set.add(desc['id'])
        if wgs:
            self.application().settings.set("comps_ids", id_set)
        return id_set

    def introduce(self):
        """modules loader"""
        any_error = False
        for desc in self.descriptions:
            if desc['isactive'] and 'module' not in desc:
                pth, nam = split(splitext(desc["path"])[0])
                try:
                    if isinstance(desc["id"], int) and desc["id"] < 1000:
                        module = import_module("." + desc["path"],
                                               "components")
                    else:
                        module = import_module(desc["path"])
                except ImportError as err:
                    desc['isactive'] = False
                    any_error = True
                    print('ImportError: %s, %s' % (nam, err))
                    continue
                if not hasattr(module, 'introduce') or \
                        module.introduce():
                    desc['isactive'] = False
                    any_error = True
                    print("Error: `%s' can't be introduced" % pth)
                    modules.pop(module.__name__)
                    continue
                desc['module'] = module
        if any_error:
            self.get_active()
        return any_error

    def terminate(self, every=False):
        """modules unloader"""
        id_off = []
        for desc in self.descriptions:
            if 'module' in desc and (every or not desc['isactive']):
                module = desc.pop('module')
                if hasattr(module, 'terminate'):
                    module.terminate()
                modules.pop(module.__name__)
                id_off.append(desc['id'])
        return id_off


def mod_from_desc(desc):
    """module loader"""
    desc['isactive'] = True
    if 'module' not in desc:
        pth, nam = split(splitext(desc['path'])[0])
        try:
            fptr, pth, dsc = find_module(nam, [pth])
        except ImportError:
            desc['isactive'] = False
            print('ImportError: %s' % nam)
            return
        module = load_module(nam, fptr, pth, dsc)
        if fptr:
            fptr.close()
        if not hasattr(module, 'introduce') or \
                module.introduce():
            desc['isactive'] = False
            print("Error: `%s' can't be introduced" % pth)
            modules.pop(module.__name__)
            return
        desc['module'] = module
        return module
    return desc['module']
