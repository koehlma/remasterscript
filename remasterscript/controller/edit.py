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
import remasterscript.interface.welcome

class Controller(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._welcome = remasterscript.interface.welcome.Welcome()
        self._welcome.connect('new', self._on_new)
        self._welcome.connect('open', self._on_open)
        self._welcome.connect('cancel', self._on_cancel)
    
    def start(self):
        self._welcome.show()
    
    def stop(self):
        self._welcome.hide()
    
    def _on_new(self, welcome):
        self._welcome.hide()
        self.emit('new')
    
    def _on_open(self, welcome):
        self._welcome.hide()
        self.emit('open')
    
    def _on_cancel(self, welcome):
        self._welcome.hide()
        self.emit('quit')

gobject.type_register(Controller)
gobject.signal_new('new',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('open',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('quit',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())