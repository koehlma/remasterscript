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

import os.path
import shutil

from knxremaster.toolkit import commands
from knxremaster.toolkit.progress import script, progress

@script
def unpack(script, source, target):
    @progress
    def cleanup(progress):
        if os.path.exists(os.path.join(target, '[BOOT]')):
            shutil.rmtree(os.path.join(target, '[BOOT]'))
            
    yield 'unpack', commands.zip7('x', '-o%s' % (target), source)
    yield 'cleanup', cleanup()

@script
def pack(script, source, target):
    yield 'pack', commands.mkisofs('-pad', '-l', '-r', '-J', '-v', '-V', 'KNOPPIX', '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table', '-b', 'boot/isolinux/isolinux.bin', '-c', 'boot/isolinux/boot.cat', '-hide-rr-moved', '-o', target, source)

if __name__ == '__main__':
    import argparse
    
    _steps = {'unpack': 'unpacking iso image...',
              'cleanup': 'cleaning up...',
              'pack': 'packing iso image...'}
    
    def main_unpack(arguments):
        _unpack = unpack(arguments.source, arguments.target)
        _unpack(_steps)
    
    def main_pack(arguments):
        _pack = pack(arguments.source, arguments.target)
        _pack(_steps)
        
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='packaging')
    parser_unpack = subparsers.add_parser('unpack', help='pack an iso image')
    parser_unpack.add_argument('source', help='knoppix iso image to unpack')
    parser_unpack.add_argument('target', help='target directory for unpacked knoppix')
    parser_unpack.set_defaults(func=main_unpack)
    parser_pack = subparsers.add_parser('pack', help='pack an iso image')
    parser_pack.add_argument('source', help='directory of unpacked knoppix')
    parser_pack.add_argument('target', help='target iso image to create')
    parser_pack.set_defaults(func=main_pack)
    arguments = parser.parse_args()
    arguments.func(arguments)