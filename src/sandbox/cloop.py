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

from __future__ import print_function, division

import math
import os.path
import struct
import zlib

HEADER = struct.Struct('! 128s I I')
OFFSET = struct.Struct('! Q')   
PREAMBLE = ('#!/bin/sh\n'
            '#V2.0 Format\n'
            'modprobe cloop file=$0 && mount -r -t iso9660 /dev/cloop $1\n'
            'exit $?').encode('ascii')

def extract_compressed_fs(input, output):
    with open(input, 'rb') as input:
        preamble, block_size, num_blocks = HEADER.unpack(input.read(HEADER.size))
        offsets = [OFFSET.unpack(input.read(OFFSET.size))[0] for i in range(num_blocks + 1)]
        with open(output, 'wb') as output:
            for i, offset in enumerate(offsets[:-1]):
                output.write(zlib.decompress(input.read(offsets[i + 1] - offset)))

def create_compressed_fs(input, output, block_size=65536, preamble=PREAMBLE, level=9):
    size = os.path.getsize(input)
    num_blocks = int(math.ceil(size / block_size))
    header = HEADER.pack(preamble, block_size, num_blocks)
    with open(output, 'wb') as output:
        output.write(header)
        current = len(header) + OFFSET.size * (num_blocks + 1)
        output.seek(current)
        offsets = [current]
        with open(input, 'rb') as input:
            for i in range(num_blocks):
                uncompressed = input.read(block_size)
                if len(uncompressed) < block_size:
                    uncompressed += '\x00' * (block_size - len(uncompressed))
                assert len(uncompressed) == block_size
                compressed = zlib.compress(uncompressed, level)
                output.write(compressed)
                current += len(compressed)
                offsets.append(current)
        output.seek(len(header))
        for offset in offsets:
            output.write(OFFSET.pack(offset))