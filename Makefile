gui: pyqt

pyqt:
	pyuic5 relational_gui/survey.ui > relational_gui/survey.py
	pyuic5 relational_gui/maingui.ui > relational_gui/maingui.py
	pyuic5 relational_gui/rel_edit.ui > relational_gui/rel_edit.py
	pyrcc5 relational_gui/resources.qrc > relational_gui/resources.py
	sed -i '' 's/QtWidgets.QPlainTextEdit/editor.Editor/g' relational_gui/maingui.py
	echo 'from . import editor' >> relational_gui/maingui.py

test:
	./driver.py

dist: clean
	rm -rf /tmp/relational/
	rm -rf /tmp/relational-*
	mkdir /tmp/relational/
	cp -R * /tmp/relational/
	rm -rf /tmp/relational/windows
	rm -rf /tmp/relational/debian/

	#mv /tmp/relational /tmp/relational-`./relational_gui.py -v | grep Relational | cut -d" " -f2`
	#(cd /tmp; tar -zcf relational.tar.gz relational-*/)
	(cd /tmp; tar -zcf relational.tar.gz relational/)
	mv /tmp/relational.tar.gz ./relational_`./relational_gui.py -v | grep Relational | cut -d" " -f2`.orig.tar.gz

release: dist
	gpg --sign --armor --detach-sign ./relational_`./relational_gui.py -v | grep Relational | cut -d" " -f2`.orig.tar.gz

clean:
	rm -rf `find -name "*~"`
	rm -rf `find -name "*pyc"`
	rm -rf `find -name "*pyo"`
	rm -rf relational*.tar.gz
	rm -rf relational*.tar.gz.asc
	rm -rf data
	rm -rf *tar.bz
	rm -rf *.deb
	rm -f relational_gui/survey.py
	rm -f relational_gui/maingui.py
	rm -f relational_gui/rel_edit.py
	rm -f relational_gui/resources.py

install-relational-cli:
	python3 setup/relational-cli.setup.py install --root=$${DESTDIR:-/};
	rm -rf build;
	install -D relational_gui.py $${DESTDIR:-/}/usr/bin/relational-cli
	install -D relational-cli.1 $${DESTDIR:-/}/usr/share/man/man1/relational-cli.1

install-python3-relational:
	python3 setup/python3-relational.setup.py install --root=$${DESTDIR:-/};
	rm -rf build;

install-relational:
	python3 setup/relational.setup.py install --root=$${DESTDIR:-/};
	rm -rf build;
	install -D relational_gui.py $${DESTDIR:-/}/usr/bin/relational
	install -m0644 -D relational.desktop $${DESTDIR:-/}/usr/share/applications/relational.desktop
	install -m0644 -D relational_gui/resources/relational.png $${DESTDIR:-/}/usr/share/pixmaps/relational.png
	install -D relational.1 $${DESTDIR:-/}/usr/share/man/man1/relational.1

install: install-relational-cli install-python3-relational install-relational
