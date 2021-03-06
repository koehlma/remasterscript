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

import functools
import os
import re
import subprocess

from knxremaster.toolkit.progress import progress, command

_MKISOFS_PERCENTAGE = re.compile(r'([0-9]*\.[0-9]*)%\s*done')

if os.name == 'posix':
    mount = functools.partial(command, 'mount')
    
    umount = functools.partial(command, 'umount')
    
    copy = functools.partial(command, 'cp')
    
    remove = functools.partial(command, 'rm')
    
    gunzip = functools.partial(command, 'gunzip')
    
    cpio = functools.partial(command, 'cpio')
    
    gzip = functools.partial(command, 'gzip')
    
    zip7 = functools.partial(command, '7z')
    
    zip7g = functools.partial(command, '7zG')
    
    _mkisofs = 'mkisofs'    
elif os.name == 'nt':
    zip7 = functools.partial(command, os.path.join(os.path.dirname(__file__), '7zip', '7z.exe'))
    
    zip7g = functools.partial(command, os.path.join(os.path.dirname(__file__), '7zip', '7zG.exe'))
    
    _mkisofs = os.path.join(os.path.dirname(__file__), 'mkisofs', 'mkisofs.exe')
    
@progress
def mkisofs(progress, *arguments):
    process = subprocess.Popen([_mkisofs] + list(arguments), stderr=subprocess.PIPE)
    while process.poll() is None:
        if progress.condition('cancel'):
            process.kill()
            return
        else:
            line = process.stderr.readline()
            match = _MKISOFS_PERCENTAGE.search(line)
            if match:
                progress.update(float(match.group(1)))
    progress.update(100)
    if process.returncode != 0:
        progress.condition('error').activate()