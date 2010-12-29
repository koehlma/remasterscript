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

import view

class Welcome(view.View):
    def __init__(self):
        view.View.__init__(self, 'welcome.ui')
        self._window.connect('delete-event', self._on_quit)
        self._new = self._builder.get_object('new')
        self._new.connect('clicked', self._on_new)
        self._open = self._builder.get_object('open')
        self._open.connect('clicked', self._on_open)
    
    def _on_new(self, button):
        self.emit('new')
    
    def _on_open(self, button):
        self.emit('open')
    
    def _on_quit(self, widget, event):
        self.emit('quit')

view.type_register(Welcome)
view.signal_new('new',
                    Welcome,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())
view.signal_new('open',
                    Welcome,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())
view.signal_new('quit',
                    Welcome,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())