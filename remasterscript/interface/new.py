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

class New(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._builder = gtk.Builder()
        self._builder.add_from_file(remasterscript.const.PATH + '/interface/ui/new.ui')
        self._window = self._builder.get_object('window')
        self._window.connect('delete-event', self._on_close)
        self._start = self._builder.get_object('start')
        self._start.connect('clicked', self._on_start)
        self._cancel = self._builder.get_object('cancel')
        self._cancel.connect('clicked', self._on_cancel)
        self._source = self._builder.get_object('source')
        self._target = self._builder.get_object('target')
    
    def destroy(self):
        self._window.destroy()
    
    def hide(self):
        self._window.hide_all()
    
    def show(self):
        self._window.show_all()
    
    def _widget_destroy(self, widget, *args):
        widget.destroy()
    
    def _on_close(self, window, event):
        self.emit('cancel')
        return True
    
    def _on_start(self, button):
        source = self._source.get_filename()
        target = self._target.get_filename()
        if source and target:
            if os.path.exists(source + '/KNOPPIX/KNOPPIX') and os.path.exists(source + '/boot/isolinux/isolinux.bin'):
                self.emit('start', source, target)
            else:
                dialog = gtk.MessageDialog(parent=self._window,
                                        type=gtk.MESSAGE_ERROR,
                                        buttons=gtk.BUTTONS_OK, message_format='Qelle ist keine KNOPPIX-CD/DVD.')
                dialog.connect('response', self._widget_destroy)
                dialog.run()
        else:
            dialog = gtk.MessageDialog(parent=self._window,
                                        type=gtk.MESSAGE_ERROR,
                                        buttons=gtk.BUTTONS_OK, message_format='Qelle und Ziehl müssen gesetzt werden.')
            dialog.connect('response', self._widget_destroy)
            dialog.run()
    
    def _on_cancel(self, button):
        self.emit('cancel')

gobject.type_register(New)
gobject.signal_new('cancel',
                        New,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('start',
                        New,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_STRING, gobject.TYPE_STRING))

class Make(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._builder = gtk.Builder()
        self._builder.add_from_file(remasterscript.const.PATH + '/interface/ui/make.ui')
        self._window = self._builder.get_object('window')
        self._window.connect('delete-event', self._on_close)
        self._cancel = self._builder.get_object('cancel')
        self._cancel.connect('clicked', self._on_cancel)
        self._progress_bars = {'decompress' : self._builder.get_object('decompress'),
                                    'mount' : self._builder.get_object('mount'),
                                    'umount' : self._builder.get_object('umount'),
                                    'copy_dvd' : self._builder.get_object('copy_dvd'),
                                    'copy_data' : self._builder.get_object('copy_data'),
                                    'mkdir' : self._builder.get_object('mkdir'),
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

gobject.type_register(Make)
gobject.signal_new('cancel',
                        Make,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('close',
                        Make,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())