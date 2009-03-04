#!/bin/bash
	echo "Package: relational"
	echo "Version: "`./relational_gui.py -v | cut -d. -f1`":"`./relational_gui.py -v`+SVN`svn update | cut -d" " -f3 | tr -d "."`
	echo "Architecture: all"
	echo "Maintainer: Salvo 'LtWorf' Tomaselli <tiposchi@tiscali.it>"
	echo "Installed-Size: "`du -s --apparent-size data/ | cut -f1`
	echo "Depends: python-qt4 (>= 4.0.1-5), python (>= 2.3), ttf-dejavu-core (>= 2.25-3)"
	echo "Recommends: libqt4-webkit (>= 4.4.3-1)"
	echo "Section: devel"
	echo "Priority: optional"
	echo "Homepage: http://galileo.dmi.unict.it/wiki/relational/"
	echo "Description: Python implementation of Relational algebra."
	echo " This program provides a GUI to execute relational algebra queries."
	echo " It is meant to be used for educational purposes."
echo ""
echo ""
