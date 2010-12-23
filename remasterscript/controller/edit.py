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

import os

import gobject

import remasterscript.const
import remasterscript.interface.edit

class Controller(gobject.GObject):
    def __init__(self, source):
        gobject.GObject.__init__(self)
        self._window = remasterscript.interface.edit.Edit()
        self._window.connect('build', self._build)
        self._window.connect('quit', self._quit)
        self._source = source
    
    def start(self, *args):
        self._window.show()
    
    def stop(self, *args):
        self._window.hide()
    
    def _build(self, edit):
        self.emit('build', self._source)
    
    def _quit(self, edit):
        self.emit('quit')

gobject.type_register(Controller)
gobject.signal_new('build',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_STRING,))
gobject.signal_new('quit',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())