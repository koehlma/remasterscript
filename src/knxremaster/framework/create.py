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

import json
import os
import os.path

from knxremaster.framework import utils, cloop
from knxremaster.framework.chain import Chain

class Create(Chain):
    def __init__(self, source, target, name, filesystem=True, minirt=True, squashfs=False, base_compression='cloop', base_version='Unknown'):
        Chain.__init__(self)
        self.source = source
        self.target = target
        self.name = name
        self.filesystem = filesystem
        self.minirt = minirt
        self.squashfs = squashfs
        self.base_compression = base_compression
        self.base_version = base_version
        self.chain = [self.mkdir, self.copy, self.settings]
        if self.filesystem:
            self.chain.extend([self.filesystem_extract, self.filesystem_mount, self.filesystem_knoppix, self.filesystem_umount])
        if self.minirt:
            self.chain.extend([self.minirt_extract, self.minirt_unpack])
        if self.squashfs:
            self.chain.extend([self.squashfs_patch])
        self.chain.append(self.clean)
    
    def mkdir(self):
        self.emit('started', 'mkdir')
        for path in ['', 'knoppix-mount']:
            path = os.path.join(self.target, path)
            if not os.path.exists(path):
                os.mkdir(path)
        if self.minirt:
            os.mkdir(os.path.join(self.target, 'minirt'))
        self.emit('finished')
                
    def copy(self):
        copy = utils.copy('-rp', self.source, os.path.join(self.target, 'master'))
        self.connect(copy, 'copy')
        copy.start()
    
    def settings(self):
        self.emit('started', 'settings')
        with open(os.path.join(self.target, 'master', 'KNOPPIX', 'remaster.info'), 'wb') as output:
            info = {'name': self.name,
                    'base': self.base_version,
                    'squashfs': False} #self.squashfs}
            json.dump(info, output)
        self.emit('finished')
    
    def filesystem_extract(self):
        extract = cloop.extract_compressed_fs(os.path.join(self.target, 'master', 'KNOPPIX', 'KNOPPIX'), os.path.join(self.target, 'knoppix.iso'))
        self.connect(extract, 'filesystem_extract')
        extract.start()
    
    def filesystem_mount(self):
        mount = utils.mount('-r', '-o', 'loop', os.path.join(self.target, 'knoppix.iso'), os.path.join(self.target, 'knoppix-mount'))
        self.connect(mount, 'filesystem_mount')
        mount.start()
        
    def filesystem_knoppix(self):
        copy = utils.copy('-rp', os.path.join(self.target, 'knoppix-mount'), os.path.join(self.target, 'knoppix'))
        self.connect(copy, 'filesystem_knoppix')
        copy.start()
    
    def filesystem_umount(self):
        umount = utils.umount(os.path.join(self.target, 'knoppix-mount'))
        self.connect(umount, 'filesystem_umount')
        umount.start()
    
    def minirt_extract(self):
        gunzip = utils.gunzip(os.path.join(self.target, 'master', 'boot', 'isolinux', 'minirt.gz'))
        self.connect(gunzip, 'minirt_extract')
        gunzip.start()
    
    def minirt_unpack(self):
        cpio = utils.cpio('-imd', '--no-absolute-filenames', stdin=open(os.path.join(self.target, 'master', 'boot', 'isolinux', 'minirt'), 'rb'), cwd=os.path.join(self.target, 'minirt'))
        self.connect(cpio, 'minirt_unpack')
        cpio.start()
    
    def squashfs_patch(self):
        self.emit('started', 'squashfs_patch')
        print('squashfs is not supported yet')
        self.emit('finished')
    
    def clean(self):
        self.emit('started', 'clean')
        if os.path.exists(os.path.join(self.target, 'knoppix-mount')):
            os.rmdir(os.path.join(self.target, 'knoppix-mount'))
        if os.path.exists(os.path.join(self.target, 'knoppix.iso')):
            os.remove(os.path.join(self.target, 'knoppix.iso'))
        self.emit('finished')