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

import gobject
import gtk

import remasterscript.misc.const as const
import remasterscript.misc.utils as utils

class MiniRT(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._builder = gtk.Builder()
        self._builder.add_from_file(const.PATH + '/plugins/minirt/minirt.ui')
        self._window = self._builder.get_object('window')
        self._window.connect('delete-event', self._on_quit)
        self._unpack = self._builder.get_object('unpack')
        self._unpack.connect('clicked', self._on_unpack)
        self._pack = self._builder.get_object('pack')
        self._pack.connect('clicked', self._on_pack)
        self._status = self._builder.get_object('status')
        self._process = None
        
    def _on_quit(self, widget, event):
        self.emit('stop')
        return True
    
    def _pulse(self, progressbar):
        progressbar.pulse()
        return True
    
    def _on_unpack(self, button):
        if not self._process:
            self._process = utils.Util('"%s" "%s" "%s"' % (const.BINARY_BASH,
                                                                const.PATH + '/plugins/minirt/unpack.sh',
                                                                self._source))
            self._process.connect('success', self._success)
            self._process.connect('error', self._error)
            self._status.set_text('Läuft')
            self._process_idle = gobject.timeout_add(100, self._pulse , self._status)
    
    def _on_pack(self, button):
         if not self._process:
            self._process = utils.Util('"%s" "%s" "%s"' % (const.BINARY_BASH,
                                                                const.PATH + '/plugins/minirt/pack.sh',
                                                                self._source))
            self._process.connect('success', self._success)
            self._process.connect('error', self._error)
            self._status.set_text('Läuft')
            self._process_idle = gobject.timeout_add(100, self._pulse , self._status)

    def _success(self, process):
        gobject.source_remove(self._process_idle)
        self._status.set_text('Fertig')
        self._status.set_fraction(1.0)
        self._process = None
    
    def _error(self, process, errorcode):
        gobject.source_remove(self._process_idle)
        self._status.set_text('Fehler')
        self._status.set_fraction(0.0)
        self._process = None
    
    def set_source(self, source):
        self._source = source
    
    def start(self):
        self._window.show_all()
        
    def stop(self):
        if self._process:
            self._process.kill()
        self._window.hide_all()
    
    def get_name(self):
        return 'MiniRT'
    
    def get_description(self):
        return 'MiniRT auspacken und einpacken'

gobject.type_register(MiniRT)
gobject.signal_new('stop',
                        MiniRT,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())