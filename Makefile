gui: pyqt

pyqt:
	pyuic5 relational_gui/survey.ui > relational_gui/survey.py
	pyuic5 relational_gui/maingui.ui > relational_gui/maingui.py
	pyuic5 relational_gui/rel_edit.ui > relational_gui/rel_edit.py
	pyrcc5 relational_gui/resources.qrc > relational_gui/resources.py

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

dist: clean
	rm -rf /tmp/relational/
	rm -rf /tmp/relational-*
	mkdir /tmp/relational/
	cp -R * /tmp/relational/
	rm -rf /tmp/relational/windows
	rm -rf /tmp/relational/samples/.svn/
	rm -rf /tmp/relational/setup/.svn/
	rm -rf /tmp/relational/debscript/.svn/
	rm -rf /tmp/relational/mac/.svn/
	rm -rf /tmp/relational/relational/.svn/
	rm -rf /tmp/relational/relational_gui/.svn/
	rm -f /tmp/relational/relational_gui/survey.py
	rm -f /tmp/relational/relational_gui/maingui.py
	rm -f /tmp/relational/relational_gui/rel_edit.py
	rm -rf /tmp/relational/relational_pyside/.svn/
	rm -rf /tmp/relational/mac
	rm -rf /tmp/relational/debian/
	rm -rf /tmp/relational/relational_curses/.svn/
	rm -rf /tmp/relational/relational_readline/.svn/
	rm -rf /tmp/relational/test/.svn

	#mv /tmp/relational /tmp/relational-`./relational_gui.py -v | grep Relational | cut -d" " -f2`
	#(cd /tmp; tar -zcf relational.tar.gz relational-*/)
	(cd /tmp; tar -zcf relational.tar.gz relational/)
	mv /tmp/relational.tar.gz ./relational_`./relational_gui.py -v | grep Relational | cut -d" " -f2`.orig.tar.gz

clean:
	rm -rf `find -name "*~"` || echo ok
	rm -rf `find -name "*pyc"` || echo ok
	rm -rf `find -name "*pyo"` || echo ok
	rm -rf Relational.app || echo ok
	rm relational*.tar.gz || echo ok
	rm -rf relational_mac
	rm -rf data || echo ok
	rm -rf *tar.bz || echo ok
	rm -rf *.deb || echo ok
	rm -rf relational_mac

debian:
	dpkg-buildpackage
