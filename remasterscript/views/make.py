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

import view

class Make(view.View):
    def __init__(self):
        view.View.__init__(self, 'make.ui')
        self._window.connect('delete-event', self._on_quit)
        self._cancel = self._builder.get_object('cancel')
        self._cancel.connect('clicked', self._on_cancel)
        self._bars = {'decompress' : self._builder.get_object('decompress'),
                            'mount' : self._builder.get_object('mount'),
                            'umount' : self._builder.get_object('umount'),
                            'copy_dvd' : self._builder.get_object('copy_dvd'),
                            'copy_data' : self._builder.get_object('copy_data'),
                            'mkdir' : self._builder.get_object('mkdir'),
                            'clean' : self._builder.get_object('clean')}
        self._idle_tasks = {}
    
    def _on_cancel(self, button):
        self.emit('cancel')
    
    def _on_quit(self, widget, event):
        self.emit('quit')
    
    def _pulse(self, progressbar):
        progressbar.pulse()
        return True
    
    def remove_all_idle(self):
        for idle in self._idle_tasks:
            gobject.source_remove(self._idle_tasks[idle])
    
    def set_all(self, text, fraction):
        for bar in self._bars:
            self._bars[bar].set_text(text)
            self._bars[bar].set_fraction(fraction)
    
    def set(self, name, text, fraction):
        self._bars[name].set_text(text)
        self._bars[name].set_fraction(fraction)
        
    def start(self, name, optional = ''):
        self._bars[name].set_text('%sLäuft' % optional)
        self._idle_tasks[name] = gobject.timeout_add(100, self._pulse , self._bars[name])
    
    def stop(self, name, success, optional = ''):
        gobject.source_remove(self._idle_tasks[name])
        if success == True:
            self._bars[name].set_text('%sFertig' % optional)
            self._bars[name].set_fraction(1.0)
        else:
            self._bars[name].set_text('%sFehler' % optional)
            self._bars[name].set_fraction(0.0)

view.type_register(Make)
view.signal_new('cancel',
                    Make,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())
view.signal_new('quit',
                    Make,
                    view.SIGNAL_RUN_LAST,
                    view.TYPE_BOOLEAN,
                    ())