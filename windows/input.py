# Relational
# Copyright (C) 2008-2020  Salvo "LtWorf" Tomaselli
#
# Relational is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>

from distutils.core import setup
import py2exe

#It was complaining about the already installed MSVCP90.dll
#So it is removed from the checks and signals to the user the
#probable need to manually install it. Since to redistribute it
#some dammit certificates are needed.

includes = (
    "sip",
    "PyQt5",
    "PyQt5.QtCore",
    "PyQt5.QtGui",
)

datafiles = (
    (
        "platforms", ["C:\\Python34\\Lib\\site-packages\\PyQt5\\plugins" + "\\platforms\\qwindows.dll"]
    ),
)

setup(
    data_files=datafiles,
    zipfile=None,
    options={
        "py2exe": {
            "includes": includes,
            "dll_excludes": ["MSVCP90.dll"],
        }
    },
    windows=[
        {
            "script": "relational.py",
            "icon_resources": [(0, "windows/favicon.ico")],
        }
    ],
    name="Relational",
    version="3.0",
)
