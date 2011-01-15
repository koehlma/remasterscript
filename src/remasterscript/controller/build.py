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
import time

import controller
import remasterscript.views.build as view
import remasterscript.utils as utils
import remasterscript.const as const

class Build(controller.Controller):
    def __init__(self):
        controller.Controller.__init__(self)
        self._view = view.Build()
        self._view.connect('test', self._test)
        self._view.connect('back', self._on_back)
        self._view.connect('quit', self._on_quit)
        self._functions = [self._prepare,
                                self._image_iso,
                                self._compress,
                                self._sha1,
                                self._cd_iso,
                                self._clean]
        self._undo_functions = [self._undo_created]
        self._undo_actions = {}
        self._created_paths = []
        self._processes = {}
        self._successed = False
        self._undone = False
    
    def _on_back(self, view):
        if self._successed:
            if 'test' in self._processes:
                self._processes['test'].kill()
            self.emit('success')
        else:
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
   
    def _undo_created(self):
        self._view.start('prepare', 'Undo - ')
        self._processes['prepare'] = utils.Remove('-rf', self._created_paths)
        self._processes['prepare'].connect('success', self._undo_success, 'prepare')
        self._processes['prepare'].connect('error', self._undo_error, 'prepare')

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
        if name in self._processes:
            self._processes.pop(name)
        self._view.stop(name, False)
        if self._undone:
            self._view.set(name, 'Undo', 0.0)
        else:
            self._undo('error')
    
    def _clean(self):
        self._view.start('clean')
        self._processes['clean'] = utils.Util('"%s" -rf "%s"' % (const.BINARY_REMOVE,
                                                                self._source + '/tmp.iso'))
        self._processes['clean'].connect('success', self._success, 'clean')
        self._processes['clean'].connect('error', self._error, 'clean')
        
    def _prepare(self):
        self._view.start('prepare')
        self._processes['prepare'] = utils.Remove('-rf', (self._source + '/master/KNOPPIX/KNOPPIX', self._source + '/remaster.iso'))
        self._processes['prepare'].connect('success', self._success, 'prepare')
        self._processes['prepare'].connect('error', self._error, 'prepare')
    
    def _sha1(self):
        self._view.start('sha1')
        self._processes['sha1'] = utils.Util('"%s" "%s" "%s" "%s"' % (const.BINARY_BASH,
                                                            const.PATH + '/scripts/sha1.sh',
                                                            self._source  + '/master/',
                                                            self._source + '/master/KNOPPIX/sha1sums'))
        self._processes['sha1'].connect('success', self._success, 'sha1')
        self._processes['sha1'].connect('error', self._error, 'sha1')
    
    def _image_iso(self):
        self._created_paths.append('/tmp.iso')
        self._view.set('image_iso', 'Gestartet', 0.0)
        self._processes['image_iso'] = utils.MkIsoFs('-R -U -V "KNOPPIX.net filesystem" -publisher "KNOPPIX" -hide-rr-moved -cache-inodes -no-bak -pad -o',
                                                                        self._source + '/rootdir',
                                                                        self._source + '/tmp.iso')
        self._processes['image_iso'].connect('update', self._image_iso_update)
        self._processes['image_iso'].connect('success', self._image_iso_success)
        self._processes['image_iso'].connect('error', self._image_iso_error)
        
    
    def _image_iso_update(self, process, percentage):
        self._view.set('image_iso', str(percentage) + '%', float(percentage) / 100)
    
    def _image_iso_success(self, process):
        self._processes.pop('image_iso')
        self._view.set('image_iso', 'Fertig', 1.0)
        self._next()
    
    def _image_iso_error(self, process, errorcode):
        self._view.set('image_iso', 'Fehler', 0.0)
        self._undo(False)
    
    def _cd_iso(self):
        self._iso_time = time.strftime('%Y%m%d-%H%M')
        self._created_paths.append('/remaster-%s.iso' % (self._iso_time))
        self._view.set('cd_iso', 'Gestartet', 0.0)
        self._processes['cd_iso'] = utils.MkIsoFs('-pad -l -r -J -v -V "KNOPPIX" -no-emul-boot -boot-load-size 4 -boot-info-table -b boot/isolinux/isolinux.bin -c boot/isolinux/boot.cat -hide-rr-moved -o',
                                                                        self._source + '/master',
                                                                        self._source + '/remaster-%s.iso' % (self._iso_time))
        self._processes['cd_iso'].connect('update', self._cd_iso_update)
        self._processes['cd_iso'].connect('success', self._cd_iso_success)
        self._processes['cd_iso'].connect('error', self._cd_iso_error)
        
    
    def _cd_iso_update(self, process, percentage):
        self._view.set('cd_iso', str(percentage) + '%', float(percentage) / 100)
    
    def _cd_iso_success(self, process):
        self._processes.pop('cd_iso')
        self._view.set('cd_iso', 'Fertig', 1.0)
        self._next()
    
    def _cd_iso_error(self, process, errorcode):
        self._view.set('cd_iso', 'Fehler', 0.0)
        self._undo(False)
    
    def _compress(self):
        self._created_paths.append('/tmpcompress.iso')
        self._view.start('compress')
        self._processes['compress'] = utils.CreateCompressedFs(self._source + '/tmpcompress.iso',
                                                                                    self._source + '/tmp.iso',
                                                                                    self._source + '/master/KNOPPIX/KNOPPIX')
        self._processes['compress'].connect('update', self._compress_update)
        self._processes['compress'].connect('success', self._success, 'compress')
        self._processes['compress'].connect('error', self._error, 'compress')
        
    
    def _compress_update(self, process, time):
        self._view.set_text('compress', 'Noch %i Sekunden' % (time))
    
    def _test(self, view):
        if self._successed:
                self._processes['test'] = utils.Util('"%s" -cdrom "%s" -m %i -no-reboot' % (const.BINARY_QEMU,
                                                                                                    self._source + '/remaster-%s.iso' % (self._iso_time),
                                                                                                    const.QEMU_MEM_SIZE))
    
    def reset(self):
        self._view.remove_all_idle()
        self._view.set_all('Nicht Gestartet', 0.0)
        self._functions = [self._prepare,
                                self._image_iso,
                                self._compress,
                                self._sha1,
                                self._cd_iso,
                                self._clean]
        self._undo_functions = [self._undo_created]
        self._undo_actions = {}
        self._created_paths = []
        self._processes = {}
        self._successed = False
        self._undone = False
    
    def set_source(self, source):
        self._source = source
    
    def start(self, controller):
        self._parent = controller
        self._parent.stop()
        self._view.show()
        self._functions[0]()
    
    def stop(self):
        self._view.hide()