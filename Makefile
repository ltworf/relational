default:
	echo "sorry, no default action"

clean:
	rm *~ || echo ok
	rm *pyc || echo ok
	rm -rf Relational.app || echo ok
	rm -rf relational || echo ok
	rm relational.tar.gz || echo ok
mac: app
	mkdir relational || echo Exists
	mv Relational.app relational
	mkdir relational/samples || echo Exists
	cp samples/*tlb relational/samples
	tar -zcvvf relational.tar.gz relational/
app:
	mkdir Relational.app/ || echo Exists
	mkdir Relational.app/Contents || echo Exists
	mkdir Relational.app/Contents/Resources || echo Exists
	cp *py Relational.app/Contents/Resources
	cp mac/Info.plist mac/PkgInfo Relational.app/Contents
	mkdir Relational.app/Contents/MacOS || echo Exists
	cp mac/relational mac/Python Relational.app/Contents/MacOS
	cp mac/PythonApplet.icns mac/__argvemulator_relational.py Relational.app/Contents/Resources/
