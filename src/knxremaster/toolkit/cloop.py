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

from __future__ import division

import math
import os.path
import struct
import zlib

from knxremaster.toolkit.progress import progress

HEADER = struct.Struct('! 128s I I')
OFFSET = struct.Struct('! Q')   
PREAMBLE = ('#!/bin/sh\n#V2.0 Format\nmodprobe cloop file=$0 && mount -r -t iso9660 /dev/cloop $1\nexit $?').encode('ascii')

@progress
def extract_compressed_fs(progress, source, target):
    with open(source, 'rb') as source:
        num_blocks = HEADER.unpack(source.read(HEADER.size))[2]
        offsets = [OFFSET.unpack(source.read(OFFSET.size))[0] for i in range(num_blocks + 1)]
        progress.update(0)
        with open(target, 'wb') as target:
            for i, offset in enumerate(offsets[:-1]):
                if progress.condition('cancel'):
                    return
                progress.update((i + 1) / num_blocks * 100)
                target.write(zlib.decompress(source.read(offsets[i + 1] - offset)))

@progress
def create_compressed_fs(progress, source, target, block_size=65536, preamble=PREAMBLE, level=9):
    size = os.path.getsize(source)
    num_blocks = int(math.ceil(size / block_size))
    header = HEADER.pack(preamble, block_size, num_blocks)
    with open(target, 'wb') as target:
        target.write(header)
        current = len(header) + OFFSET.size * (num_blocks + 1)
        target.seek(current)
        offsets = [current]
        progress.update(0)
        with open(source, 'rb') as source:
            for i in range(1, num_blocks + 1):
                if progress.condition('cancel'):
                    return
                progress.update(i / num_blocks * 100)
                uncompressed = source.read(block_size)
                if len(uncompressed) < block_size:
                    uncompressed += '\x00' * (block_size - len(uncompressed))
                assert len(uncompressed) == block_size
                compressed = zlib.compress(uncompressed, level)
                target.write(compressed)
                current += len(compressed)
                offsets.append(current)
        target.seek(len(header))
        for offset in offsets:
            target.write(OFFSET.pack(offset))