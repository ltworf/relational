#!/usr/bin/env python3
# Relational
# Copyright (C) 2023  Salvo "LtWorf" Tomaselli
#
# Relation is free software: you can redistribute it and/or modify
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
#
# Used to receive feedback from relational

from os import environ
from syslog import *

HEADERHTTP='HTTP/1.0 200 Ok\r\nContent-Type: text/html; charset=UTF-8\r\nConnection: close\r\n\r\n'
NOTFOUND='HTTP/1.0 404 Not found\r\nContent-Type: text/html; charset=UTF-8\r\nConnection: close\r\n\r\n<html><body><p>Not found</p></body></html>'

def main():
    if 'HTTP_X_SURVEY' not in environ:
        syslog(LOG_ERR, "Got invalid survey")
        print(NOTFOUND)
        return
    syslog(LOG_INFO, "Got valid survey")
    import datetime
    with open('/srv/www/survey.txt', 'at') as f:
        print(datetime.datetime.now(), file=f)
        for k, v in environ.items():
            if k.startswith('HTTP_X_SURVEY'):
                print(f'{k} = {v}', file=f)
        print(file=f)
    print(HEADERHTTP)

if __name__ == '__main__':
    openlog('feedback')
    try:
        main()
    except Exception as e:
        syslog(LOG_ERR, repr(e))
        from sys import exit
        exit(1)
