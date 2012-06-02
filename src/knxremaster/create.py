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
        yield 'filesystem_extract', cloop.extract_compressed_fs(os.path.join(target, 'master', 'KNOPPIX', 'KNOPPIX'), os.path.join(target, 'knoppix.iso'))
        yield 'filesystem_mount', commands.mount('-r', '-o', 'loop', os.path.join(target, 'knoppix.iso'), os.path.join(target, 'knoppix-mount'))
        yield 'filesystem_copy', commands.copy('-rp', os.path.join(target, 'knoppix-mount'), os.path.join(target, 'knoppix'))
        yield 'filesystem_umount', commands.umount(os.path.join(target, 'knoppix-mount'))
    if minirt:
        yield 'minirt_extract', commands.gunzip(os.path.join(target, 'master', 'boot', 'isolinux', 'minirt.gz'))
        yield 'minirt_unpack', commands.cpio('-imd', '--no-absolute-filenames', stdin=open(os.path.join(target, 'master', 'boot', 'isolinux', 'minirt'), 'rb'), cwd=os.path.join(target, 'minirt'))
    yield 'cleanup', cleanup()