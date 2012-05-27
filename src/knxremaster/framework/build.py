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

class Build():
    def __init__(self, source):
        self.source = source
    
    def prepare(self):
        knoppix = os.path.join(self.source, 'master', 'KNOPPIX', 'KNOPPIX')
        if os.path.exists(knoppix):
            os.remove(knoppix)
        remaster = os.path.join(self.source, 'remaster.iso')
        if os.path.exists(remaster):
            os.remove(remaster)
    
    def image(self):
        mkisofs = utils.mkisofs('-R', '-U', '-V', 'KNOPPIX.net filesystem', '-publisher', 'KNOPPIX', '-hide-rr-moved', '-cache-inodes', '-no-bak', '-pad', '-o', os.path.join(self.source, 'knoppix.iso'), os.path.join(self.source, 'knoppix'))
        mkisofs.handler['update'].append(self.update)
        mkisofs()
    
    def compress(self):
        compress = cloop.create_compressed_fs(os.path.join(self.source, 'knoppix.iso'), os.path.join(self.source, 'master', 'KNOPPIX', 'KNOPPIX'))
        compress.handler['update'].append(self.update)
        compress()
    
    def iso(self):
        mkisofs = utils.mkisofs('-pad', '-l', '-r', '-J', '-v', '-V', 'KNOPPIX', '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table', '-b', 'boot/isolinux/isolinux.bin', '-c', 'boot/isolinux/boot.cat', '-hide-rr-moved', '-o', os.path.join(self.source, 'remaster.iso'), os.path.join(self.source, 'master'))
        mkisofs.handler['update'].append(self.update)
        mkisofs()
        
    def clean(self):
        os.remove(os.path.join(self.source, 'knoppix.iso'))
    
    def update(self, percentage, message):
        print('\r{}%               '.format(percentage), end='')    

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print('usage: {} <source>'.format(sys.argv[0]))
    else:
        build = Build(sys.argv[1])
        print('PREPARE')
        build.prepare()
        print('IMAGE')
        build.image()
        print('\nCOMPRESS')
        build.compress()
        print('\nISO')
        build.iso()
        print('\nCLEAN')
        build.clean()
