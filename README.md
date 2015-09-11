Relational an educational tool to provide a workspace for experimenting with *relational* *algebra*, an offshoot of first-order logic.

It provides GUI that can be used for executing relational queries, and also provides a command line interface.

Provides a standalone Python module that can be used for executing relational queries, parsing relational expressions and optimizing them.

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
ρid➡i,name➡n(π a,b(A))
A ⋈ B
```


Run from sources
================

To launch the application, run

```
make
./relational_gui.py
```

If it needs some dependencies:
Qt5, Python 3.4 or greater, PyQt5, pyuic5

It can run on osx but bugreports about that will be rejected.

