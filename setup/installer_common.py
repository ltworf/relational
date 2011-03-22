# -*- coding: utf-8 -*-
# Relational
# Copyright (C) 2008  Salvo "LtWorf" Tomaselli
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

def c_setup(name):
    setup(
        version='1.1',
        name=name,
        packages=(name,),
        author="Salvo 'LtWorf' Tomaselli",
        author_email='tiposchi@tiscali.it',
        maintainer="Salvo 'LtWorf' Tomaselli",
        maintainer_email='tiposchi@tiscali.it',
        url='http://galileo.dmi.unict.it/wiki/relational/',
        license='GPL3',
    )