default:
	echo "sorry, no default action"

uninstall:
	rm -rf /opt/relational
	rm -f /usr/local/bin/relational
	rm -f /usr/share/applications/relational.desktop

install:
	mkdir /opt/relational
	cp -R relational relational_gui /opt/relational/
	cp relational_gui.py /opt/relational
	chmod -R 555 /opt/relational/
	echo "#!/bin/bash" > /usr/local/bin/relational
	echo "/opt/relational/relational_gui.py" >> /usr/local/bin/relational
	chmod 555 /usr/local/bin/relational
	cp relational.desktop /usr/share/applications/
	chmod a+r /usr/share/applications/relational.desktop

source: clean
	rm -rf /tmp/relational/
	mkdir /tmp/relational/
	cp -R * /tmp/relational/
	rm -rf /tmp/relational/windows /tmp/relational/samples/.svn/ /tmp/relational/debscript/.svn/ /tmp/relational/mac/.svn/ /tmp/relational/relational/.svn/ /tmp/relational/relational_gui/.svn/ /tmp/relational/mac /tmp/relational/debscript/ /tmp/relational/relational_curses/.svn/ /tmp/relational/relational_readline/.svn/
	echo "cd /tmp ; tar -zcvvf relational.tar.gz relational/" | bash
	mv /tmp/relational.tar.gz ./relational_`./relational_gui.py -v | grep Relational | cut -d" " -f2`.tar.gz

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
	tar -zcvvf relational_`./relational_gui.py -v | grep Relational | cut -d" " -f2`.tar.gz relational_mac/
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
	dpkg-buildpackage
