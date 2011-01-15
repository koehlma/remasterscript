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

import controller
import remasterscript.views.make as view
import remasterscript.misc.utils as utils
import remasterscript.misc.const as const

class Make(controller.Controller):
    def __init__(self):
        controller.Controller.__init__(self)
        self._view = view.Make()
        self._view.connect('quit', self._on_quit)
        self._view.connect('cancel', self._on_cancel)
        self._functions = [self._mkdir,
                                self._copy_dvd,
                                self._decompress,
                                self._mount,
                                self._copy_data,
                                self._umount,
                                self._clean]
        self._undo_functions = [self._undo_mount, self._undo_created]
        self._undo_actions = {'mount' : False}
        self._created_paths = []
        self._processes = {}
        self._successed = False
        self._undone = False
        self.error_msg = None
    
    def _on_cancel(self, buton):
        self._undo('cancel')
    
    def _on_quit(self, view):
        self._undo('quit')

    def _next(self):
        if len(self._functions) > 1:
            self._functions.pop(0)
            self._functions[0]()
        else:
            self._undone = True
            self._successed = True
            self.emit('success')
    
    def _undo(self, emit):
        if not self._undone:
            self._undone = True
            for process in self._processes:
                self._processes[process].kill()
            self._undo_emit =  emit
            self._view.set_all('Undo', 0.0)
            self._undo_functions[0]()
    
    def _undo_next(self):
        if len(self._undo_functions) > 1:
            self._undo_functions.pop(0)
            self._undo_functions[0]()
        else:
            self.emit(self._undo_emit)
        
    def _undo_mount(self):
        if self._undo_actions['mount'] and 'umount' not in self._undo_actions:
            self._view.start('mount', 'Undo - ')
            self._processes['mount'] = utils.Umount(self._target + '/knoppix-mount/')
            self._processes['mount'].connect('success', self._undo_success, 'mount')
            self._processes['mount'].connect('error', self._undo_error, 'mount')
        else:
            self._undo_next()
    
    def _undo_created(self):
        self._view.start('mkdir', 'Undo - ')
        self._processes['mkdir'] = utils.Remove('-rf', self._created_paths)
        self._processes['mkdir'].connect('success', self._undo_success, 'mkdir')
        self._processes['mkdir'].connect('error', self._undo_error, 'mkdir')

    def _undo_success(self, process, name):
        if name in self._processes:
            self._processes.pop(name)
        self._view.stop(name, True, 'Undo - ')
        self._undo_next()
    
    def _undo_error(self, process, errorcode, name):
        if name in self._processes:
            self._processes.pop(name)
        self._view.stop(name, False, 'Undo - ')
    
    def _success(self, process, name):
        if not self._undone:
            self._undo_actions[name] = True
            if name in self._processes:
                self._processes.pop(name)
            self._view.stop(name, True)
            self._next()
        else:
            self._view.stop(name, True)
            self._view.set(name, 'Undo', 0.0)
    
    def _error(self, process, errorcode, name):
        errors = {'copy_dvd' : 'Kopieren der Daten von der DVD/CD',
                        'mount' : 'Mounten des Images',
                        'copy_data' : 'Kopieren der Daten des Images',
                        'umount' : 'Umounten des Images',
                        'clean' : 'Aufräumen'}
        if name in self._processes:
            self._processes.pop(name)
        self._view.stop(name, False)
        if self._undone:
            self._view.set(name, 'Undo', 0.0)
        else:
            self.error_msg = errors[name]
            self._undo('error')
    
    def _mkdir(self):
        self._view.start('mkdir')
        try:
            os.mkdir(self._target + '/knoppix-mount/')
            self._created_paths.append(self._target + '/knoppix-mount/')
            self._view.stop('mkdir', True)
            self._next()
        except OSError:
            self._view.stop('mkdir', False)
            self.error_msg = 'Erstellen der Verzeichnisse'
            self._undo('error')
            
    def _copy_dvd(self):
        self._view.start('copy_dvd')
        self._created_paths.append(self._target + '/master/')
        self._processes['copy_dvd'] = utils.Copy('-rp', self._source, self._target + '/master/')
        self._processes['copy_dvd'].connect('success', self._success, 'copy_dvd')
        self._processes['copy_dvd'].connect('error', self._error, 'copy_dvd')
        
    def _decompress(self):
        self._created_paths.append(self._target + '/knoppix.img')
        self._processes['extract_compressed_fs'] = utils.ExtractCompressedFs(self._target + '/master/KNOPPIX/KNOPPIX', self._target + '/knoppix.img')
        self._processes['extract_compressed_fs'].connect('update', self._decompress_update)
        self._processes['extract_compressed_fs'].connect('success', self._decompress_success)
        self._processes['extract_compressed_fs'].connect('error', self._decompress_error)
    
    def _decompress_update(self, process, percentage):
        self._view.set('decompress', str(percentage) + '%', float(percentage) / 100)
    
    def _decompress_success(self, process):
        self._processes.pop('extract_compressed_fs')
        self._view.set('decompress', 'Fertig', 1.0)
        self._next()
        
    def _decompress_error(self, process, errorcode):
        self._view.set('decompress', 'Fehler', 0.0)
        self.error_msg = 'Dekomprimieren des Images'
        self._undo('error')
    
    def _mount(self):
        self._view.start('mount')
        self._processes['mount'] = utils.Mount('-r -o loop', self._target + '/knoppix.img', self._target + '/knoppix-mount')
        self._processes['mount'].connect('success', self._success, 'mount')
        self._processes['mount'].connect('error', self._error, 'mount')
    
    def _copy_data(self):
        self._view.start('copy_data')
        self._created_paths.append(self._target + '/rootdir/')
        self._processes['copy_data'] = utils.Copy('-rp', self._target + '/knoppix-mount', self._target + '/rootdir/')
        self._processes['copy_data'].connect('success', self._success, 'copy_data')
        self._processes['copy_data'].connect('error', self._error, 'copy_data')
    
    def _umount(self):
        self._view.start('umount')
        self._processes['umount'] = utils.Umount(self._target + '/knoppix-mount')
        self._processes['umount'].connect('success', self._success, 'umount')
        self._processes['umount'].connect('error', self._error, 'umount')
    
    def _clean(self):
        self._view.start('clean')
        self._processes['clean'] = utils.Remove('-rf', (self._target + '/knoppix-mount/', self._target + '/knoppix.img'))
        self._processes['clean'].connect('success', self._success, 'clean')
        self._processes['clean'].connect('error', self._error, 'clean')

    def set_source(self, source):
        self._source = source
    
    def set_target(self, target):
        self._target = target
    
    def reset(self):
        self._view.remove_all_idle()
        self._view.set_all('Nicht Gestartet', 0.0)
        self._functions = [self._mkdir,
                                self._copy_dvd,
                                self._decompress,
                                self._mount,
                                self._copy_data,
                                self._umount,
                                self._clean]
        self._undo_functions = [self._undo_mount, self._undo_created]
        self._undo_actions = {'mount' : False}
        self._created_paths = []
        self._processes = {}
        self._successed = False
        self._undone = False
        self.error_msg = None
    
    def start(self, controller):
        self._parent = controller
        self._parent.stop()
        self._view.show()
        self._functions[0]()
    
    def stop(self):
        self._view.hide()