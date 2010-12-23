# -*- coding:utf8 -*-
import re
import os

import gtk
import gobject

import controller

#import ui
#import utils
#import const

def print_event(*args):
    print args
"""
class Controller(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self)
        self._welcome = ui.Welcome()
        self._welcome.connect('new', self._on_new)
        self._welcome.connect('open', self._on_open)
        self._welcome.connect('cancel', self._on_quit)
        self._welcome.show()
        self._new = ui.New()
        self._new.connect('cancel', self._on_quit)
        self._new.connect('start', self._on_start)
        self._make = ui.Make()
        self._make.connect('cancel', self._on_quit)
        self._processes = {}
    
    def _start_mkdir(self):
        self._make.mkdir_start('Läuft')
        try:
            os.mkdir(self._target + '/knoppix-mount')
            self._make.mkdir_end(1.0, 'Fertig')
            self._start_copy_dvd()
        except OSError:
            self._make.mkdir_end(0.0, 'Fehler')
            
    def _start_copy_dvd(self):
        self._make.copy_dvd_start('Läuft')
        self._processes['copy_dvd'] = utils.Util('"%s" -rp "%s" "%s"' % (const.BINARY_COPY,
                                                                            self._source,
                                                                            self._target + '/master'))
        self._processes['copy_dvd'].connect('success', self._on_copy_dvd_success)
        self._processes['copy_dvd'].connect('error', self._on_copy_dvd_error)
    
    def _on_copy_dvd_success(self, process):
        self._processes.pop('copy_dvd')
        self._make.copy_dvd_end(1.0, 'Fertig')
        self._start_decompress()
        
    def _on_copy_dvd_error(self, process, errorcode):
        self._processes.pop('copy_dvd')
        self._make.copy_dvd_end(0.0, 'Fehler')
        
    def _start_decompress(self):
        self._processes['extract_compressed_fs'] = utils.ExtractCompressedFs(self._target + '/master/KNOPPIX/KNOPPIX', self._target + '/knoppix.img')
        self._processes['extract_compressed_fs'].connect('update', self._on_decompress_update)
        self._processes['extract_compressed_fs'].connect('success', self._on_decompress_success)
        self._processes['extract_compressed_fs'].connect('error', self._on_decompress_error)
    
    def _on_decompress_update(self, process, percentage):
        self._make.decompress_update(float(percentage) / 100, str(percentage) + '%')
    
    def _on_decompress_success(self, process):
        self._processes.pop('extract_compressed_fs')
        self._make.decompress_update(1, 'Fertig')
        self._start_mount()
        
    def _on_decompress_error(self, process, errorcode):
        self._make.decompress_update(0, 'Fehler')
    
    def _start_mount(self):
        self._make.mount_start('Läuft')
        self._processes['mount'] = utils.Util('"%s" -r -o loop "%s" "%s"' % (const.BINARY_MOUNT,
                                                    self._target + '/knoppix.img',
                                                    self._target + '/knoppix-mount'))
        self._processes['mount'].connect('success', self._on_mount_success)
        self._processes['mount'].connect('error', self._on_mount_error)
    
    def _on_mount_success(self, process):
        self._processes.pop('mount')
        self._make.mount_end(1.0, 'Fertig')
        self._start_copy_data()
        
    def _on_mount_error(self, process, errorcode):
        self._processes.pop('mount')
        self._make.mount_end(0.0, 'Fehler')
    
    def _start_copy_data(self):
        self._make.copy_data_start('Läuft')
        self._processes['copy_data'] = utils.Util('"%s" -rp "%s" "%s"' % (const.BINARY_COPY,
                                                                            self._target + '/knoppix-mount',
                                                                            self._target + '/rootdir'))
        self._processes['copy_data'].connect('success', self._on_copy_data_success)
        self._processes['copy_data'].connect('error', self._on_copy_data_error)
    
    def _on_copy_data_success(self, process):
        self._processes.pop('copy_data')
        self._make.copy_data_end(1.0, 'Fertig')
        self._start_umount()
        
    def _on_copy_data_error(self, process, errorcode):
        self._processes.pop('copy_data')
        self._make.copy_data_end(0.0, 'Fehler')
    
    def _start_umount(self):
        self._make.umount_start('Läuft')
        self._processes['umount'] = utils.Util('"%s" "%s"' % (const.BINARY_UMOUNT,
                                                                self._target + '/knoppix-mount'))
        self._processes['umount'].connect('success', self._on_umount_success)
        self._processes['umount'].connect('error', self._on_umount_error)
    
    def _on_umount_success(self, process):
        self._processes.pop('umount')
        self._make.umount_end(1.0, 'Fertig')

    def _on_umount_error(self, process, errorcode):
        self._processes.pop('umount')
        self._make.umount_end(0.0, 'Fehler')
    
    def _on_start(self, new, source, target):
        self._new.hide()
        self._make.show()
        self._source = source
        self._target = target
        self._start_mkdir()

    def _on_new(self, welcome):
        self._welcome.hide()
        self._new.show()
    
    def _on_open(self, welcome):
        pass
    
    def _on_quit(self, *args):
        for process in self._processes:
            self._processes[process].kill()
        self.emit('quit')

gobject.type_register(Controller)
gobject.signal_new('quit',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
"""

def _new_success(new, source):
    edit = controller.edit.Controller(source)
    edit.connect('quit', quit)
    edit.connect('build', _build)
    edit.start()
    new.stop()

def _build():
    pass

def quit(*args):
    gtk.main_quit()

def main():
    new = controller.new.Controller()
    new.stop()
    new.connect('quit', quit)
    new.connect('cancel', quit)
    welcome = controller.welcome.Controller()
    welcome.start()
    welcome.connect('quit', quit)
    welcome.connect('new', new.start)
    gtk.main()