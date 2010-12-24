# -*- coding:utf8 -*-
"""
This file is part of Knoppix-Remaster-Script.

Knoppix-Remaster-Script is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Knoppix-Remaster-Script is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Knoppix-Remaster-Script.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import os

import gtk
import gobject

import controller

def _new_success(new, source):
    edit = controller.edit.Controller(source)
    edit.connect('quit', quit)
    edit.connect('build', _build)
    edit.start()
    new.stop()

def _open(open, source):
    edit = controller.edit.Controller(source)
    edit.connect('quit', quit)
    edit.connect('build', _build)
    edit.start()
    open.stop()

def _build(edit, source):
    edit.stop()
    build = controller.build.Controller(source)
    build.connect('quit', quit)
    build.connect('back', edit.start)
    build.start()

def quit(*args):
    gtk.main_quit()

def main():
    new = controller.new.Controller()
    new.stop()
    new.connect('quit', quit)
    new.connect('cancel', quit)
    new.connect('success', _new_success)
    open = controller.open.Controller()
    open.connect('quit', quit)
    open.connect('open', _open)
    open.stop()
    welcome = controller.welcome.Controller()
    welcome.start()
    welcome.connect('quit', quit)
    welcome.connect('new', new.start)
    welcome.connect('open', open.start)
    gtk.main()