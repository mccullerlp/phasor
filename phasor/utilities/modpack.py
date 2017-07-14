# -*- coding: utf-8 -*-
"""
Run after a notebook to generate a zip containing all python code not in any site-packages (custom script code)
"""
from __future__ import division, print_function, unicode_literals
import sys
import re
import tempfile
import os
from os import path
import shutil
import subprocess

def generate_modpack(fname = 'modpack.tar.gz'):
    site_packages_needed = set()
    collect_dir = tempfile.mkdtemp()
    for k, v in sys.modules.items():
        if v is not None:
            try:
                fpath = v.__file__
            except AttributeError:
                #print("HMM", k)
                continue
            if re.match(r'.*site-packages', fpath):
                site_packages_needed.add(k.split('.')[0])
                pass
            elif re.match(r'.*python\d\.\d', fpath):
                pass
            else:
                mod_root_file = sys.modules[k.split('.')[0]].__file__
                pkg_dir = path.dirname(path.dirname(mod_root_file))
                pkg_rel = path.relpath(fpath, pkg_dir)
                pkg_path_rel = path.split(pkg_rel)[0]
                fpbase, fpext = path.splitext(fpath)
                if fpext in ['.pyc', '.py']:
                    try:
                        os.makedirs(path.join(collect_dir, pkg_path_rel))
                    except os.error:
                        pass
                    if fpext != '.py' and path.exists(fpbase + '.py'):
                        shutil.copyfile(fpath, path.join(collect_dir, path.relpath(fpbase + '.py', pkg_dir)))
                    else:
                        shutil.copyfile(fpath, path.join(collect_dir, pkg_rel))
        else:
            #print(k, None)
            pass
    with open(path.join(collect_dir, "NEEDED_PACKAGES.TXT"), 'w') as F:
        for pkg in sorted(site_packages_needed):
            F.write(pkg + '\n')
    subprocess.call(['tar', '-cvvzhf', fname, '--directory', collect_dir, '.'])
    shutil.rmtree(collect_dir)
    return






