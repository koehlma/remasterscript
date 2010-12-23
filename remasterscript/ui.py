# -*- coding:utf8 -*-
import os

import gtk
import gobject

import const

class Make(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._builder = gtk.Builder()
        self._builder.add_from_file(const.PATH + '/ui/make.ui')
        self._window = self._builder.get_object('make')
        self._window.connect('delete-event', self._on_close)
        self._cancel = self._builder.get_object('cancel')
        self._cancel.connect('clicked', self._on_cancel)
        self._decompress = self._builder.get_object('decompress')
        self._mount = self._builder.get_object('mount')
        self._umount = self._builder.get_object('umount')
        self._copy_dvd = self._builder.get_object('copy_dvd')
        self._copy_data = self._builder.get_object('copy_data')
        self._mkdir = self._builder.get_object('mkdir')
        
    def destroy(self):
        self._window.destroy()
    
    def hide(self):
        self._window.hide_all()
    
    def show(self):
        self._window.show_all()
        
    def _pulse(self, progressbar):
        progressbar.pulse()
        return True
    
    def mount_start(self, text):
        self._mount.set_text(text)
        self._mount_idle = gobject.timeout_add(100, self._pulse , self._mount)
    
    def mount_end(self, fraction, text):
        self._mount.set_text(text)
        self._mount.set_fraction(fraction)
        gobject.source_remove(self._mount_idle)

    def mkdir_start(self, text):
        self._mkdir.set_text(text)
        self._mkdir_idle = gobject.timeout_add(100, self._pulse , self._mkdir)
    
    def mkdir_end(self, fraction, text):
        self._mkdir.set_text(text)
        self._mkdir.set_fraction(fraction)
        gobject.source_remove(self._mkdir_idle)

    def umount_start(self, text):
        self._umount.set_text(text)
        self._umount_idle = gobject.timeout_add(100, self._pulse , self._umount)
    
    def umount_end(self, fraction, text):
        self._umount.set_text(text)
        self._umount.set_fraction(fraction)
        gobject.source_remove(self._umount_idle)
    
    def copy_dvd_start(self, text):
        self._copy_dvd.set_text(text)
        self._copy_dvd_idle = gobject.timeout_add(100, self._pulse, self._copy_dvd)
    
    def copy_dvd_end(self, fraction, text):
        self._copy_dvd.set_text(text)
        self._copy_dvd.set_fraction(fraction)
        gobject.source_remove(self._copy_dvd_idle)
    
    def copy_data_start(self, text):
        self._copy_data.set_text(text)
        self._copy_data_idle = gobject.timeout_add(100, self._pulse, self._copy_data)
    
    def copy_data_end(self, fraction, text):
        self._copy_data.set_text(text)
        self._copy_data.set_fraction(fraction)
        gobject.source_remove(self._copy_data_idle)
    
    def decompress_update(self, fraction, percentage):
        self._decompress.set_fraction(fraction)
        self._decompress.set_text(percentage)
    
    def _on_close(self, window, event):
        self.emit('cancel')
        return True
    
    def _on_cancel(self, button):
        self.emit('cancel')

gobject.type_register(Make)
gobject.signal_new('cancel',
                        Make,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())

class New(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._builder = gtk.Builder()
        self._builder.add_from_file(const.PATH + '/ui/new.ui')
        self._window = self._builder.get_object('new')
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

class Welcome(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._builder = gtk.Builder()
        self._builder.add_from_file(const.PATH + '/ui/welcome.ui')
        self._window = self._builder.get_object('welcome')
        self._window.connect('delete-event', self._on_close)
        self._new = self._builder.get_object('new')
        self._new.connect('clicked', self._on_new)
        self._open = self._builder.get_object('open')
        self._open.connect('clicked', self._on_open)
    
    def destroy(self):
        self._window.destroy()
        
    def hide(self):
        self._window.hide_all()
    
    def show(self):
        self._window.show_all()
    
    def _on_close(self, window, event):
        self.emit('cancel')
        return True
    
    def _on_new(self, button):
        self.emit('new')
    
    def _on_open(self, button):
        self.emit('open')
        
gobject.type_register(Welcome)
gobject.signal_new('cancel',
                        Welcome,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('new',
                        Welcome,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('open',
                        Welcome,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())