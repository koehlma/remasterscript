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

import view

class New(view.View):
    def __init__(self):
        view.View.__init__(self, 'new.ui')
        self._window.connect('delete-event', self._on_quit)
        self._start = self._builder.get_object('start')
        self._start.connect('clicked', self._on_start)
        self._cancel = self._builder.get_object('cancel')
        self._cancel.connect('clicked', self._on_cancel)
        self._source = self._builder.get_object('source')
        self._source.set_filename(os.path.expanduser('~/'))
        self._target = self._builder.get_object('target')
        self._target.set_filename(os.path.expanduser('~/'))
        
    def _on_start(self, button):
        self.emit('start', self._source.get_filename(), self._target.get_filename())
    
    def _on_cancel(self, button):
        self.emit('cancel')
    
    def _on_quit(self, widget, event):
        self.emit('quit')

view.type_register(New)
view.signal_new('start',
                    New,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    (view.TYPE_STRING, view.TYPE_STRING))
view.signal_new('cancel',
                    New,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())
view.signal_new('quit',
                    New,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())