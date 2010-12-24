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

import base
import remasterscript.const
import remasterscript.utils

info = ('Terminal', 'Öffne ein chroot-Terminal')

class Edit(base.Edit):
    def __init__(self, source):
        base.Edit.__init__(self, source)
        self._ui = gtk.Builder()
        self._ui.add_from_file(remasterscript.const.PATH + '/edit/terminal.ui')
        self._window = self._ui.get_object('window')
        self._start = self._ui.get_object('start')
        self._stop = self._ui.get_object('stop')
        self._container = self._ui.get_object('container')
        self._terminal = gtk.combo_box_new_text()
        for terminal in remasterscript.const.TERMINALS:
            self._terminal.append_text(terminal)
        self._terminal.set_active(0)
        self._container.pack_start(self._terminal, False, False)
        self._container.reorder_child(self._terminal, 1)

        
    def start(self):
        self._window.show_all()
    
    def stop(self):
        self._window.hide_all()

edit = Edit('/home/maximilian/test4')
gtk.main()
