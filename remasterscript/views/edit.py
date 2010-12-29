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

class Edit(view.View):
    def __init__(self):
        view.View.__init__(self, 'edit.ui')
        self._window.connect('delete-event', self._on_quit)
        self._quit = self._builder.get_object('quit')
        self._quit.connect('clicked', self._on_quit)
        self._build = self._builder.get_object('build')
        self._build.connect('clicked', self._on_build)
    
    def _on_build(self, button):
        self.emit('build')
        
    def _on_quit(self, widget, event = None):
        self.emit('quit')

view.type_register(Edit)
view.signal_new('build',
                    Edit,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())
view.signal_new('quit',
                    Edit,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())