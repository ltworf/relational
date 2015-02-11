Relational an educational tool to provide a workspace for experimenting with *relational* *algebra*, an offshoot of first-order logic.

It provides GUI that can be used for executing relational queries, and also provides a command line interface.

Provides a standalone Python module that can be used for executing relational queries, parsing relational expressions and optimizing them.

Install
=======

Windows installer can be found here: https://code.google.com/p/relational/downloads/list

For Linux, check your distribution's packages, relational is available on Debian and Ubuntu.


Syntax
======

These are some valid queries

```
σage > 25 and rank == weight(A)
σ (name.upper().startswith('J') and age>21 )(people)
Q ᐅᐊ π a,b(A) ᐅᐊ B
ρid➡i,name➡n(A) - π a,b(π a,b(A)) ᑎ σage > 25 or rank = weight(A)
π a,b(π a,b(A))
ρid➡i,name➡n(π a,b(A))
A ᐅᐊ B
```

More documentation can be found here http://ltworf.github.io/relational/



Run from sources
================


To launch the application, run

```
./relational_gui.py
```

If it needs some dependencies:
Qt4, Python 2.7, either PyQT4 or Pyside.

It can run on osx but this is not supported.

