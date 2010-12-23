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
import remasterscript.interface.open

class Controller(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._window = remasterscript.interface.open.Open()
        self._window.connect('open', self._open)
        self._window.connect('cancel', self._cancel)
    
    def start(self, *args):
        self._window.show()
    
    def stop(self, *args):
        self._window.hide()
    
    def _open(self, window, source):
        self._window.hide()
        self.emit('open', source)
    
    def _cancel(self, window):
        self._window.hide()
        self.emit('quit')

gobject.type_register(Controller)
gobject.signal_new('open',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_STRING,))
gobject.signal_new('quit',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())