.PHONY: all
all: gui translations

.PHONY: gui
gui: relational_gui/survey.py relational_gui/maingui.py relational_gui/rel_edit.py relational_gui/resources.py

relational_gui/maingui.py relational_gui/survey.py relational_gui/rel_edit.py:
	# Create .py file
	pyuic5 $(basename $@).ui > $@
	# Use my custom editor class
	sed -i 's/QtWidgets.QPlainTextEdit/editor.Editor/g' $@
	echo 'from . import editor' >> $@
	# Use gettext instead of Qt translations
	echo 'from gettext import gettext as _' >> $@
	sed -i \
		-e 's/_translate("MainWindow", /_(/g' \
		-e 's/_translate("Dialog", /_(/g' \
		-e 's/_translate("Form", /_(/g' \
		$@

relational_gui/resources.py:
	pyrcc5 relational_gui/resources.qrc > relational_gui/resources.py

.PHONY: mypy
mypy: gui
	mypy relational relational_readline relational_gui

.PHONY: test
test:
	./driver.py

deb-pkg: dist
	mv relational_*.orig.tar.gz* /tmp
	cd /tmp; tar -xf relational_*.orig.tar.gz
	cp -r debian /tmp/relational/
	cd /tmp/relational/; dpkg-buildpackage --changes-option=-S
	mkdir deb-pkg
	mv /tmp/relational* /tmp/python3-relational_*.deb deb-pkg
	$(RM) -r /tmp/relational
	lintian --pedantic -E --color auto -i -I deb-pkg/*changes

.PHONY: dist
dist: clean
	$(RM) -r /tmp/relational/
	$(RM) -r /tmp/relational-*
	mkdir /tmp/relational/
	cp -R * /tmp/relational/
	$(RM) -r /tmp/relational/windows
	$(RM) -r /tmp/relational/debian/

	#mv /tmp/relational /tmp/relational-`head -1 CHANGELOG`
	#(cd /tmp; tar -zcf relational.tar.gz relational-*/)
	(cd /tmp; tar -zcf relational.tar.gz relational/)
	mv /tmp/relational.tar.gz ./relational_`head -1 CHANGELOG`.orig.tar.gz
	gpg --sign --armor --detach-sign ./relational_`head -1 CHANGELOG`.orig.tar.gz

.PHONY: clean
clean:
	$(RM) -r deb-pkg
	$(RM) -r `find -name "*~"`
	$(RM) -r `find -name "*pyc"`
	$(RM) -r `find -name "*pyo"`
	$(RM) -r relational*.tar.gz
	$(RM) -r relational*.tar.gz.asc
	$(RM) -r data
	$(RM) -r *tar.bz
	$(RM) -r *.deb
	$(RM) relational_gui/survey.py
	$(RM) relational_gui/maingui.py
	$(RM) relational_gui/rel_edit.py
	$(RM) relational_gui/resources.py
	$(RM) po/*.mo
	$(RM) -r build
	$(RM) -r *.egg-info

.PHONY: install-relational-cli
install-relational-cli:
	python3 setup/relational-cli.setup.py install --root=$${DESTDIR:-/};
	$(RM) -r build;
	install -D relational.py $${DESTDIR:-/}/usr/bin/relational-cli
	install -D relational-cli.1 $${DESTDIR:-/}/usr/share/man/man1/relational-cli.1

.PHONY: install-python3-relational
install-python3-relational: install_translations
	python3 setup/python3-relational.setup.py install --root=$${DESTDIR:-/};
	$(RM) -r build;

.PHONY: install-relational
install-relational:
	python3 setup/relational.setup.py install --root=$${DESTDIR:-/};
	$(RM) -r build;
	install -D relational.py $${DESTDIR:-/}/usr/bin/relational
	install -m0644 -D relational.desktop $${DESTDIR:-/}/usr/share/applications/relational.desktop
	install -m0644 -D relational_gui/resources/relational.png $${DESTDIR:-/}/usr/share/pixmaps/relational.png
	install -D relational.1 $${DESTDIR:-/}/usr/share/man/man1/relational.1

.PHONY: install
install: install-relational-cli install-python3-relational install-relational

po/messages.pot: relational.py relational/*.py relational_readline/*.py relational_gui/*.py
	xgettext --from-code=utf-8 -L Python -j -o po/messages.pot --package-name=relational \
		relational.py \
		relational_readline/*.py \
		relational_gui/*.py \
		relational/*.py

po/it.po: po/messages.pot
	msgmerge --update $@ po/messages.pot

po/it.mo: po/it.po
	msgfmt po/it.po --output-file $@

.PHONY: translations
translations: po/it.mo

.PHONY: install_translations
install_translations:
	install -m644 -D po/it.mo $${DESTDIR:-/}/usr/share/locale/it/LC_MESSAGES/relational.mo
