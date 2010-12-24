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
import remasterscript.interface.build
import remasterscript.utils

class Controller(gobject.GObject):
    def __init__(self, source):
        gobject.GObject.__init__(self) 
        self._build = remasterscript.interface.build.Build()
        self._build.connect('cancel', self._cancel)
        self._build.connect('close', self._quit)
        self._build.connect('test', self._test)
        self._source = source
        self._processes = {}
        self._next_functions = [self._prepare,
                                    self._image_iso,
                                    self._compress,
                                    #self._sha1,
                                    self._cd_iso,
                                    self._clean]
        self._undo_functions = [self._undo_prepare]
        self._undo_action = {'prepare' : True}
        self._undo_done = False
        self._success_done = False
        self._undo_paths = []
        
    def start(self, *args):
        self._build.show()
        self._next_functions[0]()
    
    def stop(self, *args):
        self._build.hide()
   
    def _next(self):
        if len(self._next_functions) > 1:
            self._next_functions.pop(0)
            self._next_functions[0]()
        else:
            self._undo_done = True
            self._success_done = True
            #self.emit('success', self._source)
    
    def _undo(self, quit):
        if not self._undo_done:
            self._undo_done = True
            for process in self._processes:
                self._processes[process].kill()
            if quit == True:
                self._undo_emit = 'back'
            else:
                self._undo_emit = 'error'
            self._build.set_all('Undo', 0.0)
            self._undo_functions[0]()
    
    def _undo_next(self):
        if len(self._undo_functions) > 1:
            self._undo_functions.pop(0)
            self._undo_functions[0]()
        else:
            self._build.hide()
            self.emit(self._undo_emit)
        
    def _undo_prepare(self):
        if self._undo_action['prepare']:
            self._build.start('prepare', 'Undo - ')
            paths = ''
            print "undo"
            for path in self._undo_paths:
                if os.path.exists(self._source + path):
                    paths += '"%s" ' % (self._source + path)
            self._processes['prepare'] = remasterscript.utils.Util('"%s" -rf %s' % (remasterscript.const.BINARY_REMOVE,
                                                                                            paths))
            self._processes['prepare'].connect('success', self._undo_success, 'prepare')
            self._processes['prepare'].connect('error', self._undo_error, 'prepare')
        else:
            self._undo_next()

    def _undo_success(self, process, name):
        if name in self._processes:
            self._processes.pop(name)
        self._build.stop(name, True, 'Undo - ')
        self._undo_next()
    
    def _undo_error(self, process, errorcode, name):
        if name in self._processes:
            self._processes.pop(name)
        self._build.stop(name, False, 'Undo - ')
    
    def _success(self, process, name):
        if not self._undo_done:
            self._undo_action[name] = True
            if name in self._processes:
                self._processes.pop(name)
            self._build.stop(name, True)
            self._next()
        else:
            self._build.stop(name, True)
            self._build.update(name, 'Undo', 0.0)
    
    def _error(self, process, errorcode, name):
        if name in self._processes:
            self._processes.pop(name)
        self._build.stop(name, False)
        if self._undo_done:
            self._build.update(name, 'Undo', 0.0)
        else:
            self._undo(False)
    
    def _clean(self):
        self._build.start('clean')
        self._processes['clean'] = remasterscript.utils.Util('"%s" -rf "%s"' % (remasterscript.const.BINARY_REMOVE,
                                                                self._source + '/tmp.iso'))
        self._processes['clean'].connect('success', self._success, 'clean')
        self._processes['clean'].connect('error', self._error, 'clean')
        
    def _prepare(self):
        self._undo_action['prepare'] = True
        self._build.start('prepare')
        self._processes['prepare'] = remasterscript.utils.Util('"%s" -rf "%s" "%s"' % (remasterscript.const.BINARY_REMOVE,
                                                                self._source + '/master/KNOPPIX/KNOPPIX',
                                                                self._source + '/remaster.iso'))
        self._processes['prepare'].connect('success', self._success, 'prepare')
        self._processes['prepare'].connect('error', self._error, 'prepare')
    
    def _sha1(self):
        self._build.start('sha1')
        print '"%s" -c "find %s -type f -not -name sha1sums -not -name boot.cat -not -name isolinux.bin -exec sha1sum \'{}\' \; | sed \'s\$%s\$*\$g\' >%s"' % (remasterscript.const.BINARY_BASH,
                                                                                                                                                                                                                                                                self._source + '/master',
                                                                                                                                                                                                                                                                self._source  + '/master/',
                                                                                                                                                                                                                                                                self._source + '/master/KNOPPIX/sha1sums')
        self._processes['sha1'] = remasterscript.utils.Util('"%s" -c "find %s -type f -not -name sha1sums -not -name boot.cat -not -name isolinux.bin -exec sha1sum \'{}\' \; | sed \'s\$%s\$*\$g\' >%s"' % (remasterscript.const.BINARY_BASH,
                                                                                                                                                                                                                                                                self._source + '/master',
                                                                                                                                                                                                                                                                self._source  + '/master/',
                                                                                                                                                                                                                                                                self._source + '/master/KNOPPIX/sha1sums'))
        self._processes['sha1'].connect('success', self._success, 'sha1')
        self._processes['sha1'].connect('error', self._error, 'sha1')
    
    def _image_iso(self):
        self._undo_paths.append('/tmp.iso')
        self._build.update('image_iso', 'Gestartet', 0.0)
        self._processes['image_iso'] = remasterscript.utils.MkIsoFs('-R -U -V "KNOPPIX.net filesystem" -publisher "KNOPPIX" -hide-rr-moved -cache-inodes -no-bak -pad -o',
                                                                        self._source + '/rootdir',
                                                                        self._source + '/tmp.iso')
        self._processes['image_iso'].connect('update', self._image_iso_update)
        self._processes['image_iso'].connect('success', self._image_iso_success)
        self._processes['image_iso'].connect('error', self._image_iso_error)
        
    
    def _image_iso_update(self, process, percentage):
        self._build.update('image_iso', str(percentage) + '%', float(percentage) / 100)
    
    def _image_iso_success(self, process):
        self._processes.pop('image_iso')
        self._build.update('image_iso', 'Fertig', 1.0)
        self._next()
    
    def _image_iso_error(self, process, errorcode):
        self._build.update('image_iso', 'Fehler', 0.0)
        self._undo(False)
    
    def _cd_iso(self):
        self._undo_paths.append('/remaster.iso')
        self._build.update('cd_iso', 'Gestartet', 0.0)
        self._processes['cd_iso'] = remasterscript.utils.MkIsoFs('-pad -l -r -J -v -V "KNOPPIX" -no-emul-boot -boot-load-size 4 -boot-info-table -b boot/isolinux/isolinux.bin -c boot/isolinux/boot.cat -hide-rr-moved -o',
                                                                        self._source + '/master',
                                                                        self._source + '/remaster.iso')
        self._processes['cd_iso'].connect('update', self._cd_iso_update)
        self._processes['cd_iso'].connect('success', self._cd_iso_success)
        self._processes['cd_iso'].connect('error', self._cd_iso_error)
        
    
    def _cd_iso_update(self, process, percentage):
        self._build.update('cd_iso', str(percentage) + '%', float(percentage) / 100)
    
    def _cd_iso_success(self, process):
        self._processes.pop('cd_iso')
        self._build.update('cd_iso', 'Fertig', 1.0)
        self._next()
    
    def _cd_iso_error(self, process, errorcode):
        self._build.update('cd_iso', 'Fehler', 0.0)
        self._undo(False)
    
    def _compress(self):
        self._undo_paths.append('/tmpcompress.iso')
        self._build.start('compress')
        self._processes['compress'] = remasterscript.utils.CreateCompressedFs(self._source + '/tmpcompress.iso',
                                                                                    self._source + '/tmp.iso',
                                                                                    self._source + '/master/KNOPPIX/KNOPPIX')
        self._processes['compress'].connect('update', self._compress_update)
        self._processes['compress'].connect('success', self._success, 'compress')
        self._processes['compress'].connect('error', self._error, 'compress')
        
    
    def _compress_update(self, process, time):
        self._build.set_text('compress', 'Noch %i Sekunden' % (time))
    
    def _test(self, build):
        if self._success_done:
                self._processes['prepare'] = remasterscript.utils.Util('"%s" -cdrom "%s" -m %i -no-reboot' % (remasterscript.const.BINARY_QEMU,
                                                                                                    self._source + '/remaster.iso',
                                                                                                    remasterscript.const.QEMU_MEM_SIZE))
    
    def _cancel(self, build):
        if self._success_done:
            self.emit('back')
            self._build.hide()
        else:
            self._undo(True)
    
    def _quit(self, *args):
        if self._success_done:
            self.emit('quit')
            self._build.hide()
        else:
            self._undo(True)

gobject.type_register(Controller)
gobject.signal_new('quit',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('back',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        ())
gobject.signal_new('success',
                        Controller,
                        gobject.SIGNAL_RUN_LAST,
                        gobject.TYPE_BOOLEAN,
                        (gobject.TYPE_STRING,))