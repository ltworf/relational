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
import locale
import signal
import sys
from relational import *

def terminate(*a):
    '''Restores the terminal and terminates'''
    curses.nocbreak()
    stdscr.keypad(0)
    curses.echo()
    curses.endwin()
    
    sys.exit(0)

def main():
    global stdscr
    #Initializes the signal
    signal.signal(signal.SIGINT,terminate)
    
    #Initialize locale, to print unicode chars
    locale.setlocale(locale.LC_ALL,"")
    #Initializes curses
    stdscr = curses.initscr()
    curses.start_color() 
    curses.noecho()
    curses.cbreak()#Handles keys immediately rather than awaiting for enter
    stdscr.keypad(1)
    termsize=stdscr.getmaxyx()
    symselect=init_symbol_list(termsize)
    
    lop=curses.panel.new_panel(stdscr)
    
    win=curses.panel.new_panel(curses.newwin(termsize[0],termsize[1]))
    
    
    
    #win.window().box()
    win.window().addstr(0,(termsize[1]/2)-5,"Relational")
    win.window().refresh()
    #curses.napms(1000)
    
    
    
    query=curses.panel.new_panel(curses.newwin(3,termsize[1],1,0))
    query.window().box()
    query.window().addstr(1,1,"")
    query.window().refresh()
    #curses.napms(1000)
    
    #win.show()
    
    #curses.napms(1000)
    
    
    #qq=curses.textpad.Textbox(stdscr)
    
    '''win = curses.newwin(0, 0)#New windows for the entire screen
    #stdscr.border(0)
    stdscr.addstr(str(dir (win)))

    #curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    #stdscr.addstr(0,0,"ciao",curses.color_pair(1))

    stdscr.addstr(5, 30, "Welcome to Relational")#,curses.A_REVERSE)
    stdscr.refresh()
    
    stdscr.refresh()
    curses.napms(300)
    curses.flash()
    curses.textpad.rectangle(win,0,0,5,10)'''

    squery=''
    
    while True:
        c = win.window().getch()
        
        if c==27: #Escape
            squery+=add_symbol(symselect)
            
            
        #elif c==curses.KEY_BACKSPACE: #Delete
        elif c==13:
            squery=squery[:-1]
        else:
            squery+=chr(c);
        
        
        query.window().box()
        query.top()
        query.window().addstr(1,1,spaces(termsize[1]-2))
        query.window().addstr(1,1,squery)
        
        query.window().refresh()
def init_symbol_list(termsize,create=True):
    
    if create:
        p=curses.panel.new_panel(curses.newwin(15,16,2,termsize[1]/2-7))
    else:
        p=termsize
    p.window().box()
    #p.window().addstr(1,1,"\n8    \na   \nb   \n")
    p.window().addstr(01,2,"0   *")
    p.window().addstr(02,2,"1   -")
    p.window().addstr(03,2,"2   ᑌ")
    p.window().addstr(04,2,"3   ᑎ")
    p.window().addstr(05,2,"4   ᐅᐊ")
    p.window().addstr(06,2,"5   ᐅLEFTᐊ")
    p.window().addstr(07,2,"6   ᐅRIGHTᐊ")
    p.window().addstr( 8,2,"7   ᐅFULLᐊ")
    p.window().addstr( 9,2,"8   σ")
    p.window().addstr(10,2,"9   ρ")
    p.window().addstr(11,2,"a   π")
    p.window().addstr(12,2,"b   ➡")
    p.window().addstr(13,2,"")
    
    #p.hide()
    return p
def add_symbol(p):
    '''Shows the panel to add a symbol
    and then returns the choosen symbol itself'''
    init_symbol_list(p,False)
    
    d_={'0':'*','1':'-','2':'ᑌ','3':'ᑎ','4':'ᐅᐊ','5':'ᐅLEFTᐊ','6':'ᐅRIGHTᐊ','7':'ᐅFULLᐊ','8':'σ','9':'ρ','a':'π','b':'➡'}
    
    
    p.show()
    p.top()
    p.window().refresh()
    c = p.window().getch()
    
    p.hide()
    p.window().refresh()
    try:
        char=d_[chr(c)]
    except:
        char=''
    return char

def spaces(t):
    '''Returns a number of spaces specified t'''
    s=''
    for i in range(t):
        s+=' '
    return s
if __name__=='__main__':
    main()
    terminate()