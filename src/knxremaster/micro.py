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
            
    yield 'unpack', commands.zip7g('x', '-o%s' % (target), source)
    yield 'cleanup', cleanup()

@script
def pack(script, source, target):
    yield 'pack', commands.mkisofs('-pad', '-l', '-r', '-J', '-v', '-V', 'KNOPPIX', '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table', '-b', 'boot/isolinux/isolinux.bin', '-c', 'boot/isolinux/boot.cat', '-hide-rr-moved', '-o', target, source)