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
import gobject
from gobject import SIGNAL_RUN_LAST, TYPE_BOOLEAN, TYPE_STRING, TYPE_INT, TYPE_PYOBJECT

import remasterscript.misc.const as const

class View(gobject.GObject):
    def __init__(self, file):
        gobject.GObject.__init__(self)
        self._builder = gtk.Builder()
        self._builder.add_from_file(const.PATH + '/core/views/ui/' + file)
        self._window = self._builder.get_object('window')
    
    def hide(self):
        self._window.hide_all()
        
    def show(self):
        self._window.show_all()

gobject.type_register(View)

def type_register(type):
    gobject.type_register(type)
    
def signal_new(name, type, flags, return_type, param_types):
    gobject.signal_new(name, type, flags, return_type, param_types)