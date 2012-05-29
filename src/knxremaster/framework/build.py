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

import io
import os
import os.path
import subprocess

from knxremaster.framework import utils, cloop
from knxremaster.framework.chain import Chain

class Build(Chain):
    def __init__(self, source):
        Chain.__init__(self)
        self.source = source
        self.chain = [self.prepare]
        if os.path.exists(os.path.join(self.source, 'knoppix')):
            self.chain.extend([self.filesystem_image, self.filesystem_compress])
            self.filesystem = True
        else:
            self.filesystem = False
        if os.path.exists(os.path.join(self.source, 'minirt')):
            self.chain.extend([self.minirt_files, self.minirt_image, self.minirt_compress])
            self.minirt = True
        else:
            self.minirt = False
        self.chain.extend([self.iso, self.clean])
        
    def prepare(self):
        self.emit('started', 'prepare')
        remaster = os.path.join(self.source, 'remaster.iso')
        if os.path.exists(remaster):
            os.remove(remaster)
        knoppix = os.path.join(self.source, 'master', 'KNOPPIX', 'KNOPPIX')
        if os.path.exists(knoppix) and self.filesystem:
            os.remove(knoppix)
        minirt = os.path.join(self.source, 'master', 'boot', 'isolinux', 'minirt.gz')
        if os.path.exists(minirt) and self.minirt:
            os.remove(minirt)
        minirt = os.path.join(self.source, 'master', 'boot', 'isolinux', 'minirt')
        if os.path.exists(minirt) and self.minirt:
            os.remove(minirt)
        self.emit('finished')
        
    def filesystem_image(self):
        mkisofs = utils.mkisofs('-R', '-U', '-V', 'KNOPPIX.net filesystem', '-publisher', 'KNOPPIX', '-hide-rr-moved', '-cache-inodes', '-no-bak', '-pad', '-o', os.path.join(self.source, 'knoppix.iso'), os.path.join(self.source, 'knoppix'))
        self.connect(mkisofs, 'filesystem_image')
        mkisofs.start()
    
    def filesystem_compress(self):
        compress = cloop.create_compressed_fs(os.path.join(self.source, 'knoppix.iso'), os.path.join(self.source, 'master', 'KNOPPIX', 'KNOPPIX'))
        self.connect(compress, 'filesystem_compress')
        compress.start()
    
    def minirt_files(self):
        self.emit('started', 'minirt_files')
        minirt_files = []
        minirt = os.path.join(self.source, 'minirt')
        for root, dirnames, filenames in os.walk(minirt):
            root = root.replace(minirt, '.')
            minirt_files.append(root)
            for file in filenames:
                minirt_files.append(os.path.join(root, file))
        self._minirt_files = '\n'.join(minirt_files)
        self.emit('finished')
    
    def minirt_image(self):
        self.emit('started', 'minirt_image')
        cpio = utils.cpio('-oH' 'newc', stdin=subprocess.PIPE, stdout=open(os.path.join(self.source, 'master', 'boot', 'isolinux', 'minirt'), 'wb'), cwd=os.path.join(self.source, 'minirt'))
        cpio.start()
        cpio.checkpoint.wait()
        cpio.process.stdin.write(self._minirt_files)
        cpio.process.stdin.close()
        cpio.finished.wait()
        self.emit('finished')

    def minirt_compress(self):
        gzip = utils.gzip(os.path.join(self.source, 'master', 'boot', 'isolinux', 'minirt'))
        self.connect(gzip, 'minirt_compress')
        gzip.start()
        
    def iso(self):
        mkisofs = utils.mkisofs('-pad', '-l', '-r', '-J', '-v', '-V', 'KNOPPIX', '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table', '-b', 'boot/isolinux/isolinux.bin', '-c', 'boot/isolinux/boot.cat', '-hide-rr-moved', '-o', os.path.join(self.source, 'remaster.iso'), os.path.join(self.source, 'master'))
        self.connect(mkisofs, 'iso')
        mkisofs()
        
    def clean(self):
        self.emit('started', 'clean')
        if self.filesystem:
            os.remove(os.path.join(self.source, 'knoppix.iso'))
        self.emit('finished')