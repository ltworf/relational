Relational an educational tool to provide a workspace for experimenting with *relational* *algebra*, an offshoot of first-order logic.

It works on GNU/Linux, Windows and OS X.

It provides:
 * A GUI that can be used for executing relational queries
 * A standalone Python module that can be used for executing relational queries, parsing relational expressions and optimizing them
 * A command line interface


Official website
================

More documentation can be found here http://ltworf.github.io/relational/


Install
=======

Binary download for Windows can be obtained from the website.

For Linux, check your distribution's packages, relational is available on Debian and Ubuntu.


Syntax
======
These are some valid queries

```
σage > 25 and rank == weight(A)
σ (name.upper().startswith('J') and age>21 )(people)
Q ⋈ π a,b(A) ⋈ B
ρid➡i,name➡n(A) - π a,b(π a,b(A)) ∩ σage > 25 or rank = weight(A)
π a,b(π a,b(A))
ρ id➡i,name➡n(π a,b(A))
A ⋈ B
```


Run from sources
================
If it needs some dependencies:
 * Qt5
 * Python 3.4 or greater
 * PyQt5
 * pyuic5 and pyrcc5

You will need to run
```
make
```
to generate some .py files.

To launch the application, run

```
./relational_gui.py
```

or

```
python3 relational_gui.py
```
note: for MacOS you need to make a few changes

1. in file Makefile change the following to make the sed command to work.
```
sed -i '' 's/QtWidgets.QPlainTextEdit/editor.Editor/g' relational_gui/maingui.py
```
2. comment the following on the rational_gui.py file `import sip  # needed on windows`
```
   if x11:
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        #import sip  # needed on windows

 ```