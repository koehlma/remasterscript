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

import gtk
import gobject

import remasterscript.const

class Build(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._builder = gtk.Builder()
        self._builder.add_from_file(remasterscript.const.PATH + '/interface/ui/build.ui')
        self._window = self._builder.get_object('window')
        self._window.connect('delete-event', self._on_close)
        self._back = self._builder.get_object('back')
        self._back.connect('clicked', self._on_cancel)
        self._test = self._builder.get_object('test')
        self._test.connect('clicked', self._on_test)
        self._progress_bars = {'prepare' : self._builder.get_object('prepare'),
                                    'sha1' : self._builder.get_object('sha1'),
                                    'image_iso' : self._builder.get_object('image_iso'),
                                    'compress' : self._builder.get_object('compress'),
                                    'cd_iso' : self._builder.get_object('cd_iso'),
                                    'clean' : self._builder.get_object('clean')}
        self._idle_tasks = {}
        
    def destroy(self):
        self._window.destroy()
    
    def hide(self):
        self._window.hide_all()
    
    def show(self):
        self._window.show_all()
        
    def _pulse(self, progressbar):
        progressbar.pulse()
        return True
    
    def set_all(self, text, fraction):
        for bar in self._progress_bars:
            self._progress_bars[bar].set_text(text)
            self._progress_bars[bar].set_fraction(fraction)
    
    def set_text(self, name, text):
        self._progress_bars[name].set_text(text)
    
    def start(self, name, optional = ''):
        self._progress_bars[name].set_text('%sLäuft' % optional)
        self._idle_tasks[name] = gobject.timeout_add(100, self._pulse , self._progress_bars[name])
    
    def stop(self, name, success, optional = ''):
        gobject.source_remove(self._idle_tasks[name])
        if success == True:
            self._progress_bars[name].set_text('%sFertig' % optional)
            self._progress_bars[name].set_fraction(1.0)
        else:
            self._progress_bars[name].set_text('%sFehler' % optional)
            self._progress_bars[name].set_fraction(0.0)
    
    def update(self, name, text, fraction):
        self._progress_bars[name].set_fraction(fraction)
        self._progress_bars[name].set_text(text)
    
    def _on_close(self, window, event):
        self.emit('close')
        return True
    
    def _on_cancel(self, button):
        self.emit('cancel')
    
    def _on_test(self, button):
        self.emit('test')

gobject.type_register(Build)
gobject.signal_new('cancel',
                        Build,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('close',
                        Build,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('test',
                        Build,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())