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

from knxremaster.toolkit import commands, cloop
from knxremaster.toolkit.progress import script, progress

@script
def create(script, source, target, name='Unknown', filesystem=True, minirt=True, squashfs=False, base_compression='cloop', base_version='Unknown'):
    @progress
    def create_directories(progress):
        paths = ['']
        if filesystem:
            paths.append('knoppix-mount')
        if minirt:
            paths.append('minirt')
        for path in paths:
            path = os.path.join(target, path)
            if not os.path.exists(path):
                os.mkdir(path)
                    
    @progress
    def write_settings(progress):
        with open(os.path.join(target, 'master', 'KNOPPIX', 'remaster.info'), 'wb') as output:
            json.dump({'name': name, 'base': base_version, 'squashfs': False}, output)
                
    @progress
    def cleanup(progress):
        if os.path.exists(os.path.join(target, 'knoppix-mount')):
            os.rmdir(os.path.join(target, 'knoppix-mount'))
        if os.path.exists(os.path.join(target, 'knoppix.iso')):
            os.remove(os.path.join(target, 'knoppix.iso'))
    
    yield 'create_directories', create_directories()
    yield 'copy_master', commands.copy('-rp', source, os.path.join(target, 'master'))
    yield 'write_settings', write_settings()
    if filesystem:
        yield 'filesystem_decompress', cloop.extract_compressed_fs(os.path.join(target, 'master', 'KNOPPIX', 'KNOPPIX'), os.path.join(target, 'knoppix.iso'))
        yield 'filesystem_mount', commands.mount('-r', '-o', 'loop', os.path.join(target, 'knoppix.iso'), os.path.join(target, 'knoppix-mount'))
        yield 'filesystem_copy', commands.copy('-rp', os.path.join(target, 'knoppix-mount'), os.path.join(target, 'knoppix'))
        yield 'filesystem_umount', commands.umount(os.path.join(target, 'knoppix-mount'))
    if minirt:
        yield 'minirt_decompress', commands.gunzip(os.path.join(target, 'master', 'boot', 'isolinux', 'minirt.gz'))
        yield 'minirt_unpack', commands.cpio('-imd', '--no-absolute-filenames', stdin=open(os.path.join(target, 'master', 'boot', 'isolinux', 'minirt'), 'rb'), cwd=os.path.join(target, 'minirt'))
    yield 'cleanup', cleanup()

if __name__ == '__main__':
    import argparse
    import sys
    
    if os.getuid() != 0:
        sys.exit('This script requires root access!')
        
    _steps = {'create_directories': 'creating target directory structure...',
              'copy_master': 'copying cd/dvd...',
              'write_settings': 'writing settings...',
              'filesystem_extract': 'decompressing filesystem...',
              'filesystem_mount': 'mounting decompressed filesystem...',
              'filesystem_copy': 'copying filesystem...',
              'filesystem_umount': 'umounting decompressed filesystem',
              'minirt_extract': 'decompressing minirt...',
              'minirt_unpack': 'unpacking decompressed minirt...',
              'cleanup': 'cleaning up...'}
    
    def main_create(arguments):
        _create = create(arguments.source, arguments.target, arguments.name, arguments.nofilesystem, arguments.nominirt, arguments.squashfs)
        _create(_steps)
         
    parser = argparse.ArgumentParser()
    parser.add_argument('source', help='mounted knoppix cd/dvd')
    parser.add_argument('target', help='target path for unpacking knoppix')
    parser.add_argument('--name', default='Unknown', help='name of the remaster')
    parser.add_argument('--nofilesystem', action='store_false', help='do not extract filesystem')
    parser.add_argument('--nominirt', action='store_false', help='do not extract minirt')
    parser.add_argument('--squashfs', action='store_true', help='patch knoppix to use squashfs')
    main_create(parser.parse_args())