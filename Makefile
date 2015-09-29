gui: pyqt

pyqt:
	pyuic5 relational_gui/survey.ui > relational_gui/survey.py
	pyuic5 relational_gui/maingui.ui > relational_gui/maingui.py
	pyuic5 relational_gui/rel_edit.ui > relational_gui/rel_edit.py
	pyrcc5 relational_gui/resources.qrc > relational_gui/resources.py

dist: clean
	rm -rf /tmp/relational/
	rm -rf /tmp/relational-*
	mkdir /tmp/relational/
	cp -R * /tmp/relational/
	rm -rf /tmp/relational/windows
	rm -f /tmp/relational/relational_gui/survey.py
	rm -f /tmp/relational/relational_gui/maingui.py
	rm -f /tmp/relational/relational_gui/rel_edit.py
	rm -f /tmp/relational/relational_gui/resources.py
	rm -rf /tmp/relational/debian/

	#mv /tmp/relational /tmp/relational-`./relational_gui.py -v | grep Relational | cut -d" " -f2`
	#(cd /tmp; tar -zcf relational.tar.gz relational-*/)
	(cd /tmp; tar -zcf relational.tar.gz relational/)
	mv /tmp/relational.tar.gz ./relational_`./relational_gui.py -v | grep Relational | cut -d" " -f2`.orig.tar.gz

clean:
	rm -rf `find -name "*~"`
	rm -rf `find -name "*pyc"`
	rm -rf `find -name "*pyo"`
	rm -rf relational*.tar.gz
	rm -rf data
	rm -rf *tar.bz
	rm -rf *.deb

debian:
	dpkg-buildpackage
