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
import remasterscript.views.open as view

class Open(controller.Controller):
    def __init__(self, edit):
        controller.Controller.__init__(self)
        self._edit = edit
        self._view = view.Open()
        self._view.connect('quit', self._on_quit)
        self._view.connect('cancel', self._on_cancel)
        self._view.connect('open', self._on_open)
    
    def _on_cancel(self, view):
        self.emit('cancel')
    
    def _on_open(self, view, source):
        self._edit.set_source(source)
        self._edit.start(self)
        
    def _on_quit(self, view):
        self.emit('quit')
    
    def start(self, controller):
        self._parent = controller
        self._parent.stop()
        self._view.show()
    
    def stop(self):
        self._view.hide()