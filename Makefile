default:
	echo "sorry, no default action"

uninstall:
	rm -rf /opt/relational
	rm -f /usr/local/bin/relational

install:
	mkdir /opt/relational
	cp -R relational relational_gui /opt/relational/
	cp relational_gui.py /opt/relational
	chmod -R 555 /opt/relational/
	echo "#!/bin/bash" > /usr/local/bin/relational
	echo "/opt/relational/relational_gui.py" >> /usr/local/bin/relational
	chmod 555 /usr/local/bin/relational


source: clean
	rm -rf /tmp/relational/
	mkdir /tmp/relational/
	cp -R * /tmp/relational/
	rm -rf /tmp/relational/samples/.svn/ /tmp/relational/debscript/.svn/ /tmp/relational/mac/.svn/ /tmp/relational/relational/.svn/ /tmp/relational/relational_gui/.svn/ /tmp/relational/mac /tmp/relational/debscript/
	echo "cd /tmp ; tar -jcvvf relational.tar.bz relational/" | bash
	mv /tmp/relational.tar.bz ./relational_`./relational_gui.py -v`.tar.bz

source_all: clean
	rm -rf /tmp/relational/
	mkdir /tmp/relational/
	cp -R * /tmp/relational/
	echo "cd /tmp ; tar -jcvvf relational.tar.bz relational/" | bash
	mv /tmp/relational.tar.bz ./relational_`./relational_gui.py -v`.tar.bz

clean:
	rm -rf *~ || echo ok
	rm -rf *.pyc *.pyo || echo ok
	rm -rf Relational.app || echo ok
	rm relational*.tar.gz || echo ok
	rm -rf relational_mac
	rm -rf data || echo ok
	rm -rf *tar.bz || echo ok
	rm -rf *.deb || echo ok
	rm -rf relational/*~ || echo ok
	rm -rf relational/*.pyc *.pyo || echo ok
	rm -rf relational_gui/*~ || echo ok
	rm -rf relational_gui/*.pyc *.pyo || echo ok
	rm -rf relational_mac
mac: app
	mkdir relational_mac || echo Exists
	mv Relational.app relational_mac
	mkdir relational_mac/samples || echo Exists
	cp samples/*csv relational_mac/samples
	tar -zcvvf relational_`./relational_gui.py -v`.tar.gz relational_mac/
	rm -rf relational_mac
app:
	mkdir -p Relational.app/Contents/Resources || echo Exists
	cp *py Relational.app/Contents/Resources
	mkdir -p Relational.app/Contents/Resources/relational || echo Exists
	cp  relational/*py Relational.app/Contents/Resources/relational
	mkdir -p Relational.app/Contents/Resources/relational_gui || echo Exists
	cp relational_gui/*py Relational.app/Contents/Resources/relational_gui
	cp mac/Info.plist mac/PkgInfo Relational.app/Contents
	mkdir -p Relational.app/Contents/MacOS || echo Exists
	cp mac/relational_gui mac/Python Relational.app/Contents/MacOS
	cp mac/PythonApplet.icns mac/__argvemulator_relational_gui.py Relational.app/Contents/Resources/

debian:    
	#Python files
	mkdir -p data/usr/share/python-support/relational/
	mkdir -p data/usr/share/python-support/relational/relational_gui
	mkdir -p data/usr/share/python-support/relational/relational
	cp *py data/usr/share/python-support/relational/
	cp relational/*py data/usr/share/python-support/relational/relational/
	cp relational_gui/*py data/usr/share/python-support/relational/relational_gui
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
	echo "relational ("`./relational_gui.py -v | cut -d. -f1`":"`./relational_gui.py -v`+SVN`svn update | cut -d" " -f3 | tr -d "."`") unstable; urgency=low" >> data/usr/share/doc/relational/changelog.Debian
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
	cp debscript/relational data/usr/bin/relational
	chmod a+x data/usr/bin/relational
	#desktop file
	mkdir -p data/usr/share/applications/
	cp debscript/relational.desktop data/usr/share/applications/
	mkdir -p data/DEBIAN
	#package description
	debscript/gencontrol.sh > data/DEBIAN/control
	#cp debscript/rules data/DEBIAN
	#Postrm file to remove optimized generated python files
	cp debscript/prerm data/DEBIAN/prerm
	cp debscript/postinst data/DEBIAN/postinst
	chmod 0755 data/DEBIAN/prerm data/DEBIAN/postinst
	su -c "chown -R root:root data/*; dpkg -b data/ relational.deb; rm -rf data/"
	cp relational.deb relational_`./relational_gui.py -v`+SVN`svn update | cut -d" " -f3 | tr -d "."`.deb
	rm -f relational.deb
