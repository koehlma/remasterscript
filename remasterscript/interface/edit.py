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

import remasterscript.const

class Edit(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._builder = gtk.Builder()
        self._builder.add_from_file(remasterscript.const.PATH + '/interface/ui/edit.ui')
        self._window = self._builder.get_object('window')
        self._window.connect('delete-event', self._on_quit)
        self._quit = self._builder.get_object('quit')
        self._quit.connect('clicked', self._on_quit)
        self._build = self._builder.get_object('build')
        self._build.connect('clicked', self._on_build)
    
    def destroy(self):
        self._window.destroy()
        
    def hide(self):
        self._window.hide_all()
    
    def show(self):
        self._window.show_all()
    
    def _on_quit(self, *args):
        self.emit('quit')
        return True
    
    def _on_build(self, button):
        self.emit('build')
        
gobject.type_register(Edit)
gobject.signal_new('build',
                        Edit,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('quit',
                        Edit,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())