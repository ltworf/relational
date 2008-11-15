default:
	echo "sorry, no default action"

clean:
	rm *~ || echo ok
	rm *pyc || echo ok
	rm -rf Relational.app || echo ok
	rm -rf relational || echo ok
	rm relational*.tar.gz || echo ok
	rm -rf data || echo ok
	rm -rf *.deb || echo ok
mac: app
	mkdir relational || echo Exists
	mv Relational.app relational
	mkdir relational/samples || echo Exists
	cp samples/*tlb relational/samples
	tar -zcvvf relational_`./relational.py -v`.tar.gz relational/
app:
	mkdir Relational.app/ || echo Exists
	mkdir Relational.app/Contents || echo Exists
	mkdir Relational.app/Contents/Resources || echo Exists
	cp *py Relational.app/Contents/Resources
	cp mac/Info.plist mac/PkgInfo Relational.app/Contents
	mkdir Relational.app/Contents/MacOS || echo Exists
	cp mac/relational mac/Python Relational.app/Contents/MacOS
	cp mac/PythonApplet.icns mac/__argvemulator_relational.py Relational.app/Contents/Resources/

debian:    
	#Python files
	mkdir -p data/usr/share/python-support/relational/

	cp *py data/usr/share/python-support/relational/

	#man
	mkdir -p data/usr/share/man/man1
	cp relational.1 data/usr/share/man/man1
	gzip --best data/usr/share/man/man1/relational.1

	#doc
	mkdir -p data/usr/share/doc/relational

	echo "Copyright (C) 2008  Salvo "LtWorf" Tomaselli" >> data/usr/share/doc/relational/copyright
	echo "" >> data/usr/share/doc/relational/copyright
	echo "License:" >> data/usr/share/doc/relational/copyright
	echo "This program is under the GPLv3 license" >> data/usr/share/doc/relational/copyright

	cp CHANGELOG data/usr/share/doc/relational/changelog
	echo "relational ("`./relational.py -v | cut -d. -f1`":"`./relational.py -v`") unstable; urgency=low" >> data/usr/share/doc/relational/changelog.Debian
	echo "" >> data/usr/share/doc/relational/changelog.Debian
	echo "  * Automatically generated package, see changelog.gz" >> data/usr/share/doc/relational/changelog.Debian
	echo "" >> data/usr/share/doc/relational/changelog.Debian
	echo " -- Make <make@make.org>  Fri, 10 Oct 2008 19:18:35 +0200">> data/usr/share/doc/relational/changelog.Debian

	gzip --best data/usr/share/doc/relational/changelog.Debian
	gzip --best data/usr/share/doc/relational/changelog
	cp -r samples data/usr/share/doc/relational/examples
	rm -rf data/usr/share/doc/relational/examples/.svn

	#start script
	mkdir -p data/usr/bin
	echo "#!/bin/bash" >> data/usr/bin/relational
	echo "python /usr/share/python-support/relational/relational.py $@" >> data/usr/bin/relational
	chmod a+x data/usr/bin/relational
	
	#desktop file
	mkdir -p data/usr/share/applications/
	echo "[Desktop Entry]" >> data/usr/share/applications/relational.desktop
	echo "Name=Relational">> data/usr/share/applications/relational.desktop
	echo "Comment=Relational Algebra">> data/usr/share/applications/relational.desktop
	echo "Exec=relational">> data/usr/share/applications/relational.desktop
	echo "Icon=kexi">> data/usr/share/applications/relational.desktop
	echo "Terminal=0">> data/usr/share/applications/relational.desktop
	echo "Type=Application">> data/usr/share/applications/relational.desktop
	echo "Encoding=UTF-8">> data/usr/share/applications/relational.desktop
	echo "Categories=Education;">> data/usr/share/applications/relational.desktop
	
	mkdir -p data/DEBIAN
	#package description
	echo "Package: relational" >> data/DEBIAN/control
	echo "Version: "`./relational.py -v | cut -d. -f1`":"`./relational.py -v` >> data/DEBIAN/control
	echo "Architecture: all" >> data/DEBIAN/control
	echo "Maintainer: Salvo 'LtWorf' Tomaselli <tiposchi@tiscali.it>" >> data/DEBIAN/control
	echo "Installed-Size: "`du -bs --apparent-size data/ | cut -f1` >> data/DEBIAN/control
	echo "Depends: python-qt4 (>= 4.0.1-5), python (>= 2.3)" >> data/DEBIAN/control
	echo "Recommends: libqt4-webkit (>= 4.4.3-1)" >> data/DEBIAN/control
	echo "Section: devel" >> data/DEBIAN/control
	echo "Priority: optional" >> data/DEBIAN/control
	echo "Homepage: http://galileo.dmi.unict.it/wiki/relational/" >> data/DEBIAN/control
	echo "Description: Python implementation of Relational algebra.">> data/DEBIAN/control
	echo " This program provides a GUI to execute relational algebra queries.">> data/DEBIAN/control
	echo " It is meant to be used for educational purposes.">> data/DEBIAN/control
	su -c "chown -R root:root data/*; dpkg -b data/ relational.deb; rm -rf data/"
	cp relational.deb relational_`./relational.py -v`.deb
	rm -f relational.deb
	
	