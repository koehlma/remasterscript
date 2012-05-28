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
import json
import os
import os.path
import threading

from knxremaster.framework import utils, cloop

class Create():
    def __init__(self, source, target, name, filesystem=True, minirt=True, squashfs=False, base_compression='cloop', base_version='Unknown'):
        self.source = source
        self.target = target
        self.name = name
        self.filesystem = filesystem
        self.minirt = minirt
        self.squashfs = squashfs
        self.base_compression = base_compression
        self.base_version = base_version
        self.handler = {'success': [], 'error': [], 'started': [], 'finished': [self._next], 'update': []}
        self.current = [self.mkdir, self.copy, self.settings]
        if self.filesystem:
            self.current.extend([self.filesystem_extract, self.filesystem_mount, self.filesystem_knoppix, self.filesystem_umount])
        if self.minirt:
            self.current.extend([self.minirt_extract, self.minirt_unpack])
        if self.squashfs:
            self.current.extend([self.squashfs_patch])
        self.current.append(self.clean)
        
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
        if self.minirt:
            os.mkdir(os.path.join(self.target, 'minirt'))
        self._handle('finished')
                
    def copy(self):
        copy = utils.copy('-rp', self.source, os.path.join(self.target, 'master'))
        self._connect(copy, 'copy')
        copy.start()
    
    def settings(self):
        self._handle('started', 'settings')
        with open(os.path.join(self.target, 'master', 'KNOPPIX', 'remaster.info'), 'wb') as output:
            info = {'name': self.name,
                    'base': self.base_version,
                    'squashfs': False} #self.squashfs}
            json.dump(info, output)
        self._handle('finished')
    
    def filesystem_extract(self):
        extract = cloop.extract_compressed_fs(os.path.join(self.target, 'master', 'KNOPPIX', 'KNOPPIX'), os.path.join(self.target, 'knoppix.iso'))
        self._connect(extract, 'filesystem_extract')
        extract.start()
    
    def filesystem_mount(self):
        mount = utils.mount('-r', '-o', 'loop', os.path.join(self.target, 'knoppix.iso'), os.path.join(self.target, 'knoppix-mount'))
        self._connect(mount, 'filesystem_mount')
        mount.start()
        
    def filesystem_knoppix(self):
        copy = utils.copy('-rp', os.path.join(self.target, 'knoppix-mount'), os.path.join(self.target, 'knoppix'))
        self._connect(copy, 'filesystem_knoppix')
        copy.start()
    
    def filesystem_umount(self):
        umount = utils.umount(os.path.join(self.target, 'knoppix-mount'))
        self._connect(umount, 'filesystem_umount')
        umount.start()
    
    def minirt_extract(self):
        gunzip = utils.gunzip(os.path.join(self.target, 'master', 'boot', 'isolinux', 'minirt.gz'))
        self._connect(gunzip, 'minirt_extract')
        gunzip.start()
    
    def minirt_unpack(self):
        cpio = utils.cpio('-imd', '--no-absolute-filenames', stdin=open(os.path.join(self.target, 'master', 'boot', 'isolinux', 'minirt'), 'rb'), cwd=os.path.join(self.target, 'minirt'))
        self._connect(cpio, 'minirt_unpack')
        cpio.start()
    
    def squashfs_patch(self):
        self._handle('started', 'squashfs_patch')
        print('squashfs is not supported yet')
        self._handle('finished')
    
    def clean(self):
        self._handle('started', 'clean')
        if os.path.exists(os.path.join(self.target, 'knoppix-mount')):
            os.rmdir(os.path.join(self.target, 'knoppix-mount'))
        if os.path.exists(os.path.join(self.target, 'knoppix.iso')):
            os.remove(os.path.join(self.target, 'knoppix.iso'))
        self._handle('finished')