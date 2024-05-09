THE PROJECT HAS MOVED
=====================

[The new repository is https://codeberg.org/ltworf/relational](https://codeberg.org/ltworf/relational)


Relational
==========

Relational an educational tool to provide a workspace for experimenting with *relational* *algebra*, an offshoot of first-order logic.

![screenshot](https://ltworf.github.io/relational/screenshots/3.png)

I test it on GNU/Linux and Windows. It probably works on other systems too.

It provides:
 * A GUI that can be used for executing relational queries
 * A standalone Python module that can be used for executing relational queries, parsing relational expressions and optimizing them
 * A command line interface

[![Donate to LtWorf](docs/donate.svg)](https://liberapay.com/ltworf/donate)


Official website
================

More documentation can be found here https://ltworf.github.io/relational/


Install
=======

* Windows: https://ltworf.github.io/relational/download.html?exe
* Debian based: `apt-get install relational`
* Everyone else: Download the sources https://ltworf.github.io/relational/download.html?tar.gz


Run from sources
================

For the dependencies, check `debian/control` for the build dependencies.

You will need to run
```
make
```
to generate some .py files.

To launch the application, run

```
./relational.py
```

Syntax
======

These are some valid queries (using the provided example dataset)

```
# Join people and skills
people ⋈ skills

# Select people within a certain age range
σ age > 25 and age < 50 (people)

# Selection with complicated expression requires an extra set of () around the expression
σ (name.upper().startswith('J') and age > 21) (people)

# Cartesian product of people with itself, including only name and id
ρ id➡i, name➡n (people) * π name, id (people)
```

For the selection, python expressions are used.

The syntax is explained here: https://ltworf.github.io/relational/allowed_expressions.html
