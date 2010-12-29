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
import remasterscript.views.new as view

class New(controller.Controller):
    def __init__(self, edit, make):
        controller.Controller.__init__(self)
        self._edit = edit
        self._make = make
        self._make.connect('cancel', self.start)
        self._make.connect('success', self._on_success)
        self._view = view.New()
        self._view.connect('quit', self._on_quit)
        self._view.connect('cancel', self._on_cancel)
        self._view.connect('start', self._on_start)
    
    def _on_quit(self, view):
        self.emit('quit')
    
    def _on_success(self, make):
        self._edit.set_source(self._target)
        self._edit.start(self._make)
    
    def _on_cancel(self, view):
        self.emit('cancel')
    
    def _on_start(self, view, source, target):
        self._source = source
        self._target = target
        self._make.reset()
        self._make.set_source(source)
        self._make.set_target(target)
        self._make.start(self)
    
    def start(self, controller):
        self._parent = controller
        self._parent.stop()
        self._view.show()
    
    def stop(self):
        self._view.hide()