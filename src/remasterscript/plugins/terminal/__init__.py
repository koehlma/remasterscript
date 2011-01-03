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
import gtk

import remasterscript.const as const
import remasterscript.utils as utils

class Terminal(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._builder = gtk.Builder()
        self._builder.add_from_file(const.PATH + '/plugins/terminal/terminal.ui')
        self._window = self._builder.get_object('window')
        self._window.connect('delete-event', self._on_quit)
        self._stop = self._builder.get_object('stop')
        self._stop.connect('clicked', self._on_stop)
        self._start = self._builder.get_object('start')
        self._start.connect('clicked', self._on_start)
        self._container = self._builder.get_object('vbox')
        self._combobox = gtk.combo_box_new_text()
        for terminal in const.TERMINALS:
            if os.path.exists(const.TERMINALS[terminal]):
                self._combobox.append_text(terminal)
        self._combobox.set_active(0)
        self._container.pack_start(self._combobox, False, False)
        self._container.reorder_child(self._combobox, 1)
        self._terminal = None
        
    def _on_quit(self, widget, event):
        self.emit('stop')
        return True
    
    def _on_start(self, button):
        self._terminal = utils.Util('"%s" -e ""%s" "%s""' % (const.TERMINALS[self._get_active_text(self._combobox)],
                                                                    const.BINARY_CHROOT,
                                                                    self._source + '/rootdir/'))
        self._terminal.connect('success', self._success)
        self._terminal.connect('error', self._error)
        
    def _success(self, process):
        self._terminal = None
        
    def _error(self, process, errorcode):
        self._terminal = None
    
    def _on_stop(self, button):
        self.emit('stop')
    
    def _get_active_text(self, combobox):
        model = combobox.get_model()
        active = combobox.get_active()
        if active < 0:
            return None
        return model[active][0]
    
    def set_source(self, source):
        self._source = source
    
    def start(self):
        self._window.show_all()
        
    def stop(self):
        if self._terminal:
            self._terminal.kill()
        self._window.hide_all()
    
    def get_name(self):
        return 'Terminal'
    
    def get_description(self):
        return 'chroot-Terminal öffnen'

gobject.type_register(Terminal)
gobject.signal_new('stop',
                        Terminal,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())