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

import os
import os.path

from knxremaster.framework import utils, cloop

class Create():
    def __init__(self, source, target):
        self.source = source
        self.target = target

    def mkdir(self):
        for path in ['', 'knoppix-mount']:
            path = os.path.join(self.target, path)
            if not os.path.exists(path):
                os.mkdir(path)
                
    def copy(self):
        copy = utils.copy('-rp', self.source, os.path.join(self.target, 'master'))
        copy.handler['update'].append(self.update)
        copy()
        
    def extract(self):
        source = os.path.join(self.target, 'master', 'KNOPPIX', 'KNOPPIX')
        target = os.path.join(self.target, 'knoppix.iso')
        extract = cloop.extract_compressed_fs(source, target)
        extract.handler['update'].append(self.update)
        extract()
    
    def mount(self):
        source = os.path.join(self.target, 'knoppix.iso')
        target = os.path.join(self.target, 'knoppix-mount')
        mount = utils.mount('-r', source, target)
        mount.handler['update'].append(self.update)
        mount()
    
    def knoppix(self):
        source = os.path.join(self.target, 'knoppix-mount')
        target = os.path.join(self.target, 'knoppix')
        copy = utils.copy('-rp', source, target)
        copy.handler['update'].append(self.update)
        copy()
    
    def umount(self):
        umount = utils.umount(os.path.join(self.target, 'knoppix-mount'))
        umount.handler['update'].append(self.update)
        umount()
    
    def clean(self):
        os.rmdir(os.path.join(self.target, 'knoppix-mount'))
        os.remove(os.path.join(self.target, 'knoppix.iso'))
    
    def update(self, percentage, message):
        print('\r{}%               '.format(percentage), end='')    

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print('usage: {} <source> <target>'.format(sys.argv[0]))
    else:
        create = Create(sys.argv[1], sys.argv[2])
        print('MKDIR')
        create.mkdir()
        print('COPY')
        create.copy()
        print('EXTRACT')
        create.extract()
        print('\nMOUNT')
        create.mount()
        print('KNOPPIX')
        create.knoppix()
        print('UMOUNT')
        create.umount()
        print('CLEAN')
        create.clean()
