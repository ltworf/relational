.. link: 
.. description: 
.. tags: 
.. date: 2014/01/01 10:44:33
.. title: Download
.. slug: download

Check the downloads here: https://code.google.com/p/relational/downloads/

And remember that relational is already packaged for Debian, Ubuntu, Gentoo.


Install on Debian/Ubuntu
========================
Relational is in the stable, testing and unstable repositories, so there is no need for particular efforts.

```
# aptitude install relational
```

A menu entry will be created.

If you don't want the QT deps, you can install relational-cli package, that runs inside the terminal.

Install on Gentoo
=================

```
emerge -av  dev-python/PyQt4; emerge -av media-fonts/dejavu
```

If you want the embedded documentation (not mandatory):

```
emerge -av x11-libs/qt-webkit
```


Install on Windows
==================

Download the .exe setup and install it.

On older versions of windows you might need to separately download and install the Microsoft Visual C++ 2008 Redistributable Package.

Install on OsX
==============

Relational needs PyQt4 and Python2.7 to work, so make sure to have them on your system.

Download the source package, and then run 

```
./relational_gui.py
```
