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

import controller
import remasterscript.core.views.welcome as view

class Welcome(controller.Controller):
    def __init__(self, new, open):
        controller.Controller.__init__(self)
        self._new = new
        self._new.connect('cancel', self.start)
        self._open = open        
        self._open.connect('cancel', self.start)
        self._view = view.Welcome()
        self._view.connect('quit', self._on_quit)
        self._view.connect('new', self._on_new)
        self._view.connect('open', self._on_open)
    
    def _on_quit(self, view):
        self.emit('quit')
    
    def _on_new(self, view):
        self._new.start(self)
    
    def _on_open(self, view):
        self._open.start(self)
        
    def start(self, controller):
        if controller:
            controller.stop()
        self._view.show()
    
    def stop(self):
        self._view.hide()