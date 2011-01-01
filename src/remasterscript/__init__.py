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

import gtk

import controller

def _quit(controller):
    gtk.main_quit()

def main():
    build = controller.build.Build()
    build.connect('quit', _quit)
    edit = controller.edit.Edit(build)
    edit.connect('quit', _quit)
    make = controller.make.Make()
    make.connect('quit', _quit)
    new = controller.new.New(edit, make)
    new.connect('quit', _quit)
    open = controller.open.Open(edit)
    open.connect('quit', _quit)
    welcome = controller.welcome.Welcome(new, open)
    welcome.connect('quit', _quit)
    welcome.start(None)
    gtk.main()