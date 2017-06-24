#!/usr/bin/env python3
# Relational
# Copyright (C) 2008-2017  Salvo "LtWorf" Tomaselli
#
# Relational is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>

import sys
import os
import os.path
import getopt

version = "2.6"


def printver(exit=True):
    print ("Relational %s" % version)
    print ("Copyright (C) 2008-2017 Salvo 'LtWorf' Tomaselli.")
    print ()
    print ("This program comes with ABSOLUTELY NO WARRANTY.")
    print ("This is free software, and you are welcome to redistribute it")
    print ("under certain conditions.")
    print ("For details see the GPLv3 Licese.")
    print ()
    print ("Written by Salvo 'LtWorf' Tomaselli <tiposchi@tiscali.it>")
    print ()
    print ("http://ltworf.github.io/relational/")
    if exit:
        sys.exit(0)


def printhelp(code=0):
    print ("Relational")
    print ()
    print ("Usage: %s [options] [files]" % sys.argv[0])
    print ()
    print ("  -v            Print version and exits")
    print ("  -h            Print this help and exits")

    if sys.argv[0].endswith('relational-cli'):
        print ("  -q            Uses QT user interface")
        print ("  -r            Uses readline user interface (default)")
    else:
        print ("  -q            Uses QT user interface (default)")
        print ("  -r            Uses readline user interface")
    sys.exit(code)

if __name__ == "__main__":
    if sys.argv[0].endswith('relational-cli'):
        x11 = False
    else:
        x11 = True  # Will try to use the x11 interface

    # Getting command line
    try:
        switches, files = getopt.getopt(sys.argv[1:], "vhqr")
    except:
        printhelp(1)

    for i in switches:
        if i[0] == '-v':
            printver()
        elif i[0] == '-h':
            printhelp()
        elif i[0] == '-q':
            x11 = True
        elif i[0] == '-r':
            x11 = False

    if x11:
        import signal
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        import sip  # needed on windows
        from PyQt5 import QtWidgets
        try:
            from relational_gui import guihandler, about, surveyForm
        except:
            print (
                "Module relational_gui is missing.\n"
                "Please install relational package or run make.",
                file=sys.stderr
            )
            sys.exit(3)

        m = zip(files, map(os.path.isfile, files))
        invalid = ' '.join(
            (i[0] for i in (filter(lambda x: not x[1], m)))
        )
        if invalid:
            print ("%s: not a file" % invalid, file=sys.stderr)
            printhelp(12)

        about.version = version
        surveyForm.version = version
        guihandler.version = version

        app = QtWidgets.QApplication(sys.argv)
        app.setOrganizationName('None')
        app.setApplicationName('relational')
        app.setOrganizationDomain("None")

        form = guihandler.relForm()

        if len(files):
            form.loadRelation(files)

        form.show()
        sys.exit(app.exec_())
    else:
        try:
            import relational_readline.linegui
            if relational_readline.linegui.TTY:
                printver(False)
        except:
            print (
                "Module relational_readline is missing.\nPlease install relational-cli package.",
                file=sys.stderr
            )
            sys.exit(3)
        relational_readline.linegui.version = version
        relational_readline.linegui.main(files)
