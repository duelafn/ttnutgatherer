#!/usr/bin/env python
"""
A game of collecting nuts, modeled off of the S'Quarrels Card Game by Home Lantern Games, LLC (http://www.squarrels.com/)
"""
# SPDX-License-Identifier: GPL-3.0

import os
import os.path
import re
import setuptools
import setuptools.command.build_py
import subprocess
import unittest

__version__ = re.search(r'(?m)^__version__\s*=\s*"([\d.]+(?:[\-\+~.]\w+)*)"', open('ttnutgatherer/__init__.py').read()).group(1)

def my_test_suite():
    return unittest.TestLoader().discover('tests', pattern='test_*.py')

def find(path, ext):
    rv = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(ext):
                 rv.append(os.path.join(root, file))
    return rv

class BuildPyCommand(setuptools.command.build_py.build_py):
    """Also build kivy .atlas file during build step."""
    def run(self):
        subprocess.run(["make", "ttnutgatherer/nuts.atlas"])
        setuptools.command.build_py.build_py.run(self)

setuptools.setup(
    cmdclass={
        'build_py': BuildPyCommand,
    },

    name         = 'nutgatherer',
    version      = __version__,
    url          = 'https://github.com/duelafn/nutgatherer',
    author       = 'Dean Serenevy',
    author_email = 'dean@serenevy.net',
    description  = "A game of collecting nuts, modeled off of the S'Quarrels Card Game by Home Lantern Games, LLC (http://www.squarrels.com/)",
    packages     = setuptools.find_packages(),
    install_requires = [
        "amethyst-core",
        "amethyst-games",
        "amethyst-ttkvlib",
        "kivy",
        ],
    scripts      = [ 'nutgatherer' ],
    test_suite   = 'setup.my_test_suite',
    data_files = [
        ('share/applications', find('extra', '.desktop')),
    ],
    include_package_data = True,
)
