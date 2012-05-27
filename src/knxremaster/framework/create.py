# -*- coding:utf-8 -*-
#
# Copyright (C) 2012, Maximilian Köhl <linuxmaxi@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

import functools
import os
import os.path
import threading

from knxremaster.framework import utils, cloop

class Create():
    def __init__(self, source, target):
        self.source = source
        self.target = target
        self.handler = {'success': [], 'error': [], 'started': [], 'finished': [self._next], 'update': []}
        self.current = [self.mkdir, self.copy, self.extract, self.mount, self.knoppix, self.umount, self.clean]
        
    def _handle(self, type, *args, **kwargs):
        for handler in self.handler[type]:
            handler(*args, **kwargs)  
    
    def _connect(self, progress, name):
        progress.handler['update'].append(functools.partial(self._handle, 'update'))
        progress.handler['started'].append(functools.partial(self._handle, 'started', name))
        progress.handler['finished'].append(functools.partial(self._handle, 'finished'))
        progress.handler['error'].append(lambda *args, **kwargs: print('error!!!'))
    
    def _next(self):
        if len(self.current):
            threading.Thread(target=self.current.pop(0)).start()
        else:
            self._handle('success')
    
    def run(self):
        self._next()
    
    def mkdir(self):
        self._handle('started', 'mkdir')
        for path in ['', 'knoppix-mount']:
            path = os.path.join(self.target, path)
            if not os.path.exists(path):
                os.mkdir(path)
        self._handle('finished')
                
    def copy(self):
        copy = utils.copy('-rp', self.source, os.path.join(self.target, 'master'))
        self._connect(copy, 'copy')
        copy.start()
        
    def extract(self):
        extract = cloop.extract_compressed_fs(os.path.join(self.target, 'master', 'KNOPPIX', 'KNOPPIX'), os.path.join(self.target, 'knoppix.iso'))
        self._connect(extract, 'extract')
        extract.start()
    
    def mount(self):
        mount = utils.mount('-r', '-o', 'loop', os.path.join(self.target, 'knoppix.iso'), os.path.join(self.target, 'knoppix-mount'))
        self._connect(mount, 'mount')
        mount.start()
        
    def knoppix(self):
        copy = utils.copy('-rp', os.path.join(self.target, 'knoppix-mount'), os.path.join(self.target, 'knoppix'))
        self._connect(copy, 'knoppix')
        copy.start()
    
    def umount(self):
        umount = utils.umount(os.path.join(self.target, 'knoppix-mount'))
        self._connect(umount, 'umount')
        umount.start()
    
    def clean(self):
        self._handle('started', 'clean')
        os.rmdir(os.path.join(self.target, 'knoppix-mount'))
        os.remove(os.path.join(self.target, 'knoppix.iso'))
        self._handle('finished')