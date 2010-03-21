# -*- coding: utf-8 -*-
# Relational
# Copyright (C) 2010  Salvo "LtWorf" Tomaselli
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
import curses
import curses.panel
import signal
import sys

def terminate(*a):
    '''Restores the terminal and terminates'''
    curses.nocbreak()
    #stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    
    sys.exit(0)

def main():
    #Initializes the signal
    signal.signal(signal.SIGINT,terminate)

    #Initializes curses
    stdscr = curses.initscr()
    curses.start_color() 
    curses.noecho()
    curses.cbreak()#Handles keys immediately rather than awaiting for enter
    stdscr.keypad(1)
    
    win=curses.panel.new_panel(curses.newwin(9,90))
    win.window().box()
    win.window().addstr(3,3,"suca")
    win.window().refresh()
    curses.napms(1000)
    
    
    w=curses.panel.new_panel(curses.newwin(4,80))
    w.window().box()
    w.window().addstr(2,2,"ciao")
    w.window().refresh()
    curses.napms(1000)
    
    win.show()
    
    curses.napms(1000)
    
    
    #qq=curses.textpad.Textbox(stdscr)
    
    '''win = curses.newwin(0, 0)#New windows for the entire screen
    #stdscr.border(0)
    stdscr.addstr(str(dir (win)))

    #curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    #stdscr.addstr(0,0,"ciao",curses.color_pair(1))

    stdscr.addstr(5, 30, "Welcome to Relational")#,curses.A_REVERSE)
    stdscr.refresh()
    curses.napms(1000)
    stdscr.refresh()
    curses.napms(300)
    curses.flash()
    curses.textpad.rectangle(win,0,0,5,10)'''

    while True:
        c = win.window().getch()
        win.window().addstr(str(c))
        win.window().addstr(str(chr(c)))
        win.window().refresh()



main()




terminate()