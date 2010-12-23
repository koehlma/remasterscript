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

import gobject

import remasterscript.const
import remasterscript.interface.new
import remasterscript.utils

class Controller(gobject.GObject):
    def __init__(self):
        gobject.GObject.__init__(self) 
        self._new = remasterscript.interface.new.New()
        self._new.connect('cancel', self._cancel)
        self._new.connect('start', self._start)
        self._make = remasterscript.interface.new.Make()
        self._make.connect('cancel', self._cancel)
        self._processes = {}
        self._next_functions = [self._mkdir,
                            self._copy_dvd,
                            self._decompress,
                            self._mount,
                            self._copy_data,
                            self._umount,
                            self._clean]
        self._undo_functions = [self._undo_mount,
                            self._undo_mkdir]
        self._undo_action = {'mount' : False,
                                'mkdir' : False}
        self._undo_done = False
        self._success_done = False
        self._undo_paths = []
        
    def start(self, *args):
        self._new.show()
    
    def stop(self, *args):
        self._new.hide()
        self._make.hide()
    
    def _start(self, new, source, target):
        self._new.hide()
        self._make.show()
        self._source = source
        self._target = target
        self._next_functions[0]()
    
    def _next(self):
        if len(self._next_functions) > 1:
            self._next_functions.pop(0)
            self._next_functions[0]()
        else:
            self._undo_done = True
            self._success_done = True
            self.emit('success', self._target)
    
    def _undo(self, quit):
        if not self._undo_done:
            self._undo_done = True
            for process in self._processes:
                self._processes[process].kill()
            if quit == True:
                self._undo_emit = 'quit'
            else:
                self._undo_emit = 'error'
            self._make.set_all('Undo', 0.0)
            self._undo_functions[0]()
    
    def _undo_next(self):
        if len(self._undo_functions) > 1:
            self._undo_functions.pop(0)
            self._undo_functions[0]()
        else:
            self.emit(self._undo_emit)
        
    def _undo_mount(self):
        if self._undo_action['mount'] and 'umount' not in self._undo_action:
            self._make.start('mount', 'Undo - ')
            self._undo_mount = True
            self._processes['mount'] = remasterscript.utils.Util('"%s" "%s"' % (remasterscript.const.BINARY_UMOUNT,
                                                                                                    self._target + '/knoppix-mount'))
            self._processes['mount'].connect('success', self._undo_success, 'mount')
            self._processes['mount'].connect('error', self._undo_error, 'mount')
        else:
            self._undo_next()
    
    def _undo_mkdir(self):
        if self._undo_action['mkdir']:
            self._make.start('mkdir', 'Undo - ')
            paths = ''
            for path in self._undo_paths:
                if os.path.exists(self._target + path):
                    paths += '"%s" ' % (self._target + path)
            self._processes['mkdir'] = remasterscript.utils.Util('"%s" -rf %s' % (remasterscript.const.BINARY_REMOVE,
                                                                                            paths))
            self._processes['mkdir'].connect('success', self._undo_success, 'mkdir')
            self._processes['mkdir'].connect('error', self._undo_error, 'mkdir')
        else:
            self._undo_next()

    def _undo_success(self, process, name):
        if name in self._processes:
            self._processes.pop(name)
        self._make.stop(name, True, 'Undo - ')
        self._undo_next()
    
    def _undo_error(self, process, errorcode, name):
        if name in self._processes:
            self._processes.pop(name)
        self._make.stop(name, False, 'Undo - ')
    
    def _success(self, process, name):
        if not self._undo_done:
            self._undo_action[name] = True
            if name in self._processes:
                self._processes.pop(name)
            self._make.stop(name, True)
            self._next()
        else:
            self._make.stop(name, True)
            self._make.update(name, 'Undo', 0.0)
    
    def _error(self, process, errorcode, name):
        if name in self._processes:
            self._processes.pop(name)
        self._make.stop(name, False)
        if self._undo_done:
            self._make.update(name, 'Undo', 0.0)
        else:
            self._undo(False)
    
    def _mkdir(self):
        self._make.start('mkdir')
        try:
            os.mkdir(self._target + '/knoppix-mount')
            self._make.stop('mkdir', True)
            self._undo_action['mkdir'] = True
            self._undo_paths.append('/knoppix-mount')
            self._next()
        except OSError:
            self._make.stop('mkdir', False)
            self._undo(False)
            
    def _copy_dvd(self):
        self._make.start('copy_dvd')
        self._undo_paths.append('/master')
        self._processes['copy_dvd'] = remasterscript.utils.Util('"%s" -rp "%s" "%s"' % (remasterscript.const.BINARY_COPY,
                                                                            self._source,
                                                                            self._target + '/master'))
        self._processes['copy_dvd'].connect('success', self._success, 'copy_dvd')
        self._processes['copy_dvd'].connect('error', self._error, 'copy_dvd')
        
    def _decompress(self):
        self._undo_paths.append('/knoppix.img')
        self._processes['extract_compressed_fs'] = remasterscript.utils.ExtractCompressedFs(self._target + '/master/KNOPPIX/KNOPPIX',
                                                                                                self._target + '/knoppix.img')
        self._processes['extract_compressed_fs'].connect('update', self._decompress_update)
        self._processes['extract_compressed_fs'].connect('success', self._decompress_success)
        self._processes['extract_compressed_fs'].connect('error', self._decompress_error)
    
    def _decompress_update(self, process, percentage):
        self._make.update('decompress', str(percentage) + '%', float(percentage) / 100)
    
    def _decompress_success(self, process):
        self._processes.pop('extract_compressed_fs')
        self._make.update('decompress', 'Fertig', 1.0)
        self._next()
        
    def _decompress_error(self, process, errorcode):
        self._make.update('decompress', 'Fehler', 0.0)
        self._undo(False)
    
    def _mount(self):
        self._make.start('mount')
        self._processes['mount'] = remasterscript.utils.Util('"%s" -r -o loop "%s" "%s"' % (remasterscript.const.BINARY_MOUNT,
                                                    self._target + '/knoppix.img',
                                                    self._target + '/knoppix-mount'))
        self._processes['mount'].connect('success', self._success, 'mount')
        self._processes['mount'].connect('error', self._error, 'mount')
    
    def _copy_data(self):
        self._make.start('copy_data')
        self._undo_paths.append('/rootdir')
        self._processes['copy_data'] = remasterscript.utils.Util('"%s" -rp "%s" "%s"' % (remasterscript.const.BINARY_COPY,
                                                                            self._target + '/knoppix-mount',
                                                                            self._target + '/rootdir'))
        self._processes['copy_data'].connect('success', self._success, 'copy_data')
        self._processes['copy_data'].connect('error', self._error, 'copy_data')
    
    def _umount(self):
        self._make.start('umount')
        self._processes['umount'] = remasterscript.utils.Util('"%s" "%s"' % (remasterscript.const.BINARY_UMOUNT,
                                                                self._target + '/knoppix-mount'))
        self._processes['umount'].connect('success', self._success, 'umount')
        self._processes['umount'].connect('error', self._error, 'umount')
    
    def _clean(self):
        self._make.start('clean')
        self._make.stop('clean', True)
        self._next()
    
    def _cancel(self, button):
        if self._success_done:
            self.emit('quit')
        else:
            self._undo(True)
    
    def _quit(self, *args):
        if self._success_done:
            self.emit('quit')
        else:
            self._undo(True)

gobject.type_register(Controller)
gobject.signal_new('quit',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('cancel',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('success',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_STRING,))
gobject.signal_new('error',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())